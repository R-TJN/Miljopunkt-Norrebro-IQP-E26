import cv2 
import easyocr 
import numpy as np
from dmrlookup import dmrlookup

video = cv2.VideoCapture('Test1.1.mov')
reader = easyocr.Reader(['en', 'da'])

# Check if camera opened successfully
if (video.isOpened()== False):
  print("Error opening video stream or file")

frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
print("Opening file of " + str(frames) + " Frames")
frameCount = 1
frame_width = int(video.get(3))
frame_height = int(video.get(4))

out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))

# Read until video is completed
while(video.isOpened()):
  # Capture frame-by-frame
  ret, frame = video.read()
  if ret == True:
    result = reader.readtext(frame ,detail = 1, text_threshold = .9, blocklist = ".,{}[]()|' " )
    print("Frame " + str(frameCount) +  " result: ")

   # Find and Display words 
    for word in result: 
        #print(str(word[1]))
        lookup = dmrlookup(str(word[1]))
        if lookup != None:
          print(lookup)
          frame = cv2.putText(frame, lookup['powertrain'], (int(word[0][0][0]), int(word[0][2][1]) + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 2)
        
        frame = cv2.rectangle(frame, (int(word[0][0][0]), int(word[0][0][1])), (int(word[0][2][0]), int(word[0][2][1])), (0,255,0) , 2)
        frame = cv2.putText(frame, word[1], (int(word[0][0][0]), int(word[0][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 2)
        
    # Display the resulting frame
    out.write(frame)
    cv2.imshow('Frame',frame)
    frameCount = frameCount + 1
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
 
  # Break the loop
  else:
    break
 
# When everything done, release the video capture object
video.release()
out.release()
 
# Closes all the frames
cv2.destroyAllWindows()
