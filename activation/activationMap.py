'''
Created on 23 mar 2018

@author: richard
'''
import keras
import logging
from keras.applications.vgg16 import preprocess_input
#from keras.models import Mol
from keras.preprocessing import image
import cv2
import numpy as np
import os
import argparse
import sys

import PIL 


def resize(item, target_h, target_w, keep_aspect_ratio=False):
    """
    Resizes an image to match target dimensions
    :type item: np.ndarray
    :type target_h: int
    :type target_w: int
    :param item: 3d numpy array or PIL.Image
    :param target_h: height in pixels
    :param target_w: width in pixels
    :param keep_aspect_ratio: If False then image is rescaled to smallest dimension and then cropped
    :return: 3d numpy array
    """
    img = image.array_to_img(item, scale=False)
    if keep_aspect_ratio:
        img.thumbnail((target_w, target_w), PIL.Image.ANTIALIAS)
        img_resized = img
    else:
        img_resized = img.resize((target_w, target_h), resample=PIL.Image.NEAREST)

    # convert output
    img_resized = image.img_to_array(img_resized)
    img_resized = img_resized.astype(dtype=np.uint8)

    return img_resized 


def activationMap(args):
    
    rootdir = args.inPath
    modelPath = args.modelPath
    out_rootdir = args.outPath
    
    if not os.path.exists(out_rootdir):
        os.makedirs(out_rootdir)

    
    base_model = keras.models.load_model(filepath=modelPath)
    layers = ['block5_pool']#, 'block4_pool', 'block3_pool', 'block2_pool', 'block1_pool']
    for l in layers:
        model = keras.models.Model(inputs=base_model.input, outputs=base_model.get_layer(l).output)
        logging.info("Processing layer "+ l)
        for subdir, dirs, files in os.walk(rootdir):
            if subdir != rootdir and subdir != out_rootdir:
    
                output_dir = os.path.join(out_rootdir, l)
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                output_dir = os.path.join(output_dir, subdir.split('/')[-1])
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                maps = list()
                imgs = list()
                for filename in enumerate(files):
                    if filename[1].endswith(".jpeg"):

                        #img=image.load_img(os.path.join(subdir, filename[1]),target_size=(224,224))
                        #img_or = cv2.imread(os.path.join(subdir, filename[1]))
                       # 
                        #img = img_or.astype('float64')
                        #img = image.img_to_array(img)
                        #x = np.expand_dims(img, axis=0)
                        #x = keras.applications.vgg16.preprocess_input(x)
                        #features = model.predict(x)
                        
                        img_or = cv2.imread(os.path.join(subdir, filename[1]))
                        img_or = resize(img_or , 224,224,keep_aspect_ratio=False )
                        img = img_or.astype('float64')

                        x = np.expand_dims(img, axis=0)
                        x = preprocess_input(x)
                        features = model.predict(x)
                        
                        features = np.squeeze(features)
                        sz = features.shape
    
                        meanAct = np.mean(features, axis=(0,1))
                        idx = np.argmax(meanAct)
                        maxAct = features[:,:,idx]
                        maxAct = maxAct/np.max(maxAct)
                        activation_map = cv2.resize(maxAct, (224,224))
    
                        heatmap = cv2.applyColorMap(np.uint8(255*activation_map), cv2.COLORMAP_JET)
                        fin = cv2.addWeighted(heatmap, 0.5, img_or, 0.7, 0)
                        logging.info("salvandoImg in " + str(os.path.join(output_dir, "act_prova.png")) )
                        cv2.imwrite(os.path.join(output_dir, "act_prova.png"), fin)
                        maps.append(activation_map)
                        imgs.append(img_or)
    
                np.save(os.path.join(output_dir, 'act.npy'), np.asarray(maps))
                np.save(os.path.join(output_dir, 'imgs.npy'), np.asarray(imgs))
                logging.info("Saved" + str(os.path.join(output_dir, 'act.npy')))





if __name__ == '__main__':
    ###
    #setting logger
    global logging
    logging.basicConfig(stream= sys.stdout ,format='%(funcName)s %(asctime)s %(levelname)s:%(message)s',level=logging.DEBUG)
    
    ###
    #setting arguments parser
    parser = argparse.ArgumentParser(description='activation map printer')
    parser.add_argument('--out', dest='outPath' , 
                        help='outputh path for the crop',required=True)
    parser.add_argument('--in', dest='inPath', 
                        help='input path where crop are es test train validation')
    parser.add_argument('--format', dest='format' , default='.png' ,  
                        help='optional string format')
    parser.add_argument('--modelPath',dest="modelPath",help="keras model path",required=True)

    args = parser.parse_args()
    
    logging.info( "Starting...") 
        
        
    activationMap(args)
 
    
    logging.info( "End ")    
    exit()
