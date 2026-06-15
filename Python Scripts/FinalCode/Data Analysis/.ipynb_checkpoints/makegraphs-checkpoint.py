import matplotlib.pyplot as plt
import csv

particleCount = []
time = []

with open('processed_data/Test1/AirQualityData.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    firstLine = True
    for row in plots:
        if not firstLine:
            print("doing the thing")
            particleCount.append(int(row[2]))
            time.append(row[1])
        else:
            print("not doing the thing")
            firstLine = False
print(particleCount)
print(time)

plt.plot(time, particleCount, color = 'g', linestyle = 'dashed',
         marker = '.', ms = 1,  label = "Particles")
plt.xlabel('time')
plt.ylabel('ParticleCount')
plt.title('Particle Count at times')
plt.legend()
plt.show()