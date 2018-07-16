# import pytesseract
import tesserocr as tess
from PIL import Image
import re
import json

# Declare constants
sepcific_words = ['Auto', 'Full width', 'Mobile']
lang_list = ['EN', 'TH', 'JP', 'KR', 'ZH', 'EN:']
font_list = ['Regular', 'Bold', 'ltalic']
font_name = ['Dharma Gothic', 'System Sans Serif Fonts']

MOBILE = "Mobile"
DESKTOP = "Desktop"
READER = "Reader"

sub_module_names = ['character limit:', 'height:', 'line height:', 'width:', 'button', 'letter spacing:', 'text:',
                    'text align:', 'bg color:', 'min-width', 'max-width', 'padding:', 'left/right', 'desktop/mobile']

module_names = ['Headline', 'Image', 'Text', 'CTA Button','Price field text','Subhead','Firstname Lastname','Exclusive Text']

possible_module_names = ['headline','haadline', 'image', 'cta button', 'body text', 'hero image', 'cta text link', 'cta',
                         'text text:', 'text desktop text:', 'background color','background', 'alignment','border color','price field text','subhead','firstname lastname','exclusive text','dividing line']

exclude_module_false = ['(image)']

exclude_sub_module = ['max', 'min', 'limit','char','to','on','ut','et','ut et','ng','desktop']


hex_color = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
float_regex = re.compile('(^[-+]?([0-9]+)(\.[0-9]+)?)$')
alphabet_regex = re.compile('[a-z]')


# string.isdigit() for checking number

# print( hex_color.match("#fff"))

class OCR:

    # def __init__(self,imagePath,tessdatapath):
    #     self.imagePath = imagePath
    #     self.image = Image.open(imagePath).convert('L')
    #     self.tessDataPath = tessdatapath
    def __init__(self, imagePath):
        self.imagePath = imagePath
        self.image = Image.open(imagePath).convert('L')
        self.text = " "

    def generate_text_from_image(self):
        text = tess.image_to_text(self.image, lang='eng')
        self.text = text
        return text

    def generate_text_from_file(self, tessDataPath='tessdata-master/'):
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
    images_text = []
    whole_str = " "
    for i in range(1, 5):
        imagePath = './images/images_pdf1/image (' + str(i) + ").jpg"
        parser = OCR(imagePath)
        text = parser.generate_text_from_file()
        images_text.append(text)
        whole_str += text + "\n\n\n*******************\n\n"

    f = open('output.txt', 'wb')
    f.write(whole_str.encode('utf-8'))
    f.close()


# ************************CHECK DEFS******************************************

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
    if line.isdigit():
        return True
    else:
        return False


def check_size(num, size_format):
    if num.isdigit() and size_format.strip() == 'px':
        return True
    else:
        return False


def check_font_name(word):
    for fn in font_name:
        if word in fn:
            return True

    return False


def check_module(word):
    if word.lower() == "text:":
        return False
    for md in module_names:
        if md.lower() in word.lower():
            return True

    return False


def check_sub_module(word):
    if word.lower() in exclude_sub_module:
        return False

    for md in sub_module_names:
        if word.lower() in md:
            return True

    return False





def check_lang_list(line):
    words = line.split(' ')
    for word in words:
        if not check_langs(word):
            return False
    return True


def check_langs(word):
    if word in lang_list:
        return True
    else:
        for lang in lang_list:
            if word in lang:
                return True
        return False


def get_dict_of_lang(dict_array, lang):
    for dict_obj in dict_array:
        if 'lang' in dict_obj:
            if dict_obj['lang'] == lang:
                return dict_obj

    return None


def check_return_lang_obj(lang, array):
    for d in array:
        if 'lang' in d and d['lang'] == lang:
            return d

    return None


def is_there_2_text(lines):
    textc = 0
    last_index = 0
    for ind in range(0, len(lines)):
        if 'Text:' in lines[ind]:
            textc += 1
            last_index = ind
    if textc > 1:
        return last_index
    else:
        return 0


# ***************************************************************************************#
#                       DEFINATIONS TO PARSE DIFF MODULES


