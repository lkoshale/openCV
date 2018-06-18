
import sys
import cv2

def remove_small_rect(w,h,imheight,imwidth):
    area = imheight*imwidth
    if(w*h < 10*(area/100)):
        return True
    elif w*h > 95*(area/100) :
        return True
    else :
        return False



def object_detect(im,fast):
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)

    # resize image
    newHeight = 200
    newWidth = int(im.shape[1] * newHeight / im.shape[0])
    print(newWidth)
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
    display_box = 0

    # itereate over all the region proposals
    for i, rect in enumerate(rects):
        # draw rectangle for region proposal till numShowRects
        if (i < numShowRects):
            x, y, w, h = rect
            if( remove_small_rect(w,h,newHeight,newWidth)):
                pass
            else :
                cv2.rectangle(imOut, (x, y), (x + w, y + h), (0, 255, 0), 1, cv2.LINE_AA)
                display_box+=1
        else:
           break

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

list_img = []
for i in range(1,11):
    name = 'data\image'+str(i)+".jpg"
    list_img.append(name)

# print(list_img)
for name in list_img:
    im = cv2.imread(name)
    cv2.imshow("output",object_detect(im,False))
    cv2.waitKey(0)


# close image show window
cv2.destroyAllWindows()