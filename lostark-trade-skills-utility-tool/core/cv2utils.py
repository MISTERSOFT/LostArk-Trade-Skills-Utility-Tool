import cv2
import numpy as np


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    """
    Resize image
    """

    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def match_template_scale(gray_src_img, gray_template_img, threshold=0.7):
    """
    Search a template in a image by scaling down the template
    """

    # w, h is the current width and height we are currently matching something with in the scale iteration
    w, h = gray_template_img.shape[::-1]
    # matched locations
    locations = []

    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        resized = resize(
            gray_template_img, width=int(gray_template_img.shape[1] * scale)
        )
        w, h = resized.shape[::-1]
        res = cv2.matchTemplate(gray_src_img, resized, cv2.TM_CCOEFF_NORMED)

        locations = np.where(res >= threshold)
        if len(list(zip(*locations[::-1]))) > 0:
            break

    return locations, w, h
