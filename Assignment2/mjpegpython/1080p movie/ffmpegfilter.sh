#!/bin/sh
ffmpeg -i movie.mp4 -vf fps=25 out%04d.png

