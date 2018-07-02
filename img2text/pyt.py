
import cv2
import numpy as np
import sys
# import pytesseract
import tesserocr as  tess
from PIL import Image
im1 = Image.open("im1.jpg")
import re


#Declare constants




sepcific_words=['Auto','Full width','Mobile']
lang_list = ['EN', 'TH', 'JP', 'KR', 'ZH']
font_list = ['Regular','Bold','ltalic']
font_name = ['Dharma Gothic','System Sans Serif Fonts']

MOBILE = "Mobile"
DESKTOP = "Desktop"
READER = "Reader"

sub_module_names= ['character limit:','height:','line height:','width:','button','letter spacing:','text:','text align:','bg color:','min-width','padding:','left/right','desktop/mobile']
module_names= ['Headline','Image','Text','CTA Button']

possible_module_names= ['headline','image','cta button' , 'body text' ,'hero image','cta text link','cta','text text:']

output_dict ={}

hex_color = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
float_regex = re.compile('(^[-+]?([0-9]+)(\.[0-9]+)?)$')
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


#************************CHECK DEFS******************************************

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

    return False


def check_module(word):
    for md in module_names:
        if  md in word:
            return True

    return False

def check_sub_module(word):
    for md in sub_module_names:
        if word.lower() in md:
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


def get_dict_of_lang(dict_array,lang):
    for dict_obj in dict_array:
        if 'lang' in dict_obj:
            if dict_obj['lang']==lang:
                return dict_obj

    return None




#***************************************************************************************#
#                       DEFINATIONS TO PARSE DIFF MODULES


def parse_headline(line_list):
    # print(line_list)

    all_lang = []
    dict_array = []
    start = 0
    current_module = "Headline"
    if check_langs(line_list[0]):
        start = 1
        all_lang = line_list[0].split(' ')
        for ln in all_lang:
            dict_array.append({"lang": ln})

    for line in line_list[start:]:
        all_lang_counter = 0
        current_langs = []
        current_sub_module = ""
        i = 0
        words = line.split(' ')
        # print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False

        temp_dict = {}

        if len(all_lang) > 0 :
            temp_dict = dict_array[all_lang_counter]

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

            if word in lang_list:
                current_langs.append(word)
                continue

            if check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                current_sub_module = word + " " + words[i]
                flag_escape_next_word=True
                continue
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                continue
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() != 'px':
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() == 'px' and current_sub_module == '':
                # check before word if its a attribute add else ignore
                continue
            elif current_sub_module == 'Character limit:':
                # current_tupple.append("")
                # current_tupple.append(word)
                # TODO HARDEST PART
                break
            elif word.isdigit() and current_sub_module == 'Line Height:':
                current_tupple.append("Line Height")
                current_tupple.append(word)
            elif current_sub_module == 'Letter Spacing:' and (float_regex.match(word) or word == 'Auto'):
                current_tupple.append("Letter Spacing")
                current_tupple.append(word)
            elif hex_color.match(word)!= None:
                current_tupple.append("font_color")
                current_tupple.append(word)
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
                # print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe ")# +current_tupple[0]+" "+str(temp_dict) )
                if len(all_lang)>1:
                    all_lang_counter+=1
                    temp_dict = dict_array[all_lang_counter]
                    temp_dict[current_tupple[0]] = current_tupple[1]
                    if 'module_name' not in temp_dict:
                        temp_dict['module_name']= current_module
                else:
                    print("Single lang still repeated key")


                #if already present then add to next lang
            else :
                temp_dict[current_tupple[0]]=current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array



def parse_image(line_list):
    dict_array = []
    current_module = "Image"
    for line in line_list:
        current_sub_module=""
        current_langs = []
        i=0
        words=line.split(' ')
        # print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False
        temp_dict={}

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

            if word in lang_list:
                current_langs.append(word)
                continue

            if check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                current_sub_module = word + " " + words[i]
                flag_escape_next_word=True
                continue
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                continue
            elif current_sub_module != '' and i < len(words) and words[i] == 'px':
                current_tupple.append(current_sub_module)
                current_tupple.append(word + " px")
                flag_escape_next_word = True
            elif current_sub_module != '':
                current_tupple.append(current_sub_module)
                current_tupple.append(word)

            if not current_tupple:
                print("not found any desired object word::: " + word)
                print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe ")  # +current_tupple[0]+" "+str(temp_dict)
                # if already present then add to next lang
            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array


