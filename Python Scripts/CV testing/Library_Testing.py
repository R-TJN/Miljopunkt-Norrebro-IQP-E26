import cv2
import json
import ffmpeg
import easyocr 

### EasyOcr Testing
reader = easyocr.Reader(['en', 'da'])
result = reader.readtext('Test2.png',detail = 0, text_threshold = .9, blocklist = "., " )
print(result)

### Exif data testing
media = ffmpeg.probe("Data4.mp4", cmd='ffprobe')

print(f"# Video")
print(f"- Codec: {media['streams'][0]['codec_name']}")
print(f"- Resolution: {media['streams'][0]['width']} X {media['streams'][0]['height']}")
print(f"- Duration: {media['streams'][0]['duration']}")
print(f"- Creation Time: {media['streams'][0]['tags']['creation_time']}")
print("")

print(f"# Audio")
print(f"- Codec: {media['streams'][1]['codec_name']}")
print(f"- Sample Rate: {media['streams'][1]['sample_rate']}")
print(f"- Duration: {media['streams'][1]['duration']}")
# print(media)

### OpencV Testing 

print("Open")
img = cv2.imread("Test2.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
bfilter = cv2.bilateralFilter(gray, 11, 11, 17) 
edged = cv2.Canny(bfilter, 30, 200)

cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
cv2.imshow('Display', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Close") 
