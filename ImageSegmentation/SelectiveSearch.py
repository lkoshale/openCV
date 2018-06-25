
import sys
import cv2
from sklearn.externals import joblib
import numpy as np
import math

clf = joblib.load('gbtree.pkl')

total=0
ls_box = []

def remove_small_rect(w,h,imheight,imwidth):
    area = imheight*imwidth
    if w*h < 10*(area/100) :
        return True
    elif w*h > 95*(area/100) :
        return True
    else :
        return False


remove_internal_box = True

def check_boxes(list_boxes):
    ls_box.clear()
    for j in range(0,len(list_boxes)):
        # print("im infor1")
        (x1, y1, w1, h1)= list_boxes[j]
        for i in range(j+1,len(list_boxes)):
            (x2, y2, w2, h2) = list_boxes[i]
            # print(math.fabs(w1*h1 - w2*h2))

            if remove_internal_box:
                if (x1 < x2 and x1 + w1 > x2 + w2 and y1 < y2 and y1 + h1 > y2 + h2):
                    if (x2, y2, w2, h2) not in ls_box:
                        ls_box.append((x2, y2, w2, h2))

            if math.fabs(w1*h1 - w2*h2) < 1000 and math.fabs(x1-x2)<30 and math.fabs(y2-y1)<30 :
                # print("im at if")
                if (x1,y1,w1,h1) not in ls_box:
                    ls_box.append((x1,y1,w1,h1))
                    # print("im at append")
            else:
                continue
    return ls_box

def object_detect(im,fast):
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)

    # resize image
    newHeight = 250
    newWidth = int(im.shape[1] * newHeight / im.shape[0])
    # print(newWidth)
    im = cv2.resize(im, (newWidth, newHeight))

    # create Selective Search Segmentation Object using default parameters
    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()

    # set input image on which we will run segmentation
    ss.setBaseImage(im)

    if (fast):
        ss.switchToSelectiveSearchFast()
        # Switch to high recall but slow Selective Search method
    else:
        ss.switchToSelectiveSearchQuality()

    rects = ss.process()
    print('Total Number of Region Proposals: {}'.format(len(rects)))

    # number of region proposals to show
    numShowRects = 30
    # increment to increase/decrease total number
    # of reason proposals to be shown
    increment = 50


    imOut = im.copy()
    imCrop = im.copy()
    display_box = 0

    clf_enable = False
    enable_crop_save = True

    list_boxes = []
    # itereate over all the region proposals
    for i, rect in enumerate(rects):
        # draw rectangle for region proposal till numShowRects
        if (i < numShowRects):
            x, y, w, h = rect
            if (remove_small_rect(w, h, newHeight, newWidth)):
                pass
            else:
                list_boxes.append((x,y,w,h))
        else:
            break

    print("before {} : {}".format(len(list_boxes),list_boxes))
    list_boxes=check_boxes(list_boxes)
    print("after {} : {}".format(len(list_boxes),list_boxes))

    # itereate over all the region proposals
    for i, rect in enumerate(rects):
        # draw rectangle for region proposal till numShowRects
        if (i < numShowRects):
            x, y, w, h = rect
            if( remove_small_rect(w,h,newHeight,newWidth)):
                pass
            else :
                if clf_enable:
                    classify(imOut[y:y+h,x:x+w])

                if (x,y,w,h) in list_boxes:
                    continue
                cv2.rectangle(imOut, (x, y), (x + w, y + h), (0, 255, 0), 1, cv2.LINE_AA)
                display_box+=1
                if enable_crop_save:
                    name = "cropimg" + str(display_box) + ".jpg"
                    cv2.imwrite(name, imCrop[y:y + h, x:x + w])
        else:
           break


    print("{} boxes".format(display_box))
    return imOut


    # # show output
    # cv2.imshow("Output", imOut)
    # print(display_box)
    #
    # # record key press
    # k = cv2.waitKey(0) & 0xFF
    #
    # # m is pressed
    # if k == 109:
    #     # increase total number of rectangles to show by increment
    #     numShowRects += increment
    # # l is pressed
    # elif k == 108 and numShowRects > increment:
    #     # decrease total number of rectangles to show by increment
    #     numShowRects -= increment
    # # q is pressed
    # elif k == 113:
    #     break
    #

#
# def try_to_classify(img,list_boxes):
#     test = np.array([])
#     for (x,y,w,h) in list_boxes:
#         im_new = img[y:y+h,x:x+w]
#         im_new = cv2.resize(im_new,(75,75))
#         np.concatenate((test,im_new.flatten()),axis=0)
#
#     test = np.reshape(test, [len(list_boxes),75*75*3])
#     print()
#     cv2.imshow("crop", im_new)
#     cv2.waitKey(0)

def classify(img):
    img_copy = img.copy()
    img = cv2.resize(img,(75,75))
    img = img.flatten()
    print(clf.predict(np.reshape(img,[1,img.shape[0]])))
    cv2.imshow("crop",img_copy)
    cv2.waitKey(0)


list_img = []
for i in range(15,30):
    name = 'data\image ('+str(i)+").jpg"
    list_img.append(name)

# print(list_img)
for name in list_img:
    im = cv2.imread(name)
    cv2.imshow("output",object_detect(im,False))
    cv2.waitKey(0)


# close image show window
cv2.destroyAllWindows()