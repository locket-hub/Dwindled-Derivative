#!/bin/bash
# live_feed.sh
export DISPLAY=:0
ffplay -f v4l2 -framerate 30 -video_size 1280x720 -i /dev/video0