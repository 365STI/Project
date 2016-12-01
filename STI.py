import sys
import os
import cv2
import math
import numpy as np
from Tkinter import Tk
from tkFileDialog import askopenfilename
from matplotlib import pyplot as plt

def histogram_intersection(h1, h2, bins):
   sm = 0
   for i in range(bins-1):
       for j in range(bins-1):
           sm += min(h1[i][j],h2[i][j])
   return sm

def threshold(S,th):
    if th == 0:
        return S
    if S>th:
        return 255
    else:
        return 0

def isanumber(a):
    bool_a = True
    try:
        bool_a = float(a)
    except:
        bool_a = False
    return bool_a

def getName(file):
    index = -1
    for i in range(len(file)-1,0,-1):
        if file[i]=='.':
            index = i
            break
    return file[0:index]

def findTrans(matrix):
    row, column = matrix.shape
    res = np.array([])
    for i in range(column):
        if np.count_nonzero(matrix[:,i])/float(row) < 0.5:
            res = np.append(res,i)
    return res

def main():
    print "Please select a video file(now only support .avi)..."
    Tk().withdraw()
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)
    fname = getName(str(os.path.basename(filename)))
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
        width  = 64#cap.get(3)
        widthMid = 32#int(width/2)
        height = 64#cap.get(4)
        heightMid = 32#int(height/2)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print "Video Resolution is reduced to: %d x %d" % (width, height)
        print "There are %d frames from video." % frame_count
        S = raw_input("Please select a method to find video transitions:\n A: Copying Pixels\n B: Histogram Differences\n")
        print "Processing..."
        if (S == 'A' or S == 'a'):
            #Copying Pixels
            STI_column = np.zeros((int(height),int(frame_count),3))
            STI_row = np.zeros((int(width),int(frame_count),3))
            i = 0
            while True:
                (rv, im) = cap.read()   # im is a valid image if and only if rv is true
                if not rv:
                    break
                im = cv2.resize(im, (64,64),interpolation = cv2.INTER_CUBIC) # resize to 64*64
                mid_column = im[:,widthMid]
                mid_row = im[heightMid,:]
                STI_column[:,i] = mid_column
                STI_row[:,i] = mid_row
                i=i+1
            extra = "CP"
            cv2.imwrite(fname+'_STI_column_' + extra + '.png',STI_column)
            cv2.imwrite(fname+'_STI_row_' + extra + '.png',STI_row)
            plt.figure(1)
            plt.imshow(STI_column,cmap="gray")
            plt.xticks([]), plt.yticks([])
            plt.title('STI_column')

            plt.figure(2)
            plt.imshow(STI_row,cmap="gray")
            plt.xticks([]), plt.yticks([])
            plt.title('STI_row')
            plt.show(block=False)
            cap.release()
            raw_input("Process complete. Hit any key to exit...")
        elif (S == 'B' or S == 'b'):
            #Histogram differences
            histo = np.zeros((int(frame_count),2,int(height))) #[[x1,x2],[y1,y2]]
            numbins = 1 + math.log(int(height),2)
            bins = np.linspace(0,1,numbins)
            frame = 0
            H_column = np.zeros((int(width),int(frame_count),int(numbins)-1,int(numbins)-1))
            H_row = np.zeros((int(height),int(frame_count),int(numbins)-1,int(numbins)-1))
            STI_column = np.zeros((int(height),int(frame_count)))
            STI_row = np.zeros((int(width),int(frame_count)))
            while True:
                (rv, im) = cap.read()   # im is a valid image if and only if rv is true
                if not rv:
                    break
                im = cv2.resize(im, (64,64),interpolation = cv2.INTER_CUBIC) # resize to 64*64
                #get STI for all columns
                for index in range(int(width)):
                    column = im[:,index]
                    histX = np.zeros(int(height), dtype=np.float)
                    histY = np.zeros(int(height), dtype=np.float)
                    for i in range(int(height)):
                        R,G,B = column[i]
                        RGB = int(R)+int(G)+int(B)
                        if (RGB) != 0:
                            r= R/float(RGB)
                            g= G/float(RGB)
                        else:
                            r = 0
                            g = 0
                        #print str(r) + " " + str(g) + " and the original RGB is: " + str(R) + " " + str(G) + " " + str(B)
                        histX[i] = r
                        histY[i] = g
                    H_column[index][frame], xedges, yedges = np.histogram2d(histX, histY, bins, normed=True)
                #get STI for all rows
                for index in range(int(height)):
                    row = im[index,:]
                    histX = np.zeros(int(width), dtype=np.float)
                    histY = np.zeros(int(width), dtype=np.float)
                    for i in range(int(width)):
                        R,G,B = row[i]
                        RGB = int(R)+int(G)+int(B)
                        if (RGB) != 0:
                            r= R/float(RGB)
                            g= G/float(RGB)
                        else:
                            r = 0
                            g = 0
                        #print str(r) + " " + str(g) + " and the original RGB is: " + str(R) + " " + str(G) + " " + str(B)
                        histX[i] = r
                        histY[i] = g
                    H_row[index][frame], xedges, yedges = np.histogram2d(histX, histY, bins,normed=True )
                frame = frame + 1
            standard = histogram_intersection(H_column[0][0],H_column[0][0],int(numbins))
            p = raw_input("Please enter a threshold percentage(0-100, suggest 70-95): ")
            while isanumber(p):
                p = float(p)
                if (p>=0) and (p<=100):
                    thre = standard * p /100
                else:
                    print "Invalid number, exiting..."
                    return
                for i in range(int(height)):
                    for j in range(int(frame_count)):
                        if j == 0:
                            STI_column[i][j] = threshold(histogram_intersection(H_row[i][j],H_row[i][j],int(numbins)),thre)
                        else:
                            STI_column[i][j] = threshold(histogram_intersection(H_row[i][j],H_row[i][j-1],int(numbins)),thre)
                for i in range(int(width)):
                    for j in range(int(frame_count)):
                        if j == 0:
                            STI_row[i][j] = threshold(histogram_intersection(H_column[i][j],H_column[i][j],int(numbins)),thre)
                        else:
                            STI_row[i][j] = threshold(histogram_intersection(H_column[i][j],H_column[i][j-1],int(numbins)),thre)
                find_column = findTrans(STI_column)
                find_row = findTrans(STI_row)
                extra = "HD_" + str(p)
                cv2.imwrite(fname+'_STI_column_' + extra + '.png',STI_column)
                cv2.imwrite(fname+'_STI_row_' + extra + '.png',STI_row)
                plt.figure(1)
                plt.imshow(STI_column,cmap="gray")
                plt.xticks([]), plt.yticks([])
                plt.title('STI_column')

                plt.figure(2)
                plt.imshow(STI_row,cmap="gray")
                plt.xticks([]), plt.yticks([])
                plt.title('STI_row')
                plt.show(block=False)
                cap.release()
                #if find_column.size != 0:
                print "Here is the frame which contains the transition from column:"
                print find_column
                #if find_row.size != 0:
                print "Here is the frame which contains the transition from row:"
                print find_row
                p = raw_input("Process complete. Enter another number between 0-100 to try another threshold. Or Hit any other key to exit...")
        else:
            print "Invalid option, program ending..."
            return

if __name__ == "__main__":
    main()
