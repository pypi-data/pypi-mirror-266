from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
import subprocess
import sys
import os
import re
import shutil
from pathlib import Path

def get_res(video):
    res_probe = subprocess.run(['ffprobe','-v','error','-select_streams',
                                'v:0','-show_entries','stream=height,width',
                                '-of','flat',video],stdout=subprocess.PIPE).stdout.decode('utf-8')
    (probe_w,probe_h) = res_probe.splitlines()
    res_w = probe_w.split("=")[1]
    res_h = probe_h.split("=")[1]
    return (res_w,res_h)

input_str = r"C:\Users\WV\Videos\Untitled.mp4"
input = Path(input_str)
print(get_res(input))