from scipy import special
import numpy as np
from scipy.optimize import lsq_linear


def calculate_brightness_and_contrast(image):
    blue = image[:,:,0]
    blue = np.concatenate(blue)
    green = image[:,:,1]
    green = np.concatenate(green)
    red = image[:,:,2]
    red = np.concatenate(red)

    red_sorted_indixes = np.argsort(red)
    red_sorted_values = red[red_sorted_indixes]

    green_sorted_indixes = np.argsort(green)
    green_sorted_values = green[green_sorted_indixes]

    blue_sorted_indixes = np.argsort(blue)
    blue_sorted_values = blue[blue_sorted_indixes]

    norm_sorted_red_values = red_sorted_values / 255
    norm_sorted_green_values = green_sorted_values / 255
    norm_sorted_blue_values = blue_sorted_values / 255


    red_mean = np.mean(norm_sorted_red_values)
    red_variance = np.var(norm_sorted_red_values)
    #red_variance = red_variance ** 2

    green_mean = np.mean(norm_sorted_green_values)
    green_variance = np.var(norm_sorted_green_values)
    #green_variance = green_variance ** 2

    blue_mean = np.mean(norm_sorted_blue_values)
    blue_variance = np.var(norm_sorted_blue_values)
    #blue_variance = blue_variance ** 2

    brightness = 0.299 * red_mean + 0.587 * green_mean + 0.114 * blue_mean
    contrast = 0.299 * red_variance + 0.587 * green_variance + 0.114 * blue_variance

    brightness_perc = 100 * brightness
    brightness_perc = round(brightness_perc)
    contrast = 4*contrast
    contrast_perc = 100 * contrast
    contrast_perc = round(contrast_perc)

    return [brightness, brightness_perc, contrast, contrast_perc, red, green, blue, red_sorted_indixes, green_sorted_indixes,\
             blue_sorted_indixes, red_mean, red_variance, green_mean, green_variance, blue_mean, blue_variance]



def calculate_beta_parameters(mean, variance):
        u = mean
        s = variance

        a = ((u*u) - (u*u*u) - (u * s)) / s
        b = ((u*u*u) - (2 * (u*u)) + u + (u - 1) * s) / s

        return [a, b]
        

def beta_parameters_of_image(image):
    
    blue = image[:,:,0]
    blue = np.concatenate(blue)
    green = image[:,:,1]
    green = np.concatenate(green)
    red = image[:,:,2]
    red = np.concatenate(red)

    red_sorted_indixes = np.argsort(red)
    red_sorted_values = red[red_sorted_indixes]

    green_sorted_indixes = np.argsort(green)
    green_sorted_values = green[green_sorted_indixes]

    blue_sorted_indixes = np.argsort(blue)
    blue_sorted_values = blue[blue_sorted_indixes]

    norm_sorted_red_values = red_sorted_values / 255
    norm_sorted_green_values = green_sorted_values / 255
    norm_sorted_blue_values = blue_sorted_values / 255


    red_mean = np.mean(norm_sorted_red_values)
    red_variance = np.var(norm_sorted_red_values)
    red_variance = red_variance * red_variance

    green_mean = np.mean(norm_sorted_green_values)
    green_variance = np.var(norm_sorted_green_values)
    green_variance = green_variance * green_variance

    blue_mean = np.mean(norm_sorted_blue_values)
    blue_variance = np.var(norm_sorted_blue_values)
    blue_variance = blue_variance * blue_variance

    red_a, red_b = calculate_beta_parameters(red_mean, red_variance)
    green_a, green_b = calculate_beta_parameters(green_mean, green_variance)
    blue_a, blue_b = calculate_beta_parameters(blue_mean, blue_variance)

    return red_a, red_b, green_a, green_b, blue_a, blue_b