def parse_cta_button(line_list):
    dict_array = []
    current_module = "CTA Button"
    temp_dict = {}
    for line in line_list:

        current_sub_module = ""
        current_langs = []
        i = 0
        words = line.split(' ')
        # print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False

        for word in words:
            i += 1
            current_tupple = []
            if flag_escape_next_word:
                flag_escape_next_word = False
                continue

            if flag_escape_next_two_word:
                flag_escape_next_two_word = False
                flag_escape_next_word = True
                continue

            if word in lang_list:
                current_langs.append(word)
                continue

            lang_split = word.split('-')
            if len(lang_split) > 0:
                if lang_split[0] in lang_list:
                    # extract and add langs specific code
                    current_langs.append(lang_split[0])
                    pass

            if word == 'Text:':
                continue


            if word=='CTA':
                current_tupple.append("module_name")
                current_tupple.append(word+" "+words[i])
                current_module = word+ " "+words[i]
                flag_escape_next_word=True
            elif check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                continue
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() != 'px' :
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() == 'px' and current_sub_module == '':
                # check before word if its a attribute add else ignore
                continue
            elif current_sub_module == 'Character limit:':
                # current_tupple.append("")
                # current_tupple.append(word)
                # TODO HARDEST PART
                break
            elif current_sub_module != '' and i < len(words) and words[i] == 'px':
                current_tupple.append(current_sub_module)
                current_tupple.append(word + " px")
                flag_escape_next_word = True
            elif current_sub_module != '':
                current_tupple.append(current_sub_module)
                current_tupple.append(word)
            elif hex_color.match(word) != None:
                current_tupple.append("font_color")
                current_tupple.append(word)
            elif check_font_name(word) and i < len(words) and i + 1 < len(words) and check_font_name(
                    words[i]) and check_font_name(words[i + 1]):
                current_tupple.append("font_name")
                current_tupple.append(word + " " + words[i] + " " + words[i + 1])
                flag_escape_next_two_word = True
            elif check_font_name(word) and i < len(words) and check_font_name(words[i]):
                current_tupple.append("font_name")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif check_font_name(word):
                current_tupple.append("font_name")
                current_tupple.append(word)

            if not current_tupple:
                print("not found any desired object word::: " + word)
                print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe "+current_tupple[0]+" ")  # +current_tupple[0]+" "+str(temp_dict)

                # if already present then add to next lang
            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array


#TODO text align left
def parse_body_text(line_list):
    dict_array = []
    current_module = "Body Text"
    for line in line_list:
        current_sub_module = ""
        current_langs = []
        i = 0
        words = line.split(' ')
        # print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False
        temp_dict = {}

        for word in words:
            i += 1
            current_tupple = []
            if flag_escape_next_word:
                flag_escape_next_word = False
                continue

            if flag_escape_next_two_word:
                flag_escape_next_two_word = False
                flag_escape_next_word = True
                continue

            if word in lang_list:
                current_langs.append(word)
                continue

            if ',' in word:
                word = word[:len(word)-1]


            if word == 'Body':
                current_tupple.append("module_name")
                current_tupple.append('Body Text')
                flag_escape_next_two_word=True
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                continue
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() != 'px':
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif current_sub_module != '' and i < len(words) and words[i] == 'px':
                current_tupple.append(current_sub_module)
                current_tupple.append(word + " px")
                flag_escape_next_word = True
            elif current_sub_module != '':
                current_tupple.append(current_sub_module)
                current_tupple.append(word)
            elif hex_color.match(word)!= None:
                current_tupple.append("font_color")
                current_tupple.append(word)
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

            if not current_tupple:
                print("not found any desired object word::: " + word)
                print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe " +current_tupple[0]+" "+word)
                # if already present then add to next lang
            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array



#***************************************************************************************#

# config = ('-l eng --oem 1 --psm 3')

# im = cv2.imread('im2.jpg', cv2.IMREAD_COLOR)
# im = Image.open('./images/image (2).jpg').convert('L')
# Run tesseract OCR on image
# api = tess.PyTessBaseAPI('tessdata-master/',lang='eng')


# print(api.GetPageSegMode())
# text = tess.image_to_text(im, lang='eng')
# text = tess.image_to_string(im, config=config)
# pyt.image_to_string(im)

