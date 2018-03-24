'''
Created on Jan 27, 2018

@author: pope
'''

#made for python 2.7
#
#pip install openslide-python
#pip install matplotlib
#pip install opencv-python
#pip install pillow=4.1.1 (dalla 4.2 da un errore nella conversione a jpeg)
# 
# import openslide
# import cv2
#####
import logging
import sys
from os.path import dirname
sys.path.append("/work/rfalzini/pythonscript/demoTesi")
import argparse
from cropper import Cropper
from MyKerasModel import MyKerasModel
from HeatMap import HeatMap
import os

if __name__ == '__main__':
    ###
    #setting logger
    global logging
    logging.basicConfig(stream= sys.stdout ,format='%(funcName)s %(asctime)s %(levelname)s:%(message)s',level=logging.DEBUG)
    
    ###
    #setting arguments parser
    parser = argparse.ArgumentParser(description='demo tesi')
    parser.add_argument('--out', dest='outPath' , 
                        help='outputh path for the crop',required=True)
    parser.add_argument('--in', dest='inPath' , 
                        help='input path for the crop')
    parser.add_argument('--format', dest='format' , default='.png' ,  
                        help='optional string format')
    parser.add_argument('--nameFile',dest='name',help="name of the slide without extension ",required=True)
    parser.add_argument('--case',dest="case",help="case of slide")
    parser.add_argument('--modelPath',dest="modelPath",help="keras model path",required=True)
    parser.add_argument('--red',dest="red",help="put red crop on special folder",type=bool,default=False)

        
    args = parser.parse_args()
    
    print "Starting DEMO" 
    print args.name
    ############
    #crea i crop dalle annotazioni
    ############
    slide=Cropper(name=args.name,case=args.case,redZone=args.red,minSizeX=500,minSizeY=500,outDirPath=args.outPath)
    slide.readXML()
    slide.makeCrop()
      
    ############
    #calcola lable dei crop dal modello
    ############
    print os.path.join(args.outPath,"crop")
    model=MyKerasModel(modelPath=args.modelPath,outPutPath=args.outPath)
    model.predict(dataDir=os.path.join(args.outPath,"crop"),case=0)
    
    heatMap=HeatMap(csvPathName=os.path.join(args.outPath,"predictionBest.csv"),name=args.name,outPutPath=args.outPath)
    heatMap.makeImg()
    
    print "End DEMO"
