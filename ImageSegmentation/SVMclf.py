
####################
#    INPUT FORMAT
#    ImagePath,category     csv file
#####################


import cv2
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import sys
from sklearn.externals import joblib

from sklearn.svm import SVR


#resize images and create train dataset

#read data from csv

df = pd.read_csv('train.csv')
#suffle the data
df = df.sample(frac=1).reset_index(drop=True)
# print(df.info())

name_list = df.path.tolist()
target_list = df.category.tolist()

# trainX,testX,trainY,testY = train_test_split(name_list)

NUM_OF_CAT = 6

def categorise_data(name):
    if name == 'bed' :
        return 100
    elif name == 'food_packet':
        return 200
    elif name == 'plants':
        return 300
    elif name == 'fish_tank':
        return 400
    elif name == 'shampoo':
        return 500
    elif name == 'bowl':
        return 600
    else :
        sys.exit(0)


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

test = True

if test :
    list_img = []

    for i in name_list:
        name = 'data\\'+str(i)
        list_img.append(name)

    X = create_image_mat(list_img,75,75)
    Y = create_taget_matrix(target_list)

    trainX,testX,trainY,testY = train_test_split(X,Y,random_state=42)

    print(trainX.shape)
    print(trainY.shape)

    clf = GradientBoostingRegressor(n_estimators=500,learning_rate=0.03,verbose=True)
    # clf = SVR(gamma=0.001)
    clf.fit(trainX,trainY)


    print(clf.score(testX,testY))


    joblib.dump(clf, 'gbtree.pkl')

    # print(trainY)