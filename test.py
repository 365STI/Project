import sys
import cv2
from Tkinter import Tk
from tkFileDialog import askopenfilename
import numpy as np
from matplotlib import pyplot as plt

def main():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)
    if len(filename) < 1:
        print "Error - please select a file."
        return

    cap = cv2.VideoCapture()
    cap.open(filename)

    if not cap.isOpened():
        print "Fatal error - could not open video %s." % filename
        return
    else:
        print "Parsing video %s..." % filename
        width  = cap.get(3)
        widthMid = int(width/2)
        height = cap.get(4)
        heightMid = int(height/2)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        STI_column = np.zeros((height,frame_count,3))
        STI_row = np.zeros((width,frame_count,3))
        print "Video Resolution: %d x %d" % (width, height)
        print "There are %d frames from video." % frame_count

        i = 0
        while True:
            (rv, im) = cap.read()   # im is a valid image if and only if rv is true
            if not rv:
                break
            mid_column = im[:,widthMid]
            mid_row = im[heightMid,:]
            STI_column[:,i] = mid_column
            STI_row[:,i] = mid_row
            i=i+1
            #cv2.imshow('image',im)
            #cv2.waitKey(10)
            #print mid_column
    #cv2.imshow('image',STI)
    cv2.imwrite('STI_column.png',STI_column)
    cv2.imwrite('STI_row.png',STI_row)
    plt.imshow(STI_column)
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
    plt.imshow(STI_row)
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
    cv2.waitKey(100)
    # Do stuff with cap here.
    cap.release()

if __name__ == "__main__":
    main()
