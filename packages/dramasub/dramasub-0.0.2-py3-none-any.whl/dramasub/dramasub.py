#!/usr/bin/env python3

import os
import sys
from wand.drawing import Drawing
from wand.image import Image
import re
import subprocess
import argparse
from pathlib import Path
import importlib.util
import shutil
import copy


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input video file (the one with the audio)", required=True)
    parser.add_argument("-o", "--output", help="path to video that will be output")
    parser.add_argument("-c", "--config", help="path to config (.py) file", required=True)
    parser.add_argument("-a", "--ass", help="path to .ass subtitle file", required=True)
    parser.add_argument("--cook_only", help="only cooks assets from config (for testing)", action="store_true")

    return parser.parse_args()

def get_res(video):
    res_probe = subprocess.run(['ffprobe','-v','error','-select_streams',
                                'v:0','-show_entries','stream=height,width',
                                '-of','flat',video],stdout=subprocess.PIPE).stdout.decode('utf-8')
    (probe_w,probe_h) = res_probe.splitlines()
    res_w = int(probe_w.split("=")[1])
    res_h = int(probe_h.split("=")[1])
    return (res_w,res_h)

def draw_text(img,text,font,fill,pointsize,kerning,align,posx,posy):
    with Drawing() as draw:
        draw.font = font
        draw.fill_color = fill
        draw.font_size = pointsize
        if kerning:
            draw.text_kerning = kerning
        if align:
            draw.text_alignment = align
        draw.text(posx, posy, text)
        draw.draw(img)


def parse_font(font_name):
    try:
        font_dict = config.config["font"][font_name]    # not a copy, but the actual dict in the config, so don't modify it
    except:
        print('Error: "' + font_name + '" not found in config!')
        sys.exit(1)
    try:
        font = font_dict["font"]
    except:
        print("Error: " + font_name + " is missing font!")
        sys.exit(1)
    try:
        fill = font_dict["fill"]
    except:
        print("Error: " + font_name + " is missing fill!")
        sys.exit(1)
    try:
        pointsize = int(font_dict["pointsize"])
    except:
        print("Error: " + font_name + " has invalid pointsize!")
        sys.exit(1)
    if "kerning" in font_dict:
        try:
            kerning = float(font_dict["kerning"])
        except:
            print("Error: " + font_name + "has invalid kerning value!")
            sys.exit(1)
    else:
        kerning = None
    if "alignment" in font_dict:
        if font_dict["alignment"] in ("left", "center", "right"):
            align = font_dict["alignment"]
        else:
            print("Error: " + font_name + " has invalid title alignment!")
            sys.exit(1)
    else:
        align = None
    try:
        posx = int(font_dict["position_x"])
        posy = int(font_dict["position_y"])
    except:
        print("Error: " + font_name + " has invalid position!")
        sys.exit(1)
    return [font,fill,pointsize,kerning,align,posx,posy]


def layer_img2img(top_img, base_img, output_path):
    with Image(filename=base_img) as base:
        with Image(filename=top_img) as top:
            base.composite(top)
        base.save(filename=output_path)


def layer_txt2img(text, base_img, font_name, output_path):
    [font,fill,pointsize,kerning,align,posx,posy] = parse_font(font_name)
    with Image(filename=base_img) as img:
        draw_text(img,text,font,fill,pointsize,kerning,align,posx,posy)
        img.save(filename=output_path)


def layer_txt2blank(text, font_name, res_w, res_h, output_path):
    [font,fill,pointsize,kerning,align,posx,posy] = parse_font(font_name)
    with Image(width=res_w, height=res_h) as img:
        draw_text(img,text,font,fill,pointsize,kerning,align,posx,posy)
        img.save(filename=output_path)


def cook(actor_dict,act_eff_str,stack,res_w,res_h):
    cooked_list = []
    cook_count = 0  # number of different cooked images for the current act_eff_str, for if "ff" is used
    cook_fn = act_eff_str + "_"
    stack_len = len(stack)
    cook_on_stack = False   # whether cooking on an existing stack of layers
    last_eff = ""
    has_cooked = False

    if stack_len > 0:
        for i in stack:
            if i in actor_dict:
                curr_layer = actor_dict[i]
                if curr_layer and curr_layer["value"]:  # pass if either are None
                    curr_output = kitchen_path / (cook_fn + str(cook_count) + ".png")
                    curr_type = curr_layer["type"]
                    if cook_on_stack:
                        if curr_type == "img":
                            layer_img2img(curr_layer["value"], curr_output, curr_output)
                            last_eff = "img"
                            has_cooked = True
                        elif curr_type == "txt":
                            layer_txt2img(curr_layer["value"], curr_output, curr_layer["font"], \
                                            curr_output)
                            last_eff = "txt"
                            has_cooked = True
                        elif curr_type == "ff":
                            if last_eff != "ff":
                                cooked_list.append(curr_output)
                                cook_count += 1
                            cooked_list.append(curr_layer["value"])
                            last_eff = "ff"
                            cook_on_stack = False
                        else:
                            print('Error: "' + curr_layer + '" of "' + act_eff_str + 'does not have value \
                                "img", "txt", or "ff"!')
                            sys.exit(1)
                    else:
                        if curr_type == "img" and stack_len == 1:
                            cooked_list.append(curr_layer["value"])
                            last_eff = "img"
                        elif curr_type == "img":    # probably shouldn't do this but lazy
                            shutil.copyfile(curr_layer["value"], curr_output)
                            last_eff = "img"
                            has_cooked = True
                        elif curr_type == "ff":
                            cooked_list.append(curr_layer["ff"])
                            last_eff = "ff"
                        elif curr_type == "txt":
                            layer_txt2blank(curr_layer["value"], curr_layer["font"], res_w, res_h, curr_output)
                            last_eff = "txt"
                            has_cooked = True
                    if last_eff != "ff":
                        cook_on_stack = True
        if has_cooked and last_eff != "ff":
            cooked_list.append(curr_output)
    else:
        print('Error: "stack" has a length of 0!')
        sys.exit(1)

    return cooked_list
    

