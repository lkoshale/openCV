
import numpy
import cv2

cv2.setUseOptimized(True)
cv2.setNumThreads(4)

# read image
im = cv2.imread('im1.jpg')

# resize image
newHeight = 200
newWidth = int(im.shape[1] * 200 / im.shape[0])
im = cv2.resize(im, (newWidth, newHeight))

ss = cv2.ximgproc.segmentation.createGraphSegmentation(sigma=0.5)
ss.setK(500)
ss.setMinSize(50)

output = im.copy()

ret = ss.processImage(im)

print(ret)
cv2.imshow('out',output)
cv2.waitKey(0)