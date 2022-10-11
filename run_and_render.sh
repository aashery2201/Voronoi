#!/usr/bin/env bash

python main.py -p1 4 --last 50 --spawn 4
echo "Rendering frames..."
python render_game.py
#echo "Creating video..."
#convert -delay 5 -loop 0 $(ls -1 render/*.png | sort -V) -quality 95 game.mp4