# Dramasub

A tool for auto-generating visuals for a video based off of an `.ass` subtitle file. Intended for creating visual novel-style visual accompaniments for audio-only content, such as drama CDs.

### Installation and Requirements:

Dramasub can be installed via:

`pip install dramasub`

Requires [FFmpeg](https://ffmpeg.org/) to be installed and for both `ffmpeg` and `ffprobe` configured in PATH. Also requires the [Wand Python bindings](https://docs.wand-py.org/), which requires ImageMagick; please see the Wand documentation for installation instructions.

Has only been tested with Windows, but may work on other platforms.


### Args:
* `-i`, `--input`: Input video file (audio and non-overlay background visuals, such as scene transitions)
* `-o`, `--output`: Output video file
* `-c`, `--config`: Config file (`.py`) that lists what visuals are assigned to each Actor and Effect specified in the .ass subtitle file. For more details, see `examples/example_config.py`.
* `-a`, `-ass`: Input subtitle file (`.ass`). **IMPORTANT: Must be in the current working directory** (path your terminal is in) due to issues with ffmpeg. For an example actor/effect setup, see `examples/example_sub.ass`.
* `--cook_only` (optional): For previewing visuals without processing the whole video. Only reads the `.ass` file and generates accompanying images to the `kitchen` path specified in the config. If set, does not require output video path to be specified, but input video is still required.