def parse_headline(line_list):
    if len(line_list) == 0:
        return []
    all_lang = []
    dict_array = []
    start = 0
    current_module = "Headline"
    if check_lang_list(line_list[0]):
        start = 1
        all_lang = line_list[0].split(' ')
        for ln in all_lang:
            dict_array.append({"lang": ln})

    for line in line_list[start:]:
        all_lang_counter = 0
        current_langs = []
        current_sub_module = ""

        words = line.split(' ')
        # print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False
        num_of_escapes = 0

        temp_dict = {}

        if len(all_lang) > 0:
            temp_dict = dict_array[all_lang_counter]

        if len(all_lang) == 0 and len(dict_array) > 0:
            temp_dict = dict_array[0]

        i = 0
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

            if num_of_escapes > 0:
                num_of_escapes -= 1
                continue

            if word in lang_list:
                current_langs.append(word)
                continue


            if check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                if len(word) <= 2:
                    continue
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                if len(word) <= 2:
                    continue
                current_sub_module = word
                continue
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                if len(word)<2:
                    continue
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and current_sub_module == 'Line Height:':
                current_tupple.append("Line Height")
                current_tupple.append(word)
            elif current_sub_module.lower() == 'character limit:':
                # TODO HARDEST PART
                # Loop for the line extract till next
                if word.split('-')[0] in lang_list and len(word.split('-')) > 1:
                    dc = check_return_lang_obj(word.split('-')[0], dict_array)
                    if dc != None:
                        dc['Character limit:'] = word.split('-')[1]
                        continue
                elif len(current_langs) > 0 and word.isdigit():
                    for ln in current_langs:
                        if 'lang' in temp_dict and temp_dict['lang'] != '':
                            td = {'lang': ln, 'Character limit:': word}
                            dict_array.append(td)
                        else:
                            temp_dict['lang'] = ln
                            temp_dict['Character limit:'] = word

                    current_langs = []
                else:
                    for ind in range(i - 1, len(words)):
                        if words[ind - 1].isdigit() and ind + 1 < len(words) and words[ind] == 'per':
                            current_tupple.append('Character limit:')
                            current_tupple.append(words[ind - 1])
                        if words[ind] == 'lines':
                            num_of_escapes = 5
                            break

            elif word.isdigit() and i < len(words) and words[i].strip() != 'px' and words[i] != 'per':

                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() == 'px' and current_sub_module == '':
                # check before word if its a attribute add else ignore
                continue

            elif current_sub_module == 'Letter Spacing:' and (float_regex.match(word) or word == 'Auto'):
                current_tupple.append("Letter Spacing")
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
                if len(word) < 2:
                    continue
                current_tupple.append("font_name")
                current_tupple.append(word)
            elif i == len(words) - 1 and len(all_lang) == 0:
                for lng in current_langs:
                    if 'lang' not in temp_dict:
                        temp_dict['lang'] = lng
                    else:
                        print('lang already present')

            if not current_tupple:
                print("not found any desired object word::: " + word + " " + current_sub_module)
                # print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe " + current_tupple[0] + " " + str(temp_dict))
                if len(all_lang) > 1:
                    all_lang_counter += 1
                    temp_dict = dict_array[all_lang_counter]
                    temp_dict[current_tupple[0]] = current_tupple[1]
                    if 'module_name' not in temp_dict:
                        temp_dict['module_name'] = current_module
                elif len(current_langs) >= 1:
                    for ln in current_langs:
                        td = {'lang': ln}
                        dict_array.append(td)
                    temp_dict = dict_array[1]
                    temp_dict[current_tupple[0]] = current_tupple[1]
                    if 'module_name' not in temp_dict:
                        temp_dict['module_name'] = current_module

                else:
                    print("Single lang still repeated key")
            else:
                temp_dict[current_tupple[0]] = current_tupple[1]
                if 'module_name' not in temp_dict:
                    temp_dict['module_name'] = current_module

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    last_dict = {}
    for t_dict in dict_array:
        if 'module_name' in t_dict:
            last_dict = t_dict
        else:
            for key in last_dict.keys():
                if key not in t_dict:
                    t_dict[key] = last_dict[key]

    return dict_array


