'''
Created on Jan 27, 2018

@author: pope
'''
import csv
import logging
from PIL import Image
from PIL import ImageDraw
import os
import openslide
import cv2
import numpy as np

class HeatMap(object):
    '''
    Classe per disegnare l' heatmap a partire dal csv con le previsioni
    '''

    def __init__(self,csvPathName,name,outPutPath,slideLevel):
        '''
        Constructor
        '''
        self.imgName=name+".ndpi"
        self.pathName=csvPathName
        self.boxList=list()
        self.outPutPath=outPutPath
        self.slideLevel=slideLevel
        with open(self.pathName,'rb') as csvFile:
            csvReader= csv.DictReader(csvFile)
            for row in csvReader :
                name=row["filename"]
                campi=name.split("-")
                logging.debug("cx:%s cy:%s sizex:%s sizeY:%s ",campi[5],campi[7],campi[9],campi[11])
                cf=(float(row["preds0"]),float(row["preds1"]))
                #print cf
                if cf[0]>cf[1]:
                    #perc=int(round(cf[0]*100))
                    perc=cf[0]
                else:
                    #perc=int(round(cf[1]*100))
                    perc=cf[1]
                # cx xy dimx dimy predict percentage
                self.boxList.append((int(campi[5]),int(campi[7]),int(campi[9]),int(campi[11]),row["predict_value"],perc)) 
                
        #print self.boxList
        
        #        (newMax-newMin)(x - min)
        # f(x) = ---------------------  + newMin
        #               max - min

    def normalize(self,x, min, max,newMin,newMax):
        newDelta = newMax - newMin
        oldDelta = max - min
        return int(round((newDelta * (x - min) / oldDelta) + newMin))
    
    def PIL2array(self,img):
        logging.info("converting full slide to numpy array")
        #return np.asarray(img)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        #return np.array(img.getdata(),np.uint8).reshape(img.size[1], img.size[0], 3)

    def makeImg(self):
            
        slide = openslide.OpenSlide(os.path.join(self.imgName))
        nLevel=slide.level_count
        
        level =self.slideLevel
        fullSlideDim = slide.level_dimensions[level]
        fullSlideImg=slide.read_region((0,0), level, (fullSlideDim[0],fullSlideDim[1]))
        
        ###
        #calcolo rescale dei valori
        ###
        
        xmin=0
        ymin=0
        xmax=slide.level_dimensions[0][0]
        ymax=slide.level_dimensions[0][1]
        xnewMin=0
        ynewMin=0
        xnewMax=slide.level_dimensions[level][0]
        ynewMax=slide.level_dimensions[level][1]
        
        #box field # cx xy dimx dimy predict percentage
        boxNumber=0
        
#        pdraw = ImageDraw.Draw(fullSlideImg)
        #poly = Image.new('RGBA', (xnewMax,ynewMax) )
        #pdraw = ImageDraw.Draw(poly)
        #pdraw = np.zeros((fullSlideDim[0],fullSlideDim[1],3), np.uint8)
        pdraw = np.zeros((fullSlideDim[1],fullSlideDim[0],3), np.uint8)
      
        
        for box in self.boxList:
            cx =self.normalize(box[0], xmin, xmax, xnewMin, xnewMax)
            cy = self.normalize(box[1], ymin, ymax, ynewMin, ynewMax)
            sizeX=self.normalize(box[2], xmin, xmax, ynewMin, ynewMax)
            sizeY= self.normalize(box[3], ymin, ymax, ynewMin, ynewMax)
            
            
            poly_size = (sizeX,sizeY)
            poly_offset_cas = (cx,cy) #location in larger image
            poly_offset_cbd = (cx+sizeX,cy+sizeY)
#             poly_size = (sizeY,sizeX)
#             poly_offset_cas = (cy,cx) #location in larger image
#             poly_offset_cbd = (cy+sizeY,cx+sizeX)



            if box[4]=="0.0":
                #print "0000000000000000000"
                #pdraw.rectangle([ (cx,cy), (cx+sizeX,cy+sizeY)],fill=(255,0,0,255))
                logging.debug(str(round(255*float(box[5]))))
                cv2.rectangle(pdraw, poly_offset_cas, poly_offset_cbd, (round(255*float(box[5])),0,0), thickness=-1) 
            else:
                #print "1111111111111111111"
                #pdraw.rectangle([ (cx,cy), (cx+sizeX,cy+sizeY)],fill=(0,0,255,255))
                logging.debug(str(round(255*float(box[5]))))
                cv2.rectangle(pdraw, poly_offset_cas, poly_offset_cbd, (0,0,round(255*float(box[5]))), thickness=-1) 


            logging.debug("pasting box %d",boxNumber)
            boxNumber+=1
 
        #fullSlideImg=Image.blend(fullSlideImg,poly, 0.2 )#mask=poly)   
        #fullSlideImg.save(os.path.join(self.outPutPath,"resultImg.png"))  
        #fullSlideImg= np.array(fullSlideImg)
        fullSlideImg=self.PIL2array(fullSlideImg)
        print fullSlideImg.shape
        print pdraw.shape
        fin = cv2.addWeighted(pdraw, 0.5, fullSlideImg, 0.7, 0)
        logging.info("salvandoImg in " +  os.path.join(self.outPutPath,"resultImg.png") )
        cv2.imwrite(os.path.join(self.outPutPath,"resultImg.png"), fin)  
        
        
        
        
        
        
        
