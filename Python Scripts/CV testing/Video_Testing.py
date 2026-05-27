import cv2 
import easyocr 
import numpy as np

video = cv2.VideoCapture('Data4.mp4')
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
        print(word)
        frame = cv2.rectangle(frame, word[0][0], word[0][2], (255,0,0) , 2)
        frame = cv2.putText(frame, word[1], word[0][0], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
    # Display the resulting frame
    out.write(frame)
    # cv2.imshow('Frame',frame)
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