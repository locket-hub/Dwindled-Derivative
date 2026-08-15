#!/bin/bash
# live_feed.sh
export DISPLAY=:0
ffplay -f v4l2 -framerate 30 -video_size 1080x1920 -i /dev/video0