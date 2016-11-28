import sys
import cv2
import numpy as np
from Tkinter import Tk
from tkFileDialog import askopenfilename
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
        print "Fatal error - could not open video %s. Please use avi video files." % filename
        return
    else:
        print "Parsing video %s..." % filename
        width  = cap.get(3)
        widthMid = int(width/2)
        height = cap.get(4)
        heightMid = int(height/2)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print "Video Resolution: %d x %d" % (width, height)
        print "There are %d frames from video." % frame_count
        #Copying Pixels
        S = raw_input("Please select a method to find video transitions:\n A: Copying Pixels\n B: Histogram Differences\n")
        if (S == 'A' or S == 'a'):
            STI_column = np.zeros((int(height),int(frame_count),3))
            STI_row = np.zeros((int(width),int(frame_count),3))
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
        cv2.imwrite('STI_column.png',STI_column)
        cv2.imwrite('STI_row.png',STI_row)
        plt.figure(1)
        plt.imshow(STI_column)
        plt.xticks([]), plt.yticks([])
        plt.title('STI_column')

        plt.figure(2)
        plt.imshow(STI_row)
        plt.xticks([]), plt.yticks([])
        plt.title('STI_row')
        plt.show(block=False)
        cap.release()
        raw_input("Process complete. Hit any key to exit...")

if __name__ == "__main__":
    main()
