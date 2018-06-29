
import cv2
import numpy as np
import sys
# import pytesseract
import tesserocr as  tess
from PIL import Image
im1 = Image.open("im1.jpg")
import re


sepcific_words=['Auto','Full width','Mobile']
lang_list = ['EN', 'TH', 'JP', 'KR', 'ZH']
font_list = ['Regular','Bold','ltalic']
font_name = ['Dharma Gothic','System Sans Serif Fonts',]

MOBILE = "Mobile"
DESKTOP = "Desktop"
READER = "Reader"

sub_module_names= ['Character limit:','Line Height:','Height:','Width:','Button','Letter Spacing:','Text','Text Align:','BG Color:','Min-Width','Padding:','Left/Right','Desktop/Mobile']
module_names= ['Headline','Image','Text','CTA Button']

output_dict ={}

hex_color = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
# string.isdigit() for checking number

# print( hex_color.match("#fff"))

class OCR :

    # def __init__(self,imagePath,tessdatapath):
    #     self.imagePath = imagePath
    #     self.image = Image.open(imagePath).convert('L')
    #     self.tessDataPath = tessdatapath
    def __init__(self,imagePath):
        self.imagePath =  imagePath
        self.image = Image.open(imagePath).convert('L')
        self.text = " "

    def generate_text_from_image(self):
        text = tess.image_to_text(self.image, lang='eng')
        self.text = text
        return text

    def generate_text_from_file(self,tessDataPath='tessdata-master/'):
        text = tess.file_to_text(self.imagePath, lang='eng', psm=tess.PSM.AUTO, path=tessDataPath)
        self.text = text
        return text

    def parse_text(self):
        note_index = self.text.find('Note:')
        style_index = self.text.find('Style')
        if note_index != -1 and style_index != -1:
            self.text = self.text[style_index:note_index]
        else:
            self.text = None
            print("cant find the values")
            return -1




    def __str__(self):
        return "Parser Object for parsing images"


whole_doc = False

if whole_doc == True:
    images_text=[]
    whole_str= " "
    for i  in range(1,5):
        imagePath = './images/images_pdf1/image ('+str(i)+").jpg"
        parser = OCR(imagePath)
        text = parser.generate_text_from_file()
        images_text.append(text)
        whole_str+=text+"\n\n\n*******************\n\n"

    f = open('output.txt','wb')
    f.write(whole_str.encode('utf-8'))
    f.close()


# config = ('-l eng --oem 1 --psm 3')

# im = cv2.imread('im2.jpg', cv2.IMREAD_COLOR)
# im = Image.open('./images/image (2).jpg').convert('L')
# Run tesseract OCR on image
# api = tess.PyTessBaseAPI('tessdata-master/',lang='eng')


# print(api.GetPageSegMode())
# text = tess.image_to_text(im, lang='eng')
# text = tess.image_to_string(im, config=config)
# pyt.image_to_string(im)

def check_style(line):
    if "Style" in line:
        return True
    else:
        return False

def check_empty(line):
    if not line.strip():
        return True
    else:
        return False

def check_number(line):
    if line.isdigit() :
        return True
    else:
        return False

def check_size(num,size_format):
    if num.isdigit() and size_format.strip()=='px':
        return True
    else:
        return False

def check_font_name(word):
    for fn in font_name:
        if word in fn:
            return True
        else:
            return False


def check_module(word):
    for md in module_names:
        if word in md:
            return True

    return False

def check_sub_module(word):
    for md in sub_module_names:
        if word in md:
            return True

    return False

def extract_char_limit(line):
    pass

def check_langs(line):
    words = line.split(' ')
    for word in words:
        if word in lang_list:
            return True
        else:
            for lang in lang_list:
                if word in lang:
                    return True
            return False



def parse_line(line_list):
    all_lang=[]

    dict_array = []
    # for each line
    flag_top_col_lang=False
    start=1
    if check_langs(line_list[1]):
        start=2
        all_lang = line_list[1].split(' ')

    

    for line in line_list[start:]:
        current_module = ""
        current_sub_module = ""
        i=0
        words=line.split(' ')
        print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False

        temp_dict = {}

        for word in words:
            i+=1
            current_tupple = []

            if flag_escape_next_word:
                flag_escape_next_word = False
                continue

            if flag_escape_next_two_word:
                flag_escape_next_two_word = False
                flag_escape_next_word = True
                continue


            if word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip()!='px' and current_module == 'Headline':
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip()=='px':
                #check before word if its a attribute add else ignore
                pass
            elif word.isdigit() and current_sub_module=='Character limit:':
                # current_tupple.append("")
                # current_tupple.append(word)
                #TODO HARDEST PART
                break

            elif word.isdigit() and current_sub_module =='Line Height:':
                current_tupple.append("Line Height")
                current_tupple.append(word)
            elif hex_color.match(word)!= None:
                current_tupple.append("font_color")
                current_tupple.append(word)
            elif check_module(word) and i < len(words) and not check_module(words[i].strip()):
                current_tupple.append("module_name")
                current_tupple.append(word)
                current_module = word
            elif check_module(word) and i < len(words) and check_module(words[i]):
                current_tupple.append("module_name")
                current_tupple.append(word+" "+words[i])
                current_module = word+ " "+words[i]
            elif check_sub_module(word)and i < len(words) and check_module(words[i]):
                current_sub_module = word+ " "+words[i]
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                #no tupple here
            elif check_font_name(word) and i < len(words) and i+1 < len(words) and check_font_name(words[i]) and check_font_name(words[i+1]):
                current_tupple.append("font_name")
                current_tupple.append(word + " " + words[i]+" "+words[i+1])
                flag_escape_next_two_word = True
            elif check_font_name(word) and i < len(words) and check_font_name(words[i]) :
                current_tupple.append("font_name")
                current_tupple.append(word + " " + words[i] )
                flag_escape_next_word = True
            elif check_font_name(word):
                current_tupple.append("font_name")
                current_tupple.append(word)

            if not current_tupple :
                print("not found any desired object word::: "+word)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe")
                #if already present then add to next lang

            else :
                temp_dict[current_tupple[0]]=current_tupple[1]

        dict_array.append(temp_dict)

    return dict_array




st =""
st.isdigit()
# Print recognized text
text = tess.file_to_text('./images/images_pdf1/image (2).jpg', lang='eng',psm=tess.PSM.AUTO,path='tessdata-master/')
# print(text)
note_index = text.find('Note:')
style_index = text.find('Style')
if note_index!=-1 and style_index!=-1:
    print('string found')
    text = text[style_index:note_index]
    lines=text.split('\n')
    # print(lines)
    print(parse_line(lines[:3]))