def gen_act_dict(matched_actor,matched_effect,actor_effect_str,line_count):
    def merge_dicts(output_dict, merging_dict):
        for key in merging_dict:
            if key in output_dict:
                if isinstance(output_dict[key], dict) and isinstance(merging_dict[key], dict):
                    for subkey in merging_dict[key]:
                        output_dict[key][subkey] = merging_dict[key][subkey]
                else:
                    output_dict[key] = merging_dict[key]
            else:
                output_dict[key] = merging_dict[key]
        return output_dict

    if actor_effect_str not in cooked_actors:
        actor_dict = copy.deepcopy(config.config["actor"]["%Default"])
        if matched_actor != "%Default":
            if matched_actor in config.config["actor"]:
                m_a_dict = copy.deepcopy(config.config["actor"][matched_actor])
            else:
                m_a_dict = copy.deepcopy(config.config["actor"]["%Name"])
                for key in m_a_dict:
                    m_a_dict[key]["value"] = matched_actor
            actor_dict = merge_dicts(actor_dict, m_a_dict)

        if matched_effect != "":
            if matched_effect in config.config["effect"]:
                m_e_dict = copy.deepcopy(config.config["effect"][matched_effect])
                actor_dict = merge_dicts(actor_dict, m_e_dict)
            else:
                print("Error: effect " + matched_effect + " on line " + str(line_count) + \
                    " not found! Terminating...")
                sys.exit(1)
        
        for key in actor_dict:
            if isinstance(actor_dict[key], str):
                try:
                    actor_dict[key] = config.config[key][actor_dict[key]]
                except:
                    print('Error: issue finding "' + actor_dict[key] + \
                          '" in ' + key + 'or "' + key + '" itself for' + \
                            actor_effect_str + "in config!")
                    sys.exit(1)
            elif actor_dict[key] and not isinstance(actor_dict[key], dict):
                print("Error: " + key + '" for "' + actor_effect_str + "is not a str, dict, or None!")
                sys.exit(1)
    else:
        actor_dict = None
    return actor_dict


def iterate_ass(ass_line,line_count,regex,illegal_map):
    if ass_line.startswith("Dialogue:"):
        line_count += 1

        matches = re.search(regex, ass_line)
        matched_start = matches.group(1)
        matched_end = matches.group(2)
        matched_actor = matches.group(3)
        matched_effect = matches.group(4)
        matched_dialog = False
        if matches.group(5) != "":
            matched_dialog = True

        if matched_dialog == True or matched_actor != "" or matched_effect != "":   # skip blank lines
            if matched_actor == "":
                matched_actor = "%Default"
            if matched_effect != "":
                actor_effect_str = matched_actor + "_" + matched_effect
            else:
                actor_effect_str = matched_actor
            actor_effect_str = actor_effect_str.translate(illegal_map)  # swap out illegal chars

            return (matched_actor,matched_effect,actor_effect_str,line_count,matched_start,matched_end)
    return None


def sex_to_sec(sex):
    h,m,sms = sex.split(':')
    return int(h)*3600 + int(m)*60 + float(sms)


def gen_actor_input(act_eff, num_counter):
    act_stitch_list = []
    act_eff_inp_num = []    # act_eff_str input number list
    for layer in cooked_actors[act_eff]:
        act_stitch_list.append("-i")
        act_stitch_list.append(layer)
        act_eff_inp_num.append(num_counter)
        num_counter += 1
    return [act_stitch_list, act_eff_inp_num, num_counter]


