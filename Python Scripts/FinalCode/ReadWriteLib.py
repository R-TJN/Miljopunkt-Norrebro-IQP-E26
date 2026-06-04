import os
import csv
import constants 

def load_trakpro_data(readPath: str, writePath):
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

            # Units row: MM/dd/yyyy,hh:mm:ss,pt/cc
            if fields[0] == 'MM/dd/yyyy' and fields[1] == 'hh:mm:ss':
                units = fields[2]
                continue

            # Data row
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

def create_directory(directory_name: str):

    #File Paths Naming
    directoryPath = constants.MAIN_DIRECTORY_NAME + directory_name
    metadataPath = directoryPath + constants.METADATA_FILE_NAME
    airQualityPath = directoryPath + constants.PARTICLE_COUNT_FILE_NAME
    vehicleTrackingPath = directoryPath + constants.VEHICLE_TRACKING_FILE_NAME
    cohesivePath = directoryPath + constants.COHESIVE_FILE_NAME 

    filePaths = [metadataPath, airQualityPath, vehicleTrackingPath, cohesivePath]

    # If the overall data directory or specified directory do not exist, create them
    if not os.path.exists(constants.MAIN_DIRECTORY_NAME):
        os.makedirs(constants.MAIN_DIRECTORY_NAME)

    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)

    # If any of the files dont exist then create them 
    for filePath in filePaths:
        if not os.path.exists(filePath):
            file = open(filePath, "x")
            
    return filePaths
    
    