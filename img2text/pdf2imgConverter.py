
import os
from PIL import Image
from pdf2image import convert_from_path
pages = convert_from_path('pdf1.pdf', 500)

i=0
for page in pages:
    page.save('images/out'+str(i)+'.jpg', 'JPEG')