def parse_line(line_list):
    all_lang=[]

    dict_array = []
    # for each line
    flag_top_col_lang=False
    start=1
    if check_langs(line_list[1]):
        start=2
        all_lang = line_list[1].split(' ')
        for ln in all_lang:
            dict_array.append({"lang":ln})


    last_module_name = ''
    for line in line_list[start:]:
        all_lang_counter = 0
        current_langs = []
        current_module = ""
        current_sub_module = ""
        i=0
        words=line.split(' ')
        print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False

        temp_dict = {}

        if  len(all_lang)>0 and last_module_name=='':
            temp_dict = dict_array[all_lang_counter]

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

            if word in lang_list:
                current_langs.append(word)
                continue

            #TODO Check hypen lang
            lang_split = word.split('-')
            if len(lang_split) > 0:
                if lang_split[0] in lang_list:
                    #extract and add langs specific code
                    pass

            if check_module(word) and i < len(words) and check_module(words[i]):
                current_tupple.append("module_name")
                current_tupple.append(word+" "+words[i])
                current_module = word+ " "+words[i]
                last_module_name = current_module
                flag_escape_next_word=True
                temp_dict={}
            elif check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
                current_module = word
                last_module_name = current_module
                if(current_module!='Headline'):
                    temp_dict={}

            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                current_sub_module = word + " " + words[i]
                flag_escape_next_word=True
                continue
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                continue
                # no tupple here
            elif word in font_list and  i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word+" "+words[i])
                flag_escape_next_word=True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip()!='px' and current_module == 'Headline':
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip()=='px' and current_sub_module=='':
                #check before word if its a attribute add else ignore
                continue
            elif word.isdigit() and current_sub_module=='Character limit:':
                # current_tupple.append("")
                # current_tupple.append(word)
                #TODO HARDEST PART
                break

            elif word.isdigit() and current_sub_module =='Line Height:':
                current_tupple.append("Line Height")
                current_tupple.append(word)
            elif  current_sub_module=='Letter Spacing:' and (float_regex.match(word) or word=='Auto'):
                current_tupple.append("Letter Spacing")
                current_tupple.append(word)
            elif current_sub_module != '' and i < len(words) and words[i]=='px':
                current_tupple.append(current_sub_module)
                current_tupple.append(word+" px")
                flag_escape_next_word=True
            elif current_sub_module!='':
                current_tupple.append(current_sub_module)
                current_tupple.append(word)
            elif hex_color.match(word)!= None:
                current_tupple.append("font_color")
                current_tupple.append(word)
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
                print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe ")# +current_tupple[0]+" "+str(temp_dict) )
                if len(all_lang)>1:
                    all_lang_counter+=1
                    temp_dict = dict_array[all_lang_counter]
                    temp_dict[current_tupple[0]] = current_tupple[1]
                    if 'module_name' not in temp_dict:
                        temp_dict['module_name']= current_module
                else:
                    print("Single lang still repeated key")


                #if already present then add to next lang
            else :
                temp_dict[current_tupple[0]]=current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array




def select_call_function(function_name,line_list):
   if function_name=='headline':
      return parse_headline(line_list)
   elif function_name=='body text':
      return parse_body_text(line_list)
   elif function_name =='cta' or function_name=='cta button' or function_name== 'cta text link' :
       return parse_cta_button(line_list)
   elif  function_name== 'image':
       return  parse_image(line_list)
   else:
       return None

def module_name_occurence(line):
    for md in possible_module_names:
        if md in line.lower():
            return md
    return None

def parse_file(text):
    result_array = []
    note_index = text.find('Note:')
    style_index = text.find('Style')
    if note_index != -1 and style_index != -1:
        print('[INFO ] File is getting ready to parsed :')
        text = text[style_index+1:note_index]
        # print(text)
        lines = text.split('\n')

        current_method=''
        index=0
        last_index=-1
        for index in range(0,len(lines)):
           md = module_name_occurence(lines[index])
           if md=='headline':
               current_method=md
               last_index=0
               continue

           if md!=None and last_index>=0:
               md_result = select_call_function(current_method,lines[last_index:index])
               result_array.extend(md_result)
               # print("[INFO] rturned: "+str())
               if current_method=='image':
                   current_method=md
                   last_index=last_index+1
               else:
                  current_method=md
                  last_index=index
           else:
               print("no module : "+lines[index])

           if index==len(lines)-1:
                md_result = select_call_function(current_method, lines[last_index:index])
                result_array.extend(md_result)
                # print("[INFO] rturned: " + str())
    print("[INFO] result:"+str(result_array))










st =""
st.isdigit()
# Print recognized text
# text = tess.file_to_text('./pdf/one_page.pdf', lang='eng',psm=tess.PSM.AUTO,path='tessdata-master/')
text = tess.file_to_text('./images/images_pdf1/image (2).jpg', lang='eng',psm=tess.PSM.AUTO,path='tessdata-master/')
# print(text)
parse_file(text)
# note_index = text.find('Note:')
# style_index = text.find('Style')
# if note_index!=-1 and style_index!=-1:
#     print('string found')
#     text = text[style_index:note_index]
#     # print(text)
#     lines=text.split('\n')
#     # print(lines[12:16])
#     print(parse_body_text(lines[15:16]))

