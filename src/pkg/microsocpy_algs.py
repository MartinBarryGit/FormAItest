
import cv2
from skimage.filters import threshold_otsu


def vizu_image(img_path, scaling=20):
    rgb = cv2.imread(img_path)
    ## multiply the image by scling factor and clip to 255
    rgb = cv2.convertScaleAbs(rgb, alpha=scaling / 100)
    gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    black = rgb * 0
    if "dapi" in img_path:
        return gray
    elif "red" in img_path:
        black[:,:,0] = gray
        return black
    elif "green" in img_path:
        black[:,:,1] = gray
        return black
def otsu_threshold(img_path, scaling=20):
    if type(img_path) == str:
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    else:
        image = None
        for path in img_path:
            image = cv2.convertScaleAbs(cv2.imread(path, cv2.IMREAD_GRAYSCALE), alpha=scaling / 100) / 255 if image is None else image * (cv2.convertScaleAbs(cv2.imread(path, cv2.IMREAD_GRAYSCALE), alpha=scaling / 100) / 255)
        image = (image * 255).astype('uint8')
        thresh_val = threshold_otsu(image)
        binary = 255 * (image > thresh_val)
        return binary.astype('uint8')
    image = cv2.convertScaleAbs(image, alpha=scaling / 100)
    thresh_val = threshold_otsu(image)
    binary = 255 * (image > thresh_val)
    return binary.astype('uint8')