def parse_image(line_list):
    dict_array = []
    current_module = "Image"
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

            if check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                if len(word) <= 2:
                    continue
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                if len(word) <= 2:
                    continue
                current_sub_module = word
                continue
            elif current_sub_module == '' and word.isdigit() and i < len(words) and words[i] == 'x':
                current_tupple.append('Height')
                current_tupple.append(word)
                flag_escape_next_word = True
            elif current_sub_module == '' and word.isdigit() and words[i - 2] == 'x':
                current_tupple.append('Width')
                current_tupple.append(word)
                flag_escape_next_word = True
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
        # current_langs=[]
        current_sub_module = ""

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
            #
            # if word in lang_list:
            #     current_langs.append(word)
            #     continue
            #
            # lang_split = word.split('-')
            # if len(lang_split) > 0:
            #     if lang_split[0] in lang_list:
            #         # extract and add langs specific code
            #         current_langs.append(lang_split[0])
            #         pass

            if word == 'Text:':
                continue

            if word == 'CTA' and i < len(words):
                current_tupple.append("module_name")
                current_tupple.append(word + " " + words[i])
                current_module = word + " " + words[i]
                flag_escape_next_word = True
            elif check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                if len(word) <= 2:
                    continue
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                if len(word)<=2:
                    continue
                current_sub_module = word
                continue
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() == 'px' and current_sub_module == '':
                # check before word if its a attribute add else ignore
                continue
            elif current_sub_module == 'Character Limit:':
                if word.split('-')[0] in lang_list and len(word.split('-')) > 1:
                    if 'lang' in temp_dict:
                        td = {'lang': word.split('-')[0], "Character Limit": word.split('-')[1]}
                        dict_array.append(td)
                    else:
                        temp_dict['lang'] = word.split('-')[0]
                        temp_dict["Character Limit"] = word.split('-')[1]
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
                print("already present ignoring chenge next lang maybe " + current_tupple[
                    0] + " ")  # +current_tupple[0]+" "+str(temp_dict)

                # # if already present then add to next lang
                # if len(current_langs)>0:
                #     for l in current_langs:
                #         t_d = {}
                #         t_d['lang']=l
                #         t_d[current_tupple[0]]=current_tupple[1].split('-')[1]
                #         dict_array.append(t_d)
                #
                #     current_langs=[] #empty it

            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    last_dict = {}
    for td in dict_array:
        if 'module_name' in td:
            last_dict = td
        else:
            for key in last_dict.keys():
                if key not in td:
                    td[key] = last_dict[key]

    return dict_array


# TODO text align left
def parse_body_text(line_list):
    dict_array = []
    current_module = "Body Text"
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

            if ',' in word:
                word = word[:len(word) - 1]

            if word == 'Body':
                current_tupple.append("module_name")
                current_tupple.append('Body Text')
                flag_escape_next_two_word = True
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                if len(word) <= 2:
                    continue
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                if len(word) <= 2:
                    continue
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
                print("already present ignoring chenge next lang maybe " + current_tupple[0] + " " + word)
                # if already present then add to next lang
            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array


def parse_module_text(line_list):
    dict_array = []
    current_module = "Text"
    temp_dict = {}
    for line in line_list:
        current_langs = []
        current_sub_module = ""

        i = 0
        words = line.split(' ')

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

            if not word.isdigit() and len(word) == 1:
                continue

            if word in lang_list:
                current_langs.append(word)
                continue

            if ',' in word:
                word = word[0:len(word) - 1]

            if word == 'Text:':
                continue

            if word == "Text" and i < len(words) and words[i].lower() == 'desktop':
                current_tupple.append("module_name")
                current_tupple.append(word)
                current_module = word
                flag_escape_next_word = True
            elif word == 'Text':
                current_tupple.append("module_name")
                current_tupple.append(word)
                current_module = word


            elif check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]) and len(word) > 1:
                if len(word) <= 2:
                    continue
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word) and len(word) > 1:
                if len(word) <= 2:
                    continue
                current_sub_module = word
                continue
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif current_sub_module == 'Character Limit:':
                if len(current_langs) > 0 and word.isdigit():
                    for ln in current_langs:
                        if 'lang' in temp_dict and temp_dict['lang'] != "":
                            td = {'lang': ln, 'Character limit:': word}
                            dict_array.append(td)
                        else:
                            temp_dict['lang'] = ln
                            temp_dict['Character limit:'] = word

            elif word.isdigit() and i < len(words) and words[i].strip() != 'px':
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() == 'px' and current_sub_module == '':
                # check before word if its a attribute add else ignore
                continue

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

            if i == len(words) - 1 and 'module_name' not in temp_dict:
                temp_dict['module_name'] = current_module

            if not current_tupple:
                print("not found any desired object word::: " + word)
                print(current_sub_module)
            elif current_tupple[0] in temp_dict:
                print("already present ignoring chenge next lang maybe " + current_tupple[
                    0] + " ")  # +current_tupple[0]+" "+str(temp_dict)

            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    last_dict = {}
    for td in dict_array:
        if 'module_name' in td:
            last_dict = td
        else:
            for key in last_dict.keys():
                if key not in td:
                    td[key] = last_dict[key]

    return dict_array


