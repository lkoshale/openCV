
# import the necessary packages
from collections import namedtuple
from skimage.filters import threshold_local
from skimage import segmentation
from skimage import measure
from imutils import perspective
import numpy as np
import imutils
import cv2

def detectCharacterCandidates(image, region):
    # apply a 4-point transform to extract the license plate
    plate = perspective.four_point_transform(image, region)
    cv2.imshow("Perspective Transform", imutils.resize(plate, width=400))
    # extract the Value component from the HSV color space and apply adaptive thresholding
    # to reveal the characters on the license plate
    V = cv2.split(cv2.cvtColor(plate, cv2.COLOR_BGR2HSV))[2]
    T = threshold_local(V, 29, offset=15, method="gaussian")
    print(V>T)
    thresh = (V > T).astype("uint8") * 255
    thresh = cv2.bitwise_not(thresh)

    # resize the license plate region to a canonical size
    plate = imutils.resize(plate, width=400)
    thresh = imutils.resize(thresh, width=400)
    cv2.imshow("Thresh", thresh)