def stitch(filter_string, stitch_count, act_eff_str, act_eff_to_num,
           start_time, end_time):
    if act_eff_str in act_eff_to_num:
        for layer_inp_num in act_eff_to_num[act_eff_str]:
            if stitch_count > 0:    # if not first overlay
                curr_var = "[v" + str(stitch_count) + "]"
                filter_string += curr_var + ";" + curr_var
            stitch_count += 1
            filter_string += "[" + str(layer_inp_num) \
                + r":v]overlay=0:0:enable='between(t," + str(start_time) \
                + "," + str(end_time) + ")'"

    return(filter_string, stitch_count)


def main():
    # argparse
    parsed_args = parse_arguments()
    config_path = Path(parsed_args.config)
    if not os.path.isfile(config_path):
        print("Error: specified config does not exist!")
        sys.exit(1)
    input_ass = parsed_args.ass
    if "\\" not in input_ass and "/" not in input_ass:
        if not os.path.isfile(input_ass):
            print("Error: specified subtitle file does not exist!")
            sys.exit(1)
        else:
            ass_name = input_ass
    else:
        print("Error: .ass not in working directory (ffmpeg limitations)")
        sys.exit(1)
    input_path = Path(parsed_args.input)
    if not os.path.isfile(input_path):
        print("Error: specified input video does not exist!")
        sys.exit(1)
    if parsed_args.cook_only:
        will_only_cook = True
    else:
        will_only_cook = False
        if parsed_args.output:
            output_path = parsed_args.output
        else:
            print("Error: output file not specified!")
            sys.exit(1)


    # import .py as config file
    global config
    config_name = "config"
    spec = importlib.util.spec_from_file_location(config_name, config_path)
    config = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(config)
    except Exception as e:
        print("Error: Invalid syntax in config file (probably)! Did you forget a comma?")
        print(e)
        sys.exit(1)


    with open(ass_name,"r", encoding="utf-8") as ass:  # read aegisub file
        lines = ass.readlines()

    
    global kitchen_path
    try:
        kitchen_path = Path(config.kitchen)   #temp file directory for cooked images
        kitchen_path.mkdir(parents=True, exist_ok=True)
    except:
        print('Error: "kitchen_path" (temp directory) not set in config!')
        sys.exit(1)

    try:
        stack = config.stack
        stack.reverse()
    except:
        print('Error: "stack" not properly set in config!')
        sys.exit(1)

    global cooked_actors
    cooked_actors = {}

    (vid_w, vid_h) = get_res(input_path)

    dlg_regex = r"^Dialogue: .,([^,]*),([^,]*),[^,]*,([^,]*),[^,]*,[^,]*,[^,]*,([^,]*),([^\n]*)"
    illegal_map = str.maketrans({"/": "zA", "<": "zB", ">": "zC", ":": "zD", '"': "zE", "\\": "zF", "|": "zG", "?": "zH", "*": "zI"})
        # so illegal characters don't break the file path


    print("Generating visuals...")

    line_count = 0
    for line in lines: 
        ass_iter = iterate_ass(line, line_count, dlg_regex, illegal_map)
        if ass_iter:
            matched_actor = ass_iter[0]
            matched_effect = ass_iter[1]
            act_eff_str = ass_iter[2]
            line_count = ass_iter[3]
            actor_dict = gen_act_dict(matched_actor,matched_effect,act_eff_str,line_count)
            if actor_dict:
                cooked_list = cook(actor_dict, act_eff_str, stack, vid_w, vid_h)  # act_eff_str isn't really necessary here except for error messages
                cooked_actors[act_eff_str] = cooked_list

    if will_only_cook:
        print("Visuals generated!")
    else:
        print("Visuals generated. Generating ffmpeg command...")

        ffmpeg_stitch_list = ["ffmpeg","-y","-i",input_path]
        act_eff_to_num = {}
        num_counter = 1
        for act_eff in cooked_actors:
            if cooked_actors[act_eff]:  # don't pass None as input
                act_stitch_list, act_eff_inp_num, num_counter = gen_actor_input(act_eff, num_counter)
                ffmpeg_stitch_list += act_stitch_list
                act_eff_to_num[act_eff] = act_eff_inp_num
        ffmpeg_stitch_list.append("-filter_complex")

        stitch_count = 0
        filter_string = '[0:v]'
        for line in lines:
            ass_iter = iterate_ass(line, line_count, dlg_regex, illegal_map)
            if ass_iter:
                act_eff_str = ass_iter[2]
                line_start = sex_to_sec(ass_iter[4])
                line_end = sex_to_sec(ass_iter[5])
                [filter_string, stitch_count] = stitch(filter_string, stitch_count, act_eff_str, act_eff_to_num,
                                            line_start, line_end)
        filter_string += "[v" + str(stitch_count) + "];[v" + str(stitch_count) + "]subtitles=" + ass_name

        ffmpeg_stitch_list.append(filter_string)
        ffmpeg_stitch_list.append("-c:a")
        ffmpeg_stitch_list.append("copy")
        ffmpeg_stitch_list.append(output_path)

        print("Generated command! Running overlay...")

        subprocess.run(ffmpeg_stitch_list)

        print("Wrote stitched video, processing complete!")