<p align="center">
 <img width="600px" src="https://i.postimg.cc/k55JLthG/vdk.jpg" alt="vdk"/>
</p>

# BrightnessBooster
The code enhances an image's brightness and contrast

## Description
### Main functions in library
"""python
beta_parameters_of_image
calculate_brightness_and_contrast_from_parameters
approximate_beta_distribution
modify_brightness_distribution
"""
## How to use
### How to modify image using BrightnessBooster library
```python
import BrightnessBooster as BB
import cv2

#test image
image_path = r"\test_img\test_img_4.jpg"

# load test image use cv2
image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)

# show image
cv2.imshow('Restored Image', image_modified)
cv2.waitKey(0)

a_red_org, b_red_org, a_green_org, b_green_org, a_blue_org, \
b_blue_org = BB.beta_parameters_of_image(image)
print('Betta parameters of original image:')
print(f'a_red = {a_red_org}')
print(f'b_red = {b_red_org}')
print(f'a_red = {a_green_org}')
print(f'b_green = {b_green_org}')
print(f'a_blue = {a_blue_org}')
print(f'b_blue = {a_blue_org}')
beta_parameters_org = (a_red_org, b_red_org, a_green_org, b_green_org, a_blue_org, b_blue_org)
brightness, contrast = BB.calculate_brightness_and_contrast_from_parameters(beta_parameters_org)
print('Brightness and Contrast of original image:')
print(f'Brightness = {brightness}')
print(f'Contrast = {contrast}')

# введем желаемые параметры распределения, например
red_a = 3.1
red_b = 4.3

green_a = 2.7
green_b = 3.3

blue_a = 4.8
blue_b = 3.2

beta_parameters_mod = (red_a, red_b, green_a, green_b, blue_a, blue_b) 
image_modified = BB.modify_brightness_distribution(image, beta_parameters_mod)
height, width = image.shape[:2]
new_height = round((height * 800) / width)
new_width = 800
image_modified = cv2.resize(image_modified, (new_width, new_height))
cv2.imshow('Restored Image', image_modified)
cv2.waitKey(0)

brightness_mod, contrast_mod = BB.calculate_brightness_and_contrast_from_parameters(beta_parameters_mod)
print('Brightness and Contrast of modified image:')
print(f'Brightness = {brightness_mod}')
print(f'Contrast = {contrast_mod}')
```
### How to aproximate data by beta distribution
```python
import BrightnessBooster as BB
import numpy as np

# Задайте параметры распределения
a = 2.0  # Параметр формы (alpha)
b = 5.0  # Параметр формы (beta)
size = 1000  # Размер выборки

# Генерируем выборку из бета-распределения
data = np.random.beta(a, b, size)
a_approx, b_approx = BB.approximate_beta_distribution(data)
print(a_approx, b_approx)
```

## Licence
