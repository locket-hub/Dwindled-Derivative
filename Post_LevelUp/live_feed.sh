#!/bin/bash
# live_feed.sh
export Display=:0
ffplay -f v412 -framerate 30 -video_size 1080x1920 -i /dev/video0