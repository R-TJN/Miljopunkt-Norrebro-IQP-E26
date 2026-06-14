import numpy as np
import argparse
import os
import re
import csv
import json
import ffmpeg
import hashlib
from datetime import datetime, timedelta
from DMRConnectLib import dmrlookup
import ReadWriteLib
import VideoProccessingLib
import constants 

"""
Program Structure: 
    1. Process Args
    2. Create file structure 
    3. Find Effective Start time 
    4. Proccess Video for words in frames
    5. Proccess words in each frame for plates, find vehicle info 
    6. Proccess P-trak data (if asked to)
    7. Compile data into correct formats and locations, hash plate numbers 
    8. Overlay data onto video 
"""
# Structure of variables 
# Vehicle Data : Hashed dictionary of all the vehicle data for each license plate that has ever been proccessed
# vehiclesInFrames : List of all of the hashed vehicle plates in each frame 
# metadata : dictionary of relavent metadata

vehicleData = {}
vehiclesInFrames = []
meta_data = { "airQuality" : "", "video" : ""}

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

input_video_path = args.video_file
track_pro_path = args.data_file
video_start_time = args.start_time
directory_name = str(args.directory_name).strip()

# 2. Create file structure 
meta_data_path, particle_data_path, vehicle_tracking_path, vehicle_data_path = ReadWriteLib.create_directory(directory_name)

# 3. Pull metadata (start-time, frameCount, framerate, resolution)  
video_meta_data = {}
media = ffmpeg.probe(input_video_path, cmd = 'ffprobe')
meta_data["video"] = media

# 4. Proccess Video for words in frames
words_in_frames = VideoProccessingLib.pull_text_by_frame(input_video_path)

# 5. Proccess words in each frame for plates, find vehicle info 
print("Starting Video Proccesing of " + str(input_video_path))

video_start_time = media['streams'][0]['tags']['creation_time']
video_time = datetime.fromisoformat(creation_time[0:10] + " " + creation_time[11:19])
delta = timedelta(seconds = 2) 
print("Video starts at" + video_time)

for frame in words_in_frames:
    plates = []
    for word in words_in_frames[frame]:
        hashed_word = hashlib.sha256(word[0]).hexdigest()
        if hashed_word in vehicle_data:
            #censorPlate(word) #TODO Implement 
            plates.append(hashed_word)
        else:
            vehicle_info = dmrlookup(word[0])
            if vehicle_info is not None:
                vehicle_data[hashed_word] = vehicle_info
                print(vehicle_data)
                #censor_plate(word)
                plates.append(hashed_word)
    vehicles_in_frames.append ({constants.VEHICLE_TRACKING_FEILDNAMES[0] : video_time.date(),
                                constants.VEHICLE_TRACKING_FEILDNAMES[1] : video_time.time(),
                                constants.VEHICLE_TRACKING_FEILDNAMES[2] : plates})
    video_time = video_time + delta 
               
            
# 6. Proccess P-trak data (if asked to)
p_track_data, p_track_meta_data = ReadWriteLib.load_trakpro_data(track_pro_path)
meta_data["airQuality"] = p_track_meta_data

# 7. Compile data into correct formats and locations, hash plate numbers 
# ReadWriteLib.write_air_quality_data(particleCountCSVPath, pTrackData)
with open(meta_data_path, "w") as f:
  f.write(json.dumps(meta_data, indent=4))

with open(vehicle_data_path, "w") as f:
  f.write(json.dumps(vehicle_data, indent=4))
    
with open(particle_data_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=constants.AIR_QUALITY_FIELDNAMES)
    writer.writeheader()
    writer.writerows(p_track_data)

with open(vehicle_tracking_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=constants.VEHICLE_TRACKING_FEILDNAMES)
    writer.writeheader()
    writer.writerows(vehicles_in_frames)
    
# 8. Overlay data onto video 