def modify_brightness_distribution(image_org, distribution_parameter):
    red_a, red_b, green_a, green_b, blue_a, blue_b = distribution_parameter
    # red, red_sorted_indixes, green_sorted_indixes, blue_sorted_indixes, height, width = distribution_parameter
    # lenght = len(red)
    blue = image_org[:,:,0]
    blue = np.concatenate(blue)
    green = image_org[:,:,1]
    green = np.concatenate(green)
    red = image_org[:,:,2]
    red = np.concatenate(red)

    # сортируем индексы по значениям для будущего возвращения измененных значений в изначальный порядок
    red_sorted_indixes = np.argsort(red)
    # red_sorted_values = red[red_sorted_indixes]

    green_sorted_indixes = np.argsort(green)
    # green_sorted_values = green[green_sorted_indixes]

    blue_sorted_indixes = np.argsort(blue)
    # blue_sorted_values = blue[blue_sorted_indixes]

    height, width = image_org.shape[:2]

    lenght = len(red)


    x_org = np.linspace(0, 1, lenght)
    Ry_fit = special.betainc(red_a, red_b, x_org)
    Gy_fit = special.betainc(green_a, green_b, x_org)
    By_fit = special.betainc(blue_a, blue_b, x_org)

    Ry_fit = Ry_fit * lenght
    Gy_fit = Gy_fit * lenght
    By_fit = By_fit * lenght

    x_org = x_org * 255

    r_x = Ry_fit
    g_x = Gy_fit
    b_x = By_fit
    Ry_fit = Gy_fit = By_fit = x_org

    x_interp = np.arange(0, lenght)
    red_interpolated_values = np.interp(x_interp, r_x, Ry_fit)
    green_interpolated_values = np.interp(x_interp, g_x, Gy_fit)
    blue_interpolated_values = np.interp(x_interp, b_x, By_fit)

    x = np.arange(0, len(red), 1)
    red_interpolated_values = np.rint(red_interpolated_values)
    green_interpolated_values = np.rint(green_interpolated_values)
    blue_interpolated_values = np.rint(blue_interpolated_values)

    order_red_values = red_interpolated_values[red_sorted_indixes.argsort()]
    order_green_values = green_interpolated_values[green_sorted_indixes.argsort()]
    order_blue_values = blue_interpolated_values[blue_sorted_indixes.argsort()]

    # Восстановите вытянутые векторы каналов обратно в матрицу изображения
    restored_image = np.zeros((height, width, 3), dtype=np.uint8)
    restored_image[:, :, 2] = order_red_values.reshape((height, width))
    restored_image[:, :, 1] = order_green_values.reshape((height, width))
    restored_image[:, :, 0] = order_blue_values.reshape((height, width))

    return restored_image


def max_contrast_at_brightness(Y_user):
    Y_user = Y_user / 100
    return (1 - Y_user) * Y_user


def check_values(mean, variance):
    if mean >= 1 or mean <= 0:
         return False
    if mean >= 0 and variance >= mean:
        return True


def RGB_var(R1,G1,B1,dC,Rm,Gm,Bm):
    r, g, b =  0.299, 0.587, 0.114
  # Создайте коэффициенты матрицы A и вектора b для системы уравнений Ax = b
    A = [
        [r, g, b],
        [G1, -R1, 0],
        [0, B1, -G1],
        [B1, 0, -R1]
    ]
    b1 = dC + r*R1 + g*G1 + b*B1
    b = [b1, 0, 0, 0]

  # Создайте границы для всех переменных в одном кортеже
    lower_bounds = [0, 0, 0]  # Example lower bounds for three parameters
    upper_bounds = [Rm*(1-Rm), Gm*(1-Gm), Bm*(1-Bm)]    # Example upper bounds for three parameters

  # Create a Bounds object
    bounds = (lower_bounds, upper_bounds)


  # Решите систему уравнений с граничными условиями
    result = lsq_linear(A, b, bounds=bounds)

  # Выведите результат
    # print("Решение (x, y, z):", result.x)
    # print("Остаточные ошибки:", result.fun)
    return result.x


def calculate_mean_and_variance_for_color(a, b):
    mean = a / (a + b)
    variance = (a * b) / ((a + b)**2 * (a + b + 1))

    return [mean, variance]


def calculate_brightness_and_contrast_from_parameters(distribution_parameter):
    red_a, red_b, green_a, green_b, blue_a, blue_b = distribution_parameter

    red_mean, red_variance = calculate_mean_and_variance_for_color(red_a, red_b)
    green_mean, green_variance = calculate_mean_and_variance_for_color(green_a, green_b)
    blue_mean, blue_variance = calculate_mean_and_variance_for_color(blue_a, blue_b)

    brightness = 0.299 * red_mean + 0.587 * green_mean + 0.114 * blue_mean
    contrast = 0.299 * red_variance + 0.587 * green_variance + 0.114 * blue_variance

    return [brightness, contrast]


def RGB_mean(R1,G1,B1,dY):
    r, g, b =  0.299, 0.587, 0.114
    # Создайте коэффициенты матрицы A и вектора b для системы уравнений Ax = b
    A = [
        [r, g, b],
        [G1, -R1, 0],
        [0, B1, -G1],
        [B1, 0, -R1]
    ]
    b1 = dY + r*R1 + g*G1 + b*B1
    b = [b1, 0, 0, 0]

    # Создайте границы для всех переменных в одном кортеже

    # Решите систему уравнений с граничными условиями
    result = lsq_linear(A, b, bounds=(0,1))

    # Выведите результат
    # print("Решение (x, y, z):", result.x)
    # print("Остаточные ошибки:", result.fun)
    return result.x


def approximate_beta_distribution(data):

    sorted_indixes = np.argsort(data)
    sorted_values = data[sorted_indixes]

    norm_sorted_values = sorted_values / 255


    mean = np.mean(norm_sorted_values)
    variance = np.var(norm_sorted_values)
    variance = variance * variance

    a, b = calculate_beta_parameters(mean, variance)

    return [a, b]