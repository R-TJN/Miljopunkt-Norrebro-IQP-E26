import numpy as np
import argparse
import os
import re
from datetime import datetime, timedelta

#from dmrlookup import dmrlookup
import ReadWriteLib
#import VideoProccesingLib
import constants 
"""
Program Structure: 
    1. Process Args
    2. Create file structure 
    3. Find Effective Start time 
    4. Proccess P-trak data (if asked to)
    5. Proccess Video for words in frames
    6. Proccess words in each frame for plates, find vehicle info 
    7. Compile data into correct formats and locations, hash plate numbers 
    8. Overlay data onto video 
"""

# 1. Process Args
#python ProccessVideo.py <video_file> <data_file> <directory_name> [start_time] [--show]
parser = argparse.ArgumentParser(
description='Count vehicles by powertrain and overlay time-synced data onto a video.')
parser.add_argument('video_file', help='Video file name')
parser.add_argument('data_file', help='TrakPro data file name')
parser.add_argument('directory_name', help='name of directory files will be saved to')
parser.add_argument('start_time', nargs='?', default=None, help='Optional. Time the video starts, HH:MM:SS. If omitted, the start time is auto-detected by reading an on-screen clock (e.g. a phone held in front of the sensor).')
parser.add_argument('--show', action='store_true', help='Show the video in a live window while processing; press Q to quit early')
args = parser.parse_args()

inputVideoPath = args.video_file
trackProPath = args.data_file
videoStartTime = args.start_time
directoryName = str(args.directory_name).strip()

# 2. Create file structure 
mataDataPath, particleCountCSVPath, vehicleTrackingCSVPath, cohesiveOutputCSVPath = ReadWriteLib.create_directory(directoryName)

# 3. Find Effective Start time 

# 4. Proccess P-trak data (if asked to)

# 5. Proccess Video for words in frames
# wordsInFrames = pullTextByFrame(inputVideoPath)

# 6. Proccess words in each frame for plates, find vehicle info 

# 7. Compile data into correct formats and locations, hash plate numbers 

# 8. Overlay data onto video 

