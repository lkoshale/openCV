
####################
#    INPUT FORMAT
#    ImagePath,category     csv file
#####################


import cv2
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import GradientBoostingClassifier

#resize images and create train dataset


NUM_OF_CAT = 2

def categorise_data(name):
    if(name=='cat'):
        return 1
    elif name == 'dog':
        return 2


def create_image_mat(path_lsit,width,height):
    X = np.array([])
    for path in path_lsit:
        im = cv2.imread(path)
        # resize image
        im = cv2.resize(im, (width, height))
        im = im.flatten()
        X= np.concatenate( (X,im),axis=0)

    return np.reshape(X,[len(path_lsit),width*height*3])


def create_taget_matrix(cat_list):
    Y = np.array([])
    for cat in cat_list:
        Y = np.append(Y,[categorise_data(cat)],axis=0)

    return Y

list_img = []
for i in range(1,5):
    name = 'data\image'+str(i)+".jpg"
    list_img.append(name)

trainX = create_image_mat(list_img,200,200)
trainY = create_taget_matrix(['cat','dog'])

clf = GradientBoostingClassifier(n_estimators=100,learning_rate=0.1)



print(trainY)