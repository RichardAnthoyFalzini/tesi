'''
Created on Jan 27, 2018

@author: pope
'''
import logging
import os

import xml.dom.minidom
import openslide
import cv2

class Cropper(object):
    '''
    Classe per creare crop da file xml e img formato ndpi compatible
    '''


    def __init__(self, name ,case=None,redZone=False,minSizeX=500,minSizeY=500,outDirPath=None):
        '''
        Constructor
        pathToXML
        pathToImg
        '''
        self.xmlName =  str(name)+".xml"
        self.imgName = str(name)+".ndpi" 
        self.name=os.path.basename(name)
        self.zoneList= list()
        self.redZoneList=list()
        self.case = case
        self.redZone=redZone
        self.minSizeY=minSizeY
        self.minSizeX=minSizeX
        self.cropFormat=".png"
        self.listOfSize=[(500,500),(1000,1000)]
        self.cropNum=None
        if outDirPath is None:
            self.outDirPath="/tmp/demoTesi/"+self.name
        else:
            self.outDirPath=outDirPath
            
        if (not os.path.isfile(os.path.join(self.xmlName)) or not os.path.isfile(os.path.join(self.imgName))) :
            print os.path.join(self.imgName)
            print os.path.join(self.xmlName)
            logging.critical("error on Cropper custractor name of img or xml not exist")

    def readXML(self):
        '''
        read the xml and generate the zone list 
        return the number of region found
        '''
        ###
        # open xml file with hand crafted interest area
        
        # Open XML document using minidom parser
        DOMTree = xml.dom.minidom.parse(os.path.join(self.xmlName))
        annotations = DOMTree.documentElement
        annotation = annotations.getElementsByTagName("Annotation")
        
        regionsList=list()
        redregionsList=list()
        
        logging.debug("annotation found :%d",len(annotation))
        for an in annotation:
            regionsBlock = an.getElementsByTagName("Regions")[0]
            regions = regionsBlock.getElementsByTagName("Region")
            logging.debug("regiones found :%d",len(regions))
            for rn in regions:
                #logging.debug("red state %s color attribute %s",args.red,an.getAttribute("LineColor"))
                
                areaid = rn.getAttribute("Id")
                ###4 cordinate xy

                vertices=rn.getElementsByTagName("Vertices")[0]
                vertex=vertices.getElementsByTagName("Vertex")
                
                if len(vertex)==4:
                    x= int(round(float(vertex[0].getAttribute("X"))))
                    y= int(round(float(vertex[0].getAttribute("Y"))))
                    areax=  int(round(float(vertex[1].getAttribute("X")))) - int(round(float(vertex[0].getAttribute("X"))))
                    areay=  int(round(float(vertex[3].getAttribute("Y")))) - int(round(float(vertex[0].getAttribute("Y"))))
                    if areax<0:
                        areax=areax*-1
                    if areay<0:
                        areay=areay*-1 
                    logging.debug("area id=%s areax=%d areaY=%d",areaid,areax,areay)
                
                    for v in vertex:
                        if int(round(float(v.getAttribute("X")))) < x:
                            logging.debug("###############################swapped x")
                            x=int(round(float(v.getAttribute("X"))))
                        if  int(round(float(v.getAttribute("Y")))) < y:
                            logging.debug("###############################swapped y")
                            y=int(round(float(v.getAttribute("Y"))))
                    
                    areatopLeftCorner=x,y
            
                    if (self.redZone is True) and (an.getAttribute("LineColor") == "255"):
                        areaid+="Red"
                        logging.info("red area Found: %s",rn.getAttribute("Id"))
                        ##e' sucesso che ci fossero regioni con dimenzioni zero :-(
                        if areax!=0 and areay !=0:
                            redregionsList.append([rn.getAttribute("Id"),areatopLeftCorner,areax,areay])
                            logging.debug("red region added")
    

                    if areax < self.minSizeX or  areay < self.minSizeY:
                        logging.warning("area n: %s too small for the crop size chosen, slide: %s",areaid,self.imgName)
                    else:
                        regionsList.append([areaid,areatopLeftCorner,areax,areay])  
        
        self.zoneList=regionsList
        self.redZoneList=redregionsList
        
        return len(self.zoneList)
    
    def getCornerPointFullSlide(self,cornerPointList,region,listOfSize):
        """
        lista di leftcorner point and size [leftCorner,(sizeX,sizeY)]
        region = id,areatopLeftCorner,areax,areay
        listOfSize = [(500,500),(1000,1000)]
        """
        
        for sizeFormat in listOfSize:
            sizeX=sizeFormat[0]
            sizeY=sizeFormat[1] 
            areaTopLeftX=region[1][0]
            areaTopLeftY=region[1][1]
            x=region[2]
            y=region[3]
            
            
            logging.debug("regioon%s cropForX= %d has X=%d cropForY=%d has Y=%d",region[0],sizeX,x,sizeY,y)
            
            
            if  sizeX < x and sizeY < y :         
                #####
                ##### per calcolo della sovrapposizione in parole povere:
                #####  prendi quanto spazzio ti servirebbe per fare campioni interi approssimazione maggiore della divisione 
                #####  dividi per approssimazione inferiore e lo usi come stride per le slide :-)
    #             
    #             nX=x/sizeX
    #             nY=y/sizeY
    #             
    #             #resto
    #             Rx=x-(sizeX*nX)
    #             Ry=y-(sizeY*nY)
                
                nX , Rx = divmod(x, sizeX)
                nY , Ry = divmod(y, sizeY)
                residuoX= sizeX-Rx
                residuoY= sizeY-Ry
                
                strideX= residuoX / (nX)
                strideY= residuoY / (nY)
                
                xPoint=list()
                yPoint=list()
                
                
                logging.debug("residuo x=%f strideX=%f Rx=%f sezeX/2=%f",residuoX,strideX,Rx,sizeX/2)
                logging.debug("residuo y=%f strideY=%f Ry=%f sezeY/2=%f",residuoY,strideY,Ry,sizeY/2)
                logging.debug("topcornr x= %d y= %d",areaTopLeftX,areaTopLeftY)
                
                ###caso preciso 
                if(Rx==0):
                    for ix in range(nX) :
                        xPoint.append(areaTopLeftX+(ix*sizeX))
                        logging.debug("X   Rx=0:"+str(areaTopLeftX+(ix*sizeX)))
                        
                ###caso sovrapposiziome maggiore del 50% non uso sovrapposizione ma centro l'aria        
                elif strideX > sizeX/2 :
                    for ix in range(nX):    
                        xPoint.append(areaTopLeftX+(strideX/2)+(ix*sizeX))
                        logging.debug("X   caso stride more then 50\%:"+str(areaTopLeftX+(strideX/2)+(ix*sizeX)))
                    
                ### uso sovrapposizione
                else:
                    nX+=1
                    for ix in range(nX):
                        xPoint.append(areaTopLeftX+(ix*sizeX)-(ix*strideX))
                        logging.debug("X   Uso stride per :" +str(areaTopLeftX+(ix*(sizeX))-(ix*strideX)))
                            
                
                if(Ry==0):
                    for iy in range(nY):
                        yPoint.append(areaTopLeftY+(iy*sizeY))
                        logging.debug( "Y   Ry=0:"+str(areaTopLeftY+(iy*sizeY)))
                        
                elif strideY > sizeY/2 :
                    for iy in range(nY):
                        yPoint.append(areaTopLeftY+(strideY/2)+(iy*sizeY))
                        logging.debug( "Y   caso stride more then 50\%:"+str(areaTopLeftY+(strideY/2)+(iy*sizeY)))
                else:
                    nY+=1
                    for iy in range(nY):
                        yPoint.append(areaTopLeftY+(iy*sizeY)-(iy*strideY))
                        logging.debug( "Y   Uso stride:"+str(areaTopLeftY+(iy*sizeY)-(iy*strideY)))        
            
                ncornerPoint=0
                for cornerY in yPoint:
                    for cornerX in xPoint:
                        ncornerPoint+=1
                        tupleCorner=cornerX,cornerY
                        logging.debug( tupleCorner)
                        cornerPointList.append([tupleCorner,(sizeX,sizeY),region[0]])               
            
            
                        
                logging.info( "number of crop size %dx%d of region %s : %d ",sizeX,sizeY,region[0],ncornerPoint)
            else :
                logging.info("crop size %d x %d of region:%s impossible for dimension restriction",sizeX,sizeY,region[0]) 

    def simpleThPercentage(self,imgP,percentMax):
        ##
        ## return pecentage of black    
        ## if show is truee show the immage
        img = cv2.imread(imgP,0)
        ret,th = cv2.threshold(img,221,255,cv2.THRESH_BINARY)
        percentage = float(cv2.countNonZero(th)) / float(img.size) * 100
        imTitle=imgP + " : " + str(percentage)
        
    #     if percentage > percentMax :
    #         plt.imshow(th,"gray")
    #         plt.xticks([]),plt.yticks([])
    #         plt.title(imTitle)
    #         plt.show()
            
        return percentage   


    def makeCrop(self):
        '''
        crea i crop dalle selezioni salvate nell' xml
        ritorna il numero totale di crop creati
        '''
        
        slide = openslide.OpenSlide(os.path.join(self.imgName))
        nLevel=slide.level_count
        
        logging.debug("total number of region %d",len(self.zoneList))
        
        ######
        if not os.path.isdir(self.outDirPath):
            os.makedirs(self.outDirPath)

        cropNum=0
        outCropDir= os.path.join(self.outDirPath,"crop","case")
        
        if not os.path.isdir(outCropDir):
            os.makedirs(outCropDir)
        
        nwhite=0  
        for region in self.zoneList :
            
            cornerPointList=list()
            ###
            #list Of size dimention to croop
            self.getCornerPointFullSlide(cornerPointList,region,self.listOfSize)
            logging.debug("slide name: %s  region: %s number of crop %d",self.imgName,region[0],len(cornerPointList))
            
            for cPoint in cornerPointList:
                cropNum+=1
                
                cropName= os.path.join(outCropDir,self.name+"-RN-"+cPoint[2]+"-cx-"+str(cPoint[0][0])+"-cy-"+str(cPoint[0][1])+"-x-"+str(cPoint[1][0])+"-y-"+str(cPoint[1][1])+"-"+str(cropNum)+self.cropFormat)
                slide.read_region(cPoint[0], 0 , cPoint[1]).save(cropName)
                
                ####
                ### percentuale di bianco accettata
                whiteMax=33

                if not os.path.isdir(os.path.join(self.outDirPath,"whiteRemoved")):
                    os.mkdir(os.path.join(self.outDirPath,"whiteRemoved"))
                if self.simpleThPercentage(cropName, whiteMax) > whiteMax :
                    nwhite+=1
                    os.rename(cropName, os.path.join(self.outDirPath,"whiteRemoved",self.name+"-wn-"+str(nwhite)+"-x"+str(cPoint[1][0])+"y"+str(cPoint[1][1])+str(cropNum)+self.cropFormat))
                    logging.debug("delete img for white")
                    cropNum-=1
                    
        if self.redZone is True :
            logging.info("#################### red Mode of slide %s #####################",self.name)
                    
            redOutPath= os.path.join(self.outDirPath,"redZone")  
            logging.debug("number of red region:%d",len(self.redZoneList))
            for region in self.redZoneList :
                
                #[areaid,areatopLeftCorner,areax,areay]
                if not os.path.isdir(redOutPath):
                    os.makedirs(redOutPath)
                cropName= os.path.join(redOutPath,self.name+"-areaID-"+region[0]+self.cropFormat)
                #print region
                logging.debug("savede red zone %s", self.name+"-areaN-"+region[0])
                slide.read_region(region[1], 0 , (region[2],region[3])).save(cropName)
     
        self.cropNum=cropNum
        return cropNum
        
        
        
        

        
        
