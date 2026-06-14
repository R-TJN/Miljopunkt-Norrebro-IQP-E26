import cv2
import easyocr
import numpy as np
import argparse
import os
import re
import constants 
from datetime import datetime, timedelta

#Matches an on-screen clock reading (HH:MM:SS).
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
    
def pull_text_by_frame(VIDEO_IN): 
    #Initialize list of return Frames. Each element in return list will be a list of words 
    returnFrames = {}
    
    video = cv2.VideoCapture(VIDEO_IN)
    # Check if camera opened successfully
    if (video.isOpened() == False):
        print("Error opening video stream or file")
    reader = easyocr.Reader(['en', 'da'])
    

    #Frame rate is needed to convert frame number to elapsed seconds
    #Frame Count is used to measure progress through video
    frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = constants.DEFAULT_FPS
        
    print("Opening file of " + str(frames) + " Frames. Video is " + str(fps) + " fps")
    print("Processing... press Ctrl+C in the terminal to stop early and save output")

    try:
        frameCount = 1
        #Read until video is completed
        while(video.isOpened()):
            #Capture frame-by-frame
            ret, frame = video.read()
            #Check for valid return "ret"
            if ret == True:
                # List of all of the words in the frame, in the format Of: 
                # (Word, TopLeft, BottomRight) -> (String, (int, int), (int, int)) 
                words = []
                result = reader.readtext(frame, 
                                         detail=constants.DETAIL_SETTING, 
                                         text_threshold=constants.CONFIDENCE, 
                                         blocklist= constants.BLOCK_LIST)
                print("Frame : " + str(frameCount) + "/" + str(frames) + " result: ")

                #Find each piece of detected text
                for word in result:
                    plate_text = str(word[1]).strip().upper()
  
                    #Bounding box of this detection.
                    top_left = (int(word[0][0][0]), int(word[0][0][1]))
                    bottom_right = (int(word[0][2][0]), int(word[0][2][1]))
                    words.append( (plate_text, top_left, bottom_right))
                    
                returnFrames[frameCount] = words 
                frameCount += 1
    
            #Break the loop
            else:
                break
    
    except KeyboardInterrupt:
        #Ctrl+C: stop early but fall through to finally so the video is saved
        print("\nStopping early (Ctrl+C) -- finalizing the video file...")
    
    finally:
        video.release()
        return returnFrames

            #Output filename derived from the input video
    #out = cv2.VideoWriter(VIDEO_OUT, cv2.VideoWriter_fourcc(*'avc1'), 30, (frame_width, frame_height))

    """
        #Warn if auto-detection was requested but no clock was ever found
        if VIDEO_START_TIME is None and video_start_dt is None:
            print("\nWarning: no on-screen clock was detected, so no data overlay was drawn. You can pass the start time manually as the third argument (HH:MM:SS).")\
    

    #Load the data we want to overlay, and figure out the timeline
# data_map, data_start_time, data_units, data_label = load_trakpro_data(DATA_FILE)

#Borrow the calendar date from the data file so both timelines sit on the same day; if the data file is empty, fall back to today's date
# base_date = data_start_time.date() if data_start_time is not None else datetime.now().date()

#If a start time was given on the command line, use it directly. Otherwise leave video_start_dt as None and detect it from the on-screen clock below

                
                #Live preview window, only when --show
                if args.show:
                    cv2.imshow('Frame', frame)
                    #Press Q on keyboard to exit
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break
                


if VIDEO_START_TIME is not None:
    start_time_only = datetime.strptime(VIDEO_START_TIME, '%H:%M:%S').time()
    video_start_dt = datetime.combine(base_date, start_time_only)
    print(f"Using start time from command line: {video_start_dt.time()}")
else:
    video_start_dt = None
    print("No start time given -- will auto-detect an on-screen clock (HH:MM:SS).")



    #Running totals
    
    gas_count = 0
    ev_count = 0
    diesel_count = 0
    seen_plates = set()  #track already counted plates
    plate_cache = {}  #maps plate text to lookup result
    
                
                #Auto-detect the on-screen clock to set the start time
                if video_start_dt is None:
                    detected = detect_clock_time(result)
                    if detected is not None:
                        detected_dt = datetime.combine(base_date, detected)
                        video_start_dt = detected_dt - timedelta(seconds=(frameCount - 1) / fps)
                        print(f"Detected clock {detected} at frame {frameCount} " f"({(frameCount - 1) / fps:.2f}s in); " f"video start set to {video_start_dt.time()}") 
                  
                    #Check cache first, only call dmrlookup on new plates
                    if plate_text in plate_cache:
                        lookup = plate_cache[plate_text]
                    else:
                        try:
                            lookup = dmrlookup(plate_text)
                        except (IndexError, Exception):
                            lookup = None
                        plate_cache[plate_text] = lookup
                   
                    # Block out the detected text
                    # frame = cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), -1)
                    
                    if lookup != None:
                        print(lookup)
                    
                    #Only count each plate once
                    if plate_text not in seen_plates:
                        seen_plates.add(plate_text)

                        powertrain = lookup['powertrain'].lower() if lookup['powertrain'] else ''
                        if 'diesel' in powertrain:
                            diesel_count += 1
                        elif 'el' in powertrain or 'electric' in powertrain:
                            ev_count += 1
                        elif 'benzin' in powertrain or 'gas' in powertrain:
                            gas_count += 1

                    label = lookup['powertrain'] if lookup['powertrain'] else 'Unknown'
                    frame = cv2.putText(frame, label, (top_left[0], bottom_right[1] + 25),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                
                #Draw counter overlay in top left
                cv2.putText(frame, f'Gas: {gas_count}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f'Diesel: {diesel_count}', (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f'EV: {ev_count}', (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                if video_start_dt is not None and data_start_time is not None:
                    elapsed_seconds = (frameCount - 1) / fps
                    current_time = video_start_dt + timedelta(seconds=elapsed_seconds)
                    current_second = current_time.replace(microsecond=0)
    
                    if current_second >= data_start_time:
                        value = data_map.get(current_second)
                        if value is None:
                            value_text = f'-- {data_units}'
                        else:
                            value_text = f'{value} {data_units}'
    
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
                

    #Print final summary to console
    print("\nFinal Count)
    print(f"Gas: {gas_count}")
    print(f"Diesel: {diesel_count}")
    print(f"EV: {ev_count}")
    print(f"Total unique vehicles: {len(seen_plates)}")
    print(f"Frames processed: {frameCount - 1}")
    print(f"Saved output to: {output_file}")

    #Always release so the output file is written out correctly
    """
