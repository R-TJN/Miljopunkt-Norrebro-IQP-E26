import os
import csv 

def load_trakpro_data(path: str):
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
    # if the overall data directory does not exist, create it
    if not os.path.exists("./processed_data"):
        os.makedirs("./processed_data")

    if not os.path.exists("./processed_data" + directory_name):
        os.makedirs("./processed_data/" + directory_name)

def create_csv(directory_name: str): 
    
    