import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Read the PNG image
image_path = 'your_image.png'
image = Image.open(image_path)

# Convert image to grayscale
image_gray = image.convert('L')

# Get dimensions of the image
width, height = image_gray.size

# Define grid spacing (can be adaptive)
grid_spacing = 10  # Initial grid spacing
fine_spacing = 5   # Grid spacing around color boundaries

# Generate grid points with adaptive spacing
x, y = np.meshgrid(np.arange(0, width, grid_spacing),
                   np.arange(0, height, grid_spacing))

# Identify regions with color boundaries (example)
# This can be done using image processing techniques like edge detection
# Here, we'll just create a simple example with a horizontal color boundary
color_boundary = np.zeros((height, width))
color_boundary[:, width // 2] = 255

# Adjust grid spacing around color boundaries
x_color, y_color = np.where(color_boundary > 0)
for xc, yc in zip(x_color, y_color):
    # Determine the number of grid points on either side of the boundary
    num_points = 2 * grid_spacing // fine_spacing
    
    # Generate additional grid points around the boundary
    x = np.append(x, np.linspace(xc - num_points * fine_spacing, 
                                 xc + num_points * fine_spacing, 
                                 num_points * 2 + 1))
    y = np.append(y, np.linspace(yc - num_points * fine_spacing, 
                                 yc + num_points * fine_spacing, 
                                 num_points * 2 + 1))

# Generate mesh elements (quadrilaterals)
mesh_elements = []
for i in range(len(x) - 1):
    for j in range(len(y) - 1):
        # Define quadrilateral vertices
        v1 = (x[i], y[j])
        v2 = (x[i+1], y[j])
        v3 = (x[i+1], y[j+1])
        v4 = (x[i], y[j+1])
        # Append vertices to mesh elements
        mesh_elements.append([v1, v2, v3, v4])

# Visualize the mesh overlaid on the image
plt.imshow(image_gray, cmap='gray')
for element in mesh_elements:
    element.append(element[0])  # Close the polygon
    xs, ys = zip(*element)
    plt.plot(xs, ys, color='red')
plt.show()
