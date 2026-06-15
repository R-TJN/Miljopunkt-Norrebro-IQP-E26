import matplotlib.pyplot as plt
import csv

particle_count = []
particle_time = []
seen_plates = [] 

with open('processed_data/1.6.26/AirQualityData.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    first_line = True
    for row in plots:
        if not first_line:
            if not row[2] == 'Invalid\n':
                particle_count.append(int(row[2]))
                particle_time.append(row[1])
        else:
            first_line = False
"""
with open('processed_data/Test1/AirQualityData.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    first_line = True
    for row in plots:
        if not first_line:
            print("doing the thing")
            particleCount.append(int(row[2]))
            time.append(row[1])
        else:
            print("not doing the thing")
            first_line = False
"""

plt.plot(particle_time, particle_count, color = 'g', linestyle = 'dashed',
         marker = '.', ms = 1,  label = "Particles")

plt.xlabel('time')
plt.ylabel('Particle Count')
plt.title('Particle Count at times')
plt.legend()
plt.show()