import cv2
import json
import ffmpeg
import easyocr 

media = ffmpeg.probe("Data4.mp4", cmd='ffprobe')

print(media)