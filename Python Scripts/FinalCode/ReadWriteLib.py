import os
import csv
import constants 

def load_trakpro_data(path: str):
    particle_data = []
    meta_data = {}
    with open(path, 'r') as f:
        count = 0
        for line in f:
            count += 1
            if count in [6,8,9,10,12,13]:
                x = line.split(":,")
                print(x[0])
                print(x[1])
                meta_data[x[0]] = x[1]

            elif count in [18, 19, 20, 22, 23]:
                x = line.split(":,")
                meta_data[x[0][1:]] = x[1]

            elif count > 30 : 
                x = line.split(",")
                particle_data.append({constants.FIELDNAMES[0] : x[0],
                                      constants.FIELDNAMES[1] : x[1],
                                      constants.FIELDNAMES[2] : x[2]})
                
    return particle_data, meta_data

def create_directory(directory_name: str):

    #File Paths Naming
    directory_path = constants.MAIN_DIRECTORY_NAME + directory_name
    meta_data_path = directory_path + constants.METADATA_FILE_NAME
    air_quality_path = directory_path + constants.PARTICLE_COUNT_FILE_NAME
    vehicle_tracking_path = directory_path + constants.VEHICLE_TRACKING_FILE_NAME
    cohesive_path = directory_path + constants.COHESIVE_FILE_NAME 

    file_paths = [meta_data_path, air_quality_path, vehicle_tracking_path, cohesive_path]

    # If the overall data directory or specified directory do not exist, create them
    if not os.path.exists(constants.MAIN_DIRECTORY_NAME):
        os.makedirs(constants.MAIN_DIRECTORY_NAME)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # If any of the files dont exist then create them 
    for file_path in file_paths:
        if not os.path.exists(file_path):
            file = open(file_path, "x")
            
    return file_paths
    
    