def parse_backgound_color(line_list):
    dict_array = []
    for line in line_list:

        words = line.split(' ')
        temp_dict = {}
        flag_escape_next_word = False
        for word in words:

            if flag_escape_next_word:
                flag_escape_next_word = False
                continue

            if word.lower() == 'background':
                temp_dict['module_name'] = 'Background Color'
                flag_escape_next_word = True
            elif hex_color.match(word) != None:
                temp_dict['color'] = word
            else:
                print('[INFO} unkown word in background module')

        dict_array.append(temp_dict)

    return dict_array


def parse_alignment(line_list):
    dict_array = []
    for line in line_list:
        words = line.split('\n')
        temp_dict = {}
        i = 0
        for word in words:
            i += 1
            if word.lower == "alignment":
                temp_dict['module_name'] = 'Alignment'
            elif (word.lower == 'desktop/mobile' or word.lower == 'desktop/mobile:') and i < len(words):
                temp_dict['Desktop'] = words[i]
                temp_dict['Mobile'] = words[i]
            elif (word.lower() == 'mobile' or word.lower()=='mobile:') and i < len(words):
                temp_dict['Mobile'] = words[i]
            else:
                print('[WARN} Not able to parse in alignment ' + word)
        dict_array.append(temp_dict)
    return dict_array


def parse_subhead(line_list):
    pass

def parse_firstname(line_list):
    pass


# ***************************************************************************************#

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
    all_lang = []
    dict_array = []
    # for each line
    flag_top_col_lang = False
    start = 1
    if check_langs(line_list[1]):
        start = 2
        all_lang = line_list[1].split(' ')
        for ln in all_lang:
            dict_array.append({"lang": ln})

    last_module_name = ''
    for line in line_list[start:]:
        all_lang_counter = 0
        current_langs = []
        current_module = ""
        current_sub_module = ""
        i = 0
        words = line.split(' ')
        print(words)
        flag_escape_next_word = False
        flag_escape_next_two_word = False

        temp_dict = {}

        if len(all_lang) > 0 and last_module_name == '':
            temp_dict = dict_array[all_lang_counter]

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

            # TODO Check hypen lang
            lang_split = word.split('-')
            if len(lang_split) > 0:
                if lang_split[0] in lang_list:
                    # extract and add langs specific code
                    pass

            if check_module(word) and i < len(words) and check_module(words[i]):
                current_tupple.append("module_name")
                current_tupple.append(word + " " + words[i])
                current_module = word + " " + words[i]
                last_module_name = current_module
                flag_escape_next_word = True
                temp_dict = {}
            elif check_module(word):
                current_tupple.append("module_name")
                current_tupple.append(word)
                current_module = word
                last_module_name = current_module
                if (current_module != 'Headline'):
                    temp_dict = {}

            elif check_sub_module(word) and i < len(words) and check_sub_module(words[i]):
                current_sub_module = word + " " + words[i]
                flag_escape_next_word = True
                continue
                # no tuuple here
            elif check_sub_module(word):
                current_sub_module = word
                continue
                # no tupple here
            elif word in font_list and i < len(words) and words[i] in font_list:
                current_tupple.append("font")
                current_tupple.append(word + " " + words[i])
                flag_escape_next_word = True
            elif word in font_list:
                current_tupple.append("font")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() != 'px' and current_module == 'Headline':
                current_tupple.append("font_size")
                current_tupple.append(word)
            elif word.isdigit() and i < len(words) and words[i].strip() == 'px' and current_sub_module == '':
                # check before word if its a attribute add else ignore
                continue
            elif word.isdigit() and current_sub_module == 'Character limit:':
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
                print("already present ignoring chenge next lang maybe ")  # +current_tupple[0]+" "+str(temp_dict) )
                if len(all_lang) > 1:
                    all_lang_counter += 1
                    temp_dict = dict_array[all_lang_counter]
                    temp_dict[current_tupple[0]] = current_tupple[1]
                    if 'module_name' not in temp_dict:
                        temp_dict['module_name'] = current_module
                else:
                    print("Single lang still repeated key")

                # if already present then add to next lang
            else:
                temp_dict[current_tupple[0]] = current_tupple[1]

        if temp_dict not in dict_array:
            dict_array.append(temp_dict)

    return dict_array

