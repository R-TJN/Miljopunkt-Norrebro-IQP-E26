import cv2
import easyocr
import numpy as np
import argparse
import os
from datetime import datetime, timedelta
from dmrlookup import dmrlookup

#   python videocounting.py <video_file> <data_file> <start_time>
parser = argparse.ArgumentParser(
    description='Count vehicles by powertrain and overlay time-synced data onto a video.')
parser.add_argument('video_file', help='Video file name, e.g. 1.6.26Test.mp4')
parser.add_argument('data_file', help='TrakPro/P-Trak data file name, e.g. 6_1_2.txt')
parser.add_argument('start_time', help='Time the video starts, HH:MM:SS, e.g. 11:46:15')
args = parser.parse_args()

VIDEO_FILE = args.video_file
DATA_FILE = args.data_file
# Only the time is supplied on the command line; the date is taken from the
# data file so the two timelines line up on the same calendar day.
VIDEO_START_TIME = args.start_time


def load_trakpro_data(path):
    """
    Parse a TrakPro ASCII data file (e.g. a P-Trak export).

    Returns:
        data_map:  dict mapping datetime (1-second precision) -> value (int) or None
        start_dt:  datetime of the earliest data row (None if file has no data)
        units:     units label string, e.g. 'pt/cc'
        label:     measurement label string, e.g. 'Pt Conc'
    """
    data_map = {}
    units = ''
    label = 'Value'

    with open(path, 'r') as f:
        for line in f:
            fields = [c.strip() for c in line.strip().split(',')]
            if len(fields) < 3:
                continue

            # Column header row:  Date,Time,Pt Conc
            if fields[0] == 'Date' and fields[1] == 'Time':
                label = fields[2]
                continue

            # Units row:  MM/dd/yyyy,hh:mm:ss,pt/cc
            if fields[0] == 'MM/dd/yyyy' and fields[1] == 'hh:mm:ss':
                units = fields[2]
                continue

            # Data row:  06/01/2026,11:46:16,9670   (or ...,Invalid)
            try:
                dt = datetime.strptime(fields[0] + ' ' + fields[1], '%m/%d/%Y %H:%M:%S')
            except ValueError:
                continue  # not a data row (header text, blank line, etc.)

            try:
                value = int(fields[2])
            except ValueError:
                value = None  # 'Invalid' or any non-numeric reading

            data_map[dt] = value

    start_dt = min(data_map.keys()) if data_map else None
    return data_map, start_dt, units, label


video = cv2.VideoCapture(VIDEO_FILE)
reader = easyocr.Reader(['en', 'da'])

# Load the data we want to overlay, and figure out the timeline.
data_map, data_start_time, data_units, data_label = load_trakpro_data(DATA_FILE)

# Only a time (HH:MM:SS) is given on the command line. Borrow the calendar
# date from the data file so both timelines sit on the same day; if the data
# file is empty, fall back to today's date (the overlay won't show anyway).
start_time_only = datetime.strptime(VIDEO_START_TIME, '%H:%M:%S').time()
base_date = data_start_time.date() if data_start_time is not None else datetime.now().date()
video_start_dt = datetime.combine(base_date, start_time_only)

# Check if camera opened successfully
if (video.isOpened() == False):
    print("Error opening video stream or file")

frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
print("Opening file of " + str(frames) + " Frames")
frameCount = 1
frame_width = int(video.get(3))
frame_height = int(video.get(4))

# Frame rate is needed to convert frame number -> elapsed seconds.
fps = video.get(cv2.CAP_PROP_FPS)
if not fps or fps <= 0:
    fps = 30.0  # fall back to the writer's rate if metadata is missing

# Output filename derived from the input video
output_file = os.path.splitext(VIDEO_FILE)[0] + 'output.mp4'
out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'avc1'), 30, (frame_width, frame_height))

# Running totals
gas_count = 0
ev_count = 0
diesel_count = 0
seen_plates = set()  # track already counted plates
plate_cache = {}  # maps plate text -> lookup result

# Read until video is completed
while(video.isOpened()):
    # Capture frame-by-frame
    ret, frame = video.read()
    if ret == True:
        result = reader.readtext(frame, detail=1, text_threshold=.9, blocklist=".,{}[]()|' ")
        print("Frame " + str(frameCount) + " result: ")

        # Find and display words
        for word in result:
            plate_text = str(word[1]).strip().upper()

            # Check cache first, only call dmrlookup on new plates
            if plate_text in plate_cache:
                lookup = plate_cache[plate_text]
            else:
                try:
                    lookup = dmrlookup(plate_text)
                except (IndexError, Exception):
                    lookup = None
                plate_cache[plate_text] = lookup  # cache it (even if None)

            if lookup != None:
                print(lookup)

                # Only count each plate once
                if plate_text not in seen_plates:
                    seen_plates.add(plate_text)

                    powertrain = lookup['powertrain'].lower() if lookup['powertrain'] else ''
                    if 'diesel' in powertrain:
                        diesel_count += 1
                    elif 'el' in powertrain or 'electric' in powertrain:
                        ev_count += 1
                    elif 'benzin' in powertrain or 'gas' in powertrain:
                        gas_count += 1

                frame = cv2.putText(frame, lookup['powertrain'], (int(word[0][0][0]), int(word[0][2][1]) + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            frame = cv2.rectangle(frame, (int(word[0][0][0]), int(word[0][0][1])), (int(word[0][2][0]), int(word[0][2][1])), (0, 255, 0), 2)
            frame = cv2.putText(frame, word[1], (int(word[0][0][0]), int(word[0][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Draw counter overlay in top left
        cv2.putText(frame, f'Gas: {gas_count}',     (20, 40),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Diesel: {diesel_count}',(20, 80),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'EV: {ev_count}',        (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # ---- Data overlay in top right, synced to wall-clock time ----
        # Elapsed video time at this frame, converted to a wall-clock moment.
        elapsed_seconds = (frameCount - 1) / fps
        current_time = video_start_dt + timedelta(seconds=elapsed_seconds)
        current_second = current_time.replace(microsecond=0)  # round down to the second

        # Only show the overlay once the video clock has caught up to the
        # data's start time (i.e. the two timelines are synced).
        if data_start_time is not None and current_second >= data_start_time:
            value = data_map.get(current_second)
            if value is None:
                value_text = f'-- {data_units}'        # missing or 'Invalid' reading
            else:
                value_text = f'{value} {data_units}'

            # Right-align both lines in the top-right corner.
            for i, text in enumerate((data_label, value_text)):
                (text_w, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                x = frame_width - text_w - 20
                y = 40 + i * 40
                cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Write the resulting frame
        out.write(frame)
        frameCount += 1
        cv2.imshow('Frame',frame)
        # Press Q on keyboard to  exit
        if cv2.waitKey(10) & 0xFF == ord('q'):
          break

    # Break the loop
    else:
        break

# Print final summary to console
print("\n--- Final Count ---")
print(f"Gas:    {gas_count}")
print(f"Diesel: {diesel_count}")
print(f"EV:     {ev_count}")
print(f"Total unique vehicles: {len(seen_plates)}")

# When everything done, release the video capture object
video.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()
