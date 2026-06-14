from typing import final 

# File and Directory Names 
MAIN_DIRECTORY_NAME = "./processed_data/"
METADATA_FILE_NAME = "/MetaData.json" 
PARTICLE_COUNT_FILE_NAME = "/AirQualityData.csv"
VEHICLE_TRACKING_FILE_NAME = "/VehicleData.csv"
COHESIVE_FILE_NAME = "/VehicleRegistry.json"


#Video Constants 
DEFAULT_FPS = 30

# EasyOCR Constants
BLOCK_LIST = ".,{}[]()|' "
DETAIL_SETTING = 1
CONFIDENCE = .9

AIR_QUALITY_FIELDNAMES = ["Date", "Time", "Particle_Count"]
VEHICLE_TRACKING_FEILDNAMES = ["Date", "Time", "plates"]