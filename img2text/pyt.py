
import cv2
import numpy as np
import sys
# import pytesseract
import tesserocr as  tess
from PIL import Image
im1 = Image.open("im1.jpg")

config = ('-l eng --oem 1 --psm 3')
im = cv2.imread('im2.jpg', cv2.IMREAD_COLOR)
# Run tesseract OCR on image
text = tess.image_to_text(Image.open('./im6.jpg').convert('L'), lang='eng')
# text = tess.image_to_string(im, config=config)
# pyt.image_to_string(im)

# Print recognized text
print(text)