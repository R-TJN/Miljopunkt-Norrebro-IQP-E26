import cv2
import easyocr
import numpy as np
import argparse
import os
import re
from datetime import datetime, timedelta
from dmrlookup import dmrlookup

#python ProccessVideo.py <video_file> <data_file> [start_time] [--show]
parser = argparse.ArgumentParser(
description='Count vehicles by powertrain and overlay time-synced data onto a video.')
parser.add_argument('video_file', help='Video file name')
parser.add_argument('data_file', help='TrakPro data file name')
parser.add_argument('start_time', nargs='?', default=None, help='Optional. Time the video starts, HH:MM:SS. If omitted, the start time is auto-detected by reading an on-screen clock (e.g. a phone held in front of the sensor).')
parser.add_argument('--show', action='store_true', help='Show the video in a live window while processing; press Q to quit early')
args = parser.parse_args()

VIDEO_FILE = args.video_file
DATA_FILE = args.data_file
VIDEO_START_TIME = args.start_time
