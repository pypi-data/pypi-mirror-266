import imageio
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

def load_image(img_path):
    return imageio.imread(img_path)

def rgb_to_grayscale(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

def invert_image(image):
    return 255 - image

def apply_gaussian_blur(image, sigma=5):
    return gaussian_filter(image, sigma=sigma)

def dodge(blur_img, gray_img):
    resultant_dodge = blur_img * 255 / (255 - gray_img)
    resultant_dodge[resultant_dodge > 255] = 255
    resultant_dodge[gray_img == 255] = 255
    return resultant_dodge.astype('uint8')

def process_image(img_path):
    source_img = load_image(img_path)
    grayscale_img = rgb_to_grayscale(source_img)
    inverted_img = invert_image(grayscale_img)
    blurred_img = apply_gaussian_blur(inverted_img)
    target_img = dodge(blurred_img, grayscale_img)
    return target_img

def display_and_save_image(target_img, save_path='target_image.png'):
    plt.imshow(target_img, cmap="gray")
    plt.imsave(save_path, target_img, cmap='gray', vmin=0, vmax=255)
    plt.show()

if __name__ == "__main__":
    img_path = "C:/Users/shakt/OneDrive/Pictures/Screenshots/Tokyo.png"
    target_img = process_image(img_path)
    display_and_save_image(target_img)