def select_call_function(function_name, line_list):
    if function_name == 'headline':
        return parse_headline(line_list)
    elif function_name == 'body text':
        return parse_body_text(line_list)
    elif function_name == 'cta' or function_name == 'cta button' or function_name == 'cta text link':
        return parse_cta_button(line_list)
    elif function_name == 'image':
        return parse_image(line_list)
    elif function_name == 'text text:' or function_name == 'text desktop text:':
        return parse_module_text(line_list)
    elif function_name == 'background color':
        return parse_backgound_color(line_list)
    elif function_name == 'alignment':
        return parse_alignment(line_list)
    elif function_name == 'subhead':
        return []
    else:
        return []


def module_name_occurence(line):
    for not_md in exclude_module_false:
        if not_md in line.lower():
            return None
    for md in possible_module_names:
        if md in line.lower():
            return md
    return None


def parse_file(text):
    result_array = []
    note_index = text.find('Note')
    style_index = text.find('Style')
    headline_index = text.find('Headline')

    if style_index > headline_index and headline_index!=-1:
        style_index = headline_index-2

    if style_index==-1:
        style_index = text.find('30 px')
        if style_index==-1:
            style_index=1


    if note_index != -1 and style_index != -1:
        print('[INFO ] File is getting ready to parsed :')
        text = text[style_index:note_index]
        print(text)

        lines = text.split('\n')[1:]

        current_method = ''
        last_index = 0
        invoked_methods_list = []
        for index in range(0, len(lines)):
            ln = lines[index]
            md = module_name_occurence(lines[index])
            if md == 'headline':
                current_method = md
                last_index = 0
                continue

            if md != None:
                if current_method == '':
                    current_method = 'headline'
                md_result = select_call_function(current_method, lines[last_index:index])
                result_array.extend(md_result)
                invoked_methods_list.append(current_method)
                # print("[INFO] rturned: "+str())
                if current_method == 'image':
                    current_method = md
                    last_index = last_index + 1
                else:
                    current_method = md
                    last_index = index
            else:
                print("no module : " + lines[index])

            if index == len(lines) - 1:
                # repeat at end means text
                if current_method == 'image' and index - last_index > 1:
                    md_result = select_call_function(current_method, lines[last_index:last_index + 1])
                    result_array.extend(md_result)
                    last_index = last_index + 1
                    invoked_methods_list.append(current_method)

                ind = is_there_2_text(lines[last_index:index])
                if ind > 0:
                    md_result = select_call_function(current_method, lines[last_index:last_index + ind])
                    result_array.extend(md_result)
                    invoked_methods_list.append(current_method)
                    last_index = last_index + ind

                if current_method in invoked_methods_list:
                    current_method = 'text text:'
                md_result = select_call_function(current_method, lines[last_index:index])
                result_array.extend(md_result)
                # print("[INFO] rturned: " + str())
    # print("[INFO] result:"+json.dumps(result_array) )
    updated_result_array =[]
    for dt in result_array:
        if not dt:
            continue
        elif 'module_name' not in dt.keys():
            continue
        else:
            updated_result_array.append(dt)

    return updated_result_array

def getPageName(text):
    line_list = text.split('\n')

    if len(line_list)>5 :
        if line_list[0]=="Confirm your email to start transacting." :
           for i in range(1,6):
               if line_list[i]=='':
                   continue
               elif line_list[i]=='View Online':
                   continue
               else:
                   return line_list[i]

        elif line_list[0].strip()!='':
            return line_list[0]
        else:
            return line_list[1]

    return "NaN"

def write_json_to_file():
    file_path = './images/images_pdf1/'
    f = open('out.json', 'w+')
    write_array=[]
    pageID = 1
    for i in range(2, 60):
        file = file_path + "image (" + str(i) + ").jpg"
        text = tess.file_to_text(file, lang='eng', psm=tess.PSM.AUTO, path='tessdata-master/')
        array =[]
        jsn={}
        try:
         array = parse_file(text)
        except Exception as inst:
            pass
        finally:
            jsn['page_id']=str(pageID)
            pageID+=1
            jsn['page_name']=getPageName(text)
            jsn['page_info'] = array
            write_array.append(jsn)


    f.write(json.dumps(write_array))
    f.close()


