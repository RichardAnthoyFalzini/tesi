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

class HeatMap(object):
    '''
    Classe per disegnare l' heatmap a partire dal csv con le previsioni
    '''

    def __init__(self,csvPathName,name,outPutPath):
        '''
        Constructor
        '''
        self.imgName=name+".ndpi"
        self.pathName=csvPathName
        self.boxList=list()
        self.outPutPath=outPutPath
        with open(self.pathName,'rb') as csvFile:
            csvReader= csv.DictReader(csvFile)
            for row in csvReader :
                name=row["filename"]
                campi=name.split("-")
                logging.debug("cx:%s cy:%s sizex:%s sizeY:%s ",campi[5],campi[7],campi[9],campi[11])
                cf=(float(row["preds0"]),float(row["preds1"]))
                #print cf
                if cf[0]>cf[1]:
                    perc=int(round(cf[0]*100))
                else:
                    perc=int(round(cf[1]*100))
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

    def makeImg(self):
            
        slide = openslide.OpenSlide(os.path.join(self.imgName))
        nLevel=slide.level_count
        
        level =3
        fullSlideDim = slide.level_dimensions[level]
        fullSlideImg=slide.read_region((0,0), level, fullSlideDim)
        
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
        poly = Image.new('RGBA', (xnewMax,ynewMax) )
        pdraw = ImageDraw.Draw(poly)
        for box in self.boxList:
            cx =self.normalize(box[0], xmin, xmax, xnewMin, xnewMax)
            cy = self.normalize(box[1], ymin, ymax, ynewMin, ynewMax)
            sizeX=self.normalize(box[2], xmin, xmax, ynewMin, ynewMax)
            sizeY= self.normalize(box[3], ymin, ymax, ynewMin, ynewMax)
            poly_size = (sizeX,sizeY)
            poly_offset = (cx,cy) #location in larger image
            #back = Image.new('RGBA', img_size, (255,0,0,0) )
#             poly = Image.new('RGBA', poly_size )
#             pdraw = ImageDraw.Draw(poly)
#             pdraw.rectangle([ (0,0), (sizeX,sizeY)], 
#                           fill=(255,255,255,127), )#outline=(255,255,255,255))
#             fullSlideImg.blend(poly, poly_offset, )#mask=poly)
#             
#             pdraw.rectangle([ (cx,cy), (cx+sizeX,cy+sizeY)],
#                              fill=(255,0,0,127))
#             pdraw.rectangle([ (0,0), (sizeX,sizeY)], 
#                          fill=(255,0,0,256), )#outline=(255,255,255,255))
            print box[4]
            if box[4]=="0.0":
                print "0000000000000000000"
                pdraw.rectangle([ (cx,cy), (cx+sizeX,cy+sizeY)],
                                 fill=(255,0,0,255))
            else:
                print "1111111111111111111"
                pdraw.rectangle([ (cx,cy), (cx+sizeX,cy+sizeY)],
                                 fill=(0,0,255,255))
                

            logging.debug("pasting box %d",boxNumber)
            boxNumber+=1
            
        fullSlideImg=Image.blend(fullSlideImg,poly, 0.2 )#mask=poly)
            
        fullSlideImg.save(os.path.join(self.outPutPath,"resultImg.png"))     
        
        
        
        
        
        
        
