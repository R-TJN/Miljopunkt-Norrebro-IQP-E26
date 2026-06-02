import cv2
import easyocr
import numpy as np
import argparse
import os
import re
from datetime import datetime, timedelta
from dmrlookup import dmrlookup

#   python videocounting.py <video_file> <data_file> [start_time] [--show]
parser = argparse.ArgumentParser(
    description='Count vehicles by powertrain and overlay time-synced data onto a video.')
parser.add_argument('video_file', help='Video file name, e.g. 1.6.26Test.mp4')
parser.add_argument('data_file', help='TrakPro/P-Trak data file name, e.g. 6_1_2.txt')
parser.add_argument('start_time', nargs='?', default=None,
                    help='Optional. Time the video starts, HH:MM:SS, e.g. 11:46:15. '
                         'If omitted, the start time is auto-detected by reading an '
                         'on-screen clock (e.g. a phone held in front of the sensor).')
parser.add_argument('--show', action='store_true',
                    help='Show the video in a live window while processing; press Q to quit early')
args = parser.parse_args()

VIDEO_FILE = args.video_file
DATA_FILE = args.data_file
# Only the time is supplied on the command line; the date is taken from the
# data file so the two timelines line up on the same calendar day.
# This may be None, in which case the start time is detected from the video.
VIDEO_START_TIME = args.start_time

# Matches an on-screen clock reading (HH:MM:SS).
CLOCK_RE = re.compile(r'(\d{1,2}:\d{2}:\d{2})')


def detect_clock_time(ocr_result):
    """
    Scan a frame's OCR results for the first valid HH:MM:SS clock reading.
    Returns a datetime.time, or None if no valid time is found.
    """
    for word in ocr_result:
        match = CLOCK_RE.search(str(word[1]))
        if match:
            try:
                return datetime.strptime(match.group(1), '%H:%M:%S').time()
            except ValueError:
                continue  # e.g. 99:99:99 -- keep looking
    return None


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

# Borrow the calendar date from the data file so both timelines sit on the
# same day; if the data file is empty, fall back to today's date.
base_date = data_start_time.date() if data_start_time is not None else datetime.now().date()

# If a start time was given on the command line, use it directly. Otherwise
# leave video_start_dt as None and detect it from the on-screen clock below.
if VIDEO_START_TIME is not None:
    start_time_only = datetime.strptime(VIDEO_START_TIME, '%H:%M:%S').time()
    video_start_dt = datetime.combine(base_date, start_time_only)
    print(f"Using start time from command line: {video_start_dt.time()}")
else:
    video_start_dt = None
    print("No start time given -- will auto-detect an on-screen clock (HH:MM:SS).")

# Check if camera opened successfully
if (video.isOpened() == False):
    print("Error opening video stream or file")

frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
print("Opening file of " + str(frames) + " Frames")
print("Processing... press Ctrl+C in the terminal to stop early and save the video.")
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

# The whole loop runs inside try/finally so that, however it ends -- normal
# end of video, Q keypress, or Ctrl+C
try:
    # Read until video is completed
    while(video.isOpened()):
        # Capture frame-by-frame
        ret, frame = video.read()
        if ret == True:
            result = reader.readtext(frame, detail=1, text_threshold=.9, blocklist=".,{}[]()|' ")
            print("Frame " + str(frameCount) + " result: ")

            # ---- Auto-detect the on-screen clock to set the start time ----
            # Runs only in auto mode (video_start_dt is None) and only until the
            # first valid reading is found. Done before any redaction below so
            # the clock is still readable to the OCR even though we cover it.
            if video_start_dt is None:
                detected = detect_clock_time(result)
                if detected is not None:
                    detected_dt = datetime.combine(base_date, detected)
                    # The clock was read at this frame, i.e. (frameCount-1)/fps
                    # seconds into the video. Rewind by that delay so video_start_dt
                    # is the wall-clock time of frame 1.
                    video_start_dt = detected_dt - timedelta(seconds=(frameCount - 1) / fps)
                    print(f"Detected clock {detected} at frame {frameCount} "
                          f"({(frameCount - 1) / fps:.2f}s in); "
                          f"video start set to {video_start_dt.time()}")

            # Find each piece of detected text (license plates, etc.)
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

                # Bounding box of this detection.
                top_left = (int(word[0][0][0]), int(word[0][0][1]))
                bottom_right = (int(word[0][2][0]), int(word[0][2][1]))

                # Block out the detected text with a SOLID green box (thickness
                # -1 fills it) so the license plate number itself is never shown.
                frame = cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), -1)

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

                    # Show the propulsion type INSTEAD of the plate number,
                    # just below the blocked-out box.
                    label = lookup['powertrain'] if lookup['powertrain'] else 'Unknown'
                    frame = cv2.putText(frame, label, (top_left[0], bottom_right[1] + 25),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw counter overlay in top left
            cv2.putText(frame, f'Gas: {gas_count}',     (20, 40),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Diesel: {diesel_count}',(20, 80),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'EV: {ev_count}',        (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Only once we know the video start time (given or detected) and we have data to show.
            if video_start_dt is not None and data_start_time is not None:
                elapsed_seconds = (frameCount - 1) / fps
                current_time = video_start_dt + timedelta(seconds=elapsed_seconds)
                current_second = current_time.replace(microsecond=0)  # round down to the second

                # Only show the overlay once the video clock has caught up to the
                # data's start time (i.e. the two timelines are synced).
                if current_second >= data_start_time:
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

            #Current time display bottom right
            if video_start_dt is not None:
                time_text = (video_start_dt + timedelta(seconds=(frameCount - 1) / fps)).strftime('%H:%M:%S')
            else:
                time_text = 'N/A'
            (time_w, _), _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
            cv2.putText(frame, time_text, (frame_width - time_w - 20, frame_height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Write the resulting frame
            out.write(frame)
            frameCount += 1

            # Live preview window, only when --show is passed.
            if args.show:
                cv2.imshow('Frame', frame)
                # Press Q on keyboard to exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

        # Break the loop
        else:
            break

except KeyboardInterrupt:
    # Ctrl+C: stop early but fall through to finally so the video is saved.
    print("\nStopping early (Ctrl+C) -- finalizing the video file...")

finally:
    # Warn if auto-detection was requested but no clock was ever found.
    if VIDEO_START_TIME is None and video_start_dt is None:
        print("\nWarning: no on-screen clock was detected, so no data overlay was drawn. "
              "You can pass the start time manually as the third argument (HH:MM:SS).")

    # Print final summary to console
    print("\n--- Final Count ---")
    print(f"Gas:    {gas_count}")
    print(f"Diesel: {diesel_count}")
    print(f"EV:     {ev_count}")
    print(f"Total unique vehicles: {len(seen_plates)}")
    print(f"Frames processed: {frameCount - 1}")
    print(f"Saved output to: {output_file}")

    # Always release so the output file is written out correctly.
    video.release()
    out.release()
    cv2.destroyAllWindows()