def extract_char_limit(lines):
    ln=[]
    ch=[]
    for line in lines:
        words=line.split(' ')
        if len(words) < 3:
            continue

        if words[0].isdigit():
            words=words[1:]
        elif words[1].isdigit():
            words=words[2:]

        if words[-1].lower() == 'Unlimited'.lower() or words[-1].isdigit() or words[-1].lower()=='n/a':
            ln.append(" ".join(words[:len(words)-1]))
            ch.append(words[-1])
        else:
            if len(words) < 3:
                continue
            if check_langs(words[-2]):
                ln.append(" ".join(words[:len(words) - 2]))
                ch.append(words[-2]+" "+words[-1])
            elif check_langs(words[-3]):
                ln.append(" ".join(words[:len(words) - 3]))
                ch.append(words[-3]+" "+words[-1])

    if len(ln)==0:
        return lines,ch
    return ln,ch





def select_method_to_parse(function_name,line_list):

    line_list, max_char = extract_char_limit(line_list)

    print(line_list)
    print(max_char)

    if function_name=='headline'or function_name=='haadline':
        return parse_headline(line_list)
    elif function_name=='image':
        return parse_image(line_list)
    elif function_name == 'body text':
        return parse_body_text(line_list)
    elif function_name == 'cta' or function_name == 'cta button' or function_name == 'cta text link':
        return parse_cta_button(line_list)
    elif function_name == 'image':
        return parse_image(line_list)
    elif function_name == 'text text:' or function_name == 'text desktop text:':
        return parse_module_text(line_list)
    elif function_name == 'background color' or function_name=='background':
        return parse_backgound_color(line_list)
    elif function_name == 'alignment':
        return parse_alignment(line_list)
    elif function_name == 'subhead':
        return []  #TODO
    elif function_name == 'exclusive text':
        return []
    elif function_name== 'dividing line':
        return []

    return []




def parse_file2(text):
    result_array=[]
    lines = text.split('\n')

    last_index=0
    index=0
    last_method = None
    for index in range(0,len(lines)):
        md = module_name_occurence(lines[index])

        if index == len(lines) - 1:
            md_result=select_method_to_parse(last_method, lines[last_index:index])
            result_array.extend(md_result)

        if lines[index].strip()=='' and last_method==None:
            last_index=index+1
            continue

        if 'Style'.lower() in lines[index].lower():
            last_index=index+1
            continue

        if 'desktop/reader &'.lower() in lines[index].lower():
            last_index= index+1
            continue

        if md==None:
            continue

        if md.lower()=='headline' and last_method==None:
           last_method=md
           continue

        if md != None and last_method == None:
            last_method = md
            continue

        if 'cta' in md.lower():
            md_result=select_method_to_parse(last_method, lines[last_index: index])
            result_array.extend(md_result)
            last_method = 'cta'
            last_index=index
            continue

        if md != None and last_method=='cta':
            # for lng in lang_list:
                temp_index=0
                for ls in lines[last_index:index]:
                    ls_ind=0
                    bool_break = False
                    for lang in lang_list:
                        if lang.lower() in ls.lower():
                            temp_index=ls_ind
                            bool_break=True
                            break
                        ls_ind+=1
                    if bool_break:
                        break

                if temp_index==0:
                    temp_index=index
                md_result=select_method_to_parse(last_method,lines[last_index:temp_index])
                result_array.extend(md_result)
                last_index = temp_index



        if md != None:
            md_result=select_method_to_parse(last_method,lines[last_index:index])
            result_array.extend(md_result)
            last_index=index
            last_method=md
            continue
    print(result_array)





# Print recognized text
# text = tess.file_to_text('./pdf/one_page.pdf', lang='eng',psm=tess.PSM.AUTO,path='tessdata-master/')


text = tess.file_to_text('./images/images_pdf3/image (40).jpg', lang='eng', psm=tess.PSM.AUTO, path='tessdata-master/')
print(text)
parse_file2(text)
# print(json.dumps(parse_file(text)))
# write_json_to_file()

# note_index = text.find('Note:')
# style_index = text.find('Style')
# if note_index!=-1 and style_index!=-1:
#     print('string found')
#     text = text[style_index:note_index]
#     # print(text)
#     lines=text.split('\n')
#     # print(lines[12:16])
#     print(parse_body_text(lines[15:16]))
