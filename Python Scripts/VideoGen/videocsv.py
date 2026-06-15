import cv2
import easyocr
import argparse
import os
import re
import csv
from datetime import datetime, timedelta
from dmrlookup import dmrlookup

#python videocounting.py <video_file> <data_file> [start_time]
parser = argparse.ArgumentParser(
description='Detect vehicle plates in a video and export per-second vehicle and particle data to a CSV.')
parser.add_argument('video_file', help='Video file name')
parser.add_argument('data_file', help='TrakPro data file name')
parser.add_argument('start_time', nargs='?', default=None, help='Optional. Time the video starts, HH:MM:SS. If omitted, the start time is auto-detected by reading an on-screen clock (e.g. a phone held in front of the sensor).')
args = parser.parse_args()

VIDEO_FILE = args.video_file
DATA_FILE = args.data_file
VIDEO_START_TIME = args.start_time

#Matches an on-screen clock reading
CLOCK_RE = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

def detect_clock_time(ocr_result):
    for word in ocr_result:
        match = CLOCK_RE.search(str(word[1]))
        if match:
            try:
                return datetime.strptime(match.group(1), '%H:%M:%S').time()
            except ValueError:
                continue
    return None


def classify_powertrain(lookup):
    #Map a DMR lookup result to one of 'diesel', 'ev', 'gas', or none
    if not lookup:
        return None
    powertrain = lookup['powertrain'].lower() if lookup['powertrain'] else ''
    if 'diesel' in powertrain:
        return 'diesel'
    elif 'el' in powertrain or 'electric' in powertrain:
        return 'ev'
    elif 'benzin' in powertrain or 'gas' in powertrain:
        return 'gas'
    return None


def load_trakpro_data(path):
    data_map = {}
    units = ''
    label = 'Value'
    with open(path, 'r') as f:
        for line in f:
            fields = [c.strip() for c in line.strip().split(',')]
            if len(fields) < 3:
                continue

            #Column header row: Date,Time,Pt Conc
            if fields[0] == 'Date' and fields[1] == 'Time':
                label = fields[2]
                continue

            #Units row: MM/dd/yyyy,hh:mm:ss,pt/cc
            if fields[0] == 'MM/dd/yyyy' and fields[1] == 'hh:mm:ss':
                units = fields[2]
                continue

            #Data row
            try:
                dt = datetime.strptime(fields[0] + ' ' + fields[1], '%m/%d/%Y %H:%M:%S')
            except ValueError:
                continue

            try:
                value = int(fields[2])
            except ValueError:
                value = None
            data_map[dt] = value

    start_dt = min(data_map.keys()) if data_map else None
    return data_map, start_dt, units, label


video = cv2.VideoCapture(VIDEO_FILE)
reader = easyocr.Reader(['en', 'da'])

#Load the particle data and figure out the timeline
data_map, data_start_time, data_units, data_label = load_trakpro_data(DATA_FILE)

#Borrow the calendar date from the data file so both timelines sit on the same day; if the data file is empty, fall back to today's date
base_date = data_start_time.date() if data_start_time is not None else datetime.now().date()

#If a start time was given on the command line, use it directly. Otherwise leave video_start_dt as None and detect it from the on-screen clock below
if VIDEO_START_TIME is not None:
    start_time_only = datetime.strptime(VIDEO_START_TIME, '%H:%M:%S').time()
    video_start_dt = datetime.combine(base_date, start_time_only)
    print(f"Using start time from command line: {video_start_dt.time()}")
else:
    video_start_dt = None
    print("No start time given -- will auto-detect an on-screen clock (HH:MM:SS).")

#Check if video opened successfully
if (video.isOpened() == False):
    print("Error opening video stream or file")

frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
print("Opening file of " + str(frames) + " Frames")
print("Processing... press Ctrl+C in the terminal to stop early and save the CSV.")
frameCount = 1

#Frame rate is needed to convert frame number to elapsed seconds
fps = video.get(cv2.CAP_PROP_FPS)
if not fps or fps <= 0:
    fps = 30.0

seen_plates = set()
plate_cache = {}
per_second_counts = {}

try:
    while(video.isOpened()):
        ret, frame = video.read()
        if ret == True:
            result = reader.readtext(frame, detail=1, text_threshold=.6, blocklist=".,{}[]()|' ")
            print("Frame " + str(frameCount))

            #Auto-detect the on-screen clock to set the start time
            if video_start_dt is None:
                detected = detect_clock_time(result)
                if detected is not None:
                    detected_dt = datetime.combine(base_date, detected)
                    video_start_dt = detected_dt - timedelta(seconds=(frameCount - 1) / fps)
                    print(f"Detected clock {detected} at frame {frameCount} " f"({(frameCount - 1) / fps:.2f}s in); " f"video start set to {video_start_dt.time()}")

            #Second for this frame. Stays None until a start time is known
            current_second = None
            if video_start_dt is not None:
                current_second = (video_start_dt + timedelta(seconds=(frameCount - 1) / fps)).replace(microsecond=0)
                per_second_counts.setdefault(current_second, {'plates': set(), 'ev': set(), 'diesel': set(), 'gas': set()})

            #Look up each piece of detected text and record it against the current second
            for word in result:
                plate_text = str(word[1]).strip().upper()
                #Check cache first, only call dmrlookup on new plates
                if plate_text in plate_cache:
                    lookup = plate_cache[plate_text]
                else:
                    try:
                        lookup = dmrlookup(plate_text)
                    except (IndexError, Exception):
                        lookup = None
                    plate_cache[plate_text] = lookup

                if lookup is None:
                    continue

                seen_plates.add(plate_text)
                category = classify_powertrain(lookup)

                #Record this vehicle against the current second for the CSV
                if current_second is not None:
                    bucket = per_second_counts[current_second]
                    bucket['plates'].add(plate_text)
                    if category in ('ev', 'diesel', 'gas'):
                        bucket[category].add(plate_text)

            frameCount += 1

        #Break the loop
        else:
            break

except KeyboardInterrupt:
    #Ctrl+C stop early but fall through to finally so the CSV is written
    print("\nStopping early (Ctrl+C) -- finalizing the CSV...")

finally:
    #Warn if auto-detection was requested but no clock was ever found
    if VIDEO_START_TIME is None and video_start_dt is None:
        print("\nWarning: no on-screen clock was detected, so the CSV has no rows. You can pass the start time manually as the third argument (HH:MM:SS).")

    #Write the CSV
    csv_file = os.path.splitext(VIDEO_FILE)[0] + 'output.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        particle_header = f'Particle Count ({data_units})' if data_units else 'Particle Count'
        writer.writerow(['Timestamp', particle_header, 'Vehicles In Frame', 'EVs', 'Diesel', 'Benzin'])

        if per_second_counts:
            current = min(per_second_counts)
            last = max(per_second_counts)
            while current <= last:
                bucket = per_second_counts.get(current)
                vehicles = len(bucket['plates']) if bucket else 0
                evs = len(bucket['ev']) if bucket else 0
                diesel = len(bucket['diesel']) if bucket else 0
                benzin = len(bucket['gas']) if bucket else 0

                value = data_map.get(current)
                particle = '' if value is None else value

                writer.writerow([current.strftime('%H:%M:%S'), particle, vehicles, evs, diesel, benzin])
                current += timedelta(seconds=1)

    print("\nDone")
    print(f"Total unique vehicles: {len(seen_plates)}")
    print(f"Frames processed: {frameCount - 1}")
    print(f"Saved CSV to: {csv_file}")

    #Release the capture
    video.release()
