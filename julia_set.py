import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm #color map

#width = 300
#height = 150
width = int(input("Enter screen width: "))
height = int(input("Enter screen height: "))
c = complex(float(input("Enter the real part: ")),float(input("Enter the imaginary part: ")))
#c = complex(-0.1, 0.65)
max_iterations = 100

min_x = -1.5
max_x =  2
width_x = max_x - min_x

min_y = -1.5
max_y =  2
height_y = max_y - min_y

tab = np.zeros((width,height))

for x in range(width):
    for y in range(height):
        z = complex(x / width * width_x + min_x, y / height * height_y + min_y)
        i = 0
        while abs(z) <= 2 and i < max_iterations:
            z = z**2 + c
            i = i + 1
        scale = i / max_iterations
        tab[x,y] = scale

temp, plot = plt.subplots()
plot.imshow(tab, cmap=cm.bone)
plt.show()