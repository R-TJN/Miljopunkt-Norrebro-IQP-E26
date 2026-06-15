import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import csv
import constants 
directory_name = "1.6.26/" 
particle_count_path = constants.MAIN_DIRECTORY_NAME + directory_name + constants.PARTICLE_COUNT_FILE_NAME
vehicle_data_path = constants.MAIN_DIRECTORY_NAME + directory_name + constants.VEHICLE_TRACKING_FILE_NAME

particle_count = []
particle_time = []
vehicle_time = []
seen_plates = []
plate_representation = [] 

with open(particle_count_path,'r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    first_line = True
    for row in plots:
        if not first_line:
            if not row[2] == 'Invalid\n':
                particle_count.append(int(row[2]))
                particle_time.append(row[1])
        else:
            first_line = False

with open(vehicle_data_path,'r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    first_line = True
    for row in plots:
        if not first_line:
            if not row[2] == None and not row[2] in seen_plates:
                seen_plates.append(row[2])
                plate_representation.append(8000)
                vehicle_time.append(row[1])
        else:
            first_line = False
print(seen_plates)
print(vehicle_time)

fig, ax = plt.subplots()


myFmt = mdates.DateFormatter("%H:%M")
ax.xaxis.set_major_formatter(myFmt)

ax.plot(particle_time, particle_count, color = 'g',
         marker = '.', ms = 1,  label = "Particles")
ax.scatter(vehicle_time, plate_representation, color = 'b')

ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax.tick_params("x", rotation=45)
plt.xlabel('time')
plt.ylabel('Particle Count')
plt.title('Particle Count at times')
plt.legend()
plt.show()