'''
Created on Jan 27, 2018

@author: pope
'''

from keras.preprocessing.image import ImageDataGenerator
import keras


import os
import numpy as np
import csv

##################
# solo per confusion matrix
import itertools
import matplotlib
#from sklearn.metrics import confusion_matrix
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
###################


class MyKerasModel(object):
    '''
    Classe che si occupa della gestione del modello keras della rete
    confusion_label=['E','S']
    '''


    def __init__(self, modelPath,outPutPath):
        '''
        Constructor
        '''
        self.outPutPath=outPutPath
        self.model = keras.models.load_model(filepath=modelPath)
        self.model.summary()
            # dimensions of our images.
        self.img_width = 224
        self.img_height = 224
        self.predictionList=list()

    def plot_confusion_matrix(self,cm, classes,
                              normalize=False,
                              title='Confusion matrix',
                              cmap=plt.cm.get_cmap("Blues"),
                              best=False):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')
    
        print(cm)
    
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)
    
        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fmt),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
    
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        if normalize:
            if best :
                plt.savefig('Best_normalized_Confusion_Matrix.png')
            else:
                plt.savefig('normalized_Confusion_Matrix.png')
        else:
            if best:
                plt.savefig('best_Confusion_Matrix.png')
            else:
                plt.savefig('Confusion_Matrix.png')
        plt.close()





  
    def predict(self,dataDir,case=None):
        
        # only rescaling channel color
        test_datagen = ImageDataGenerator(rescale=1. /255)
        test_data_dir = os.path.join(dataDir)
        
        test_generator = test_datagen.flow_from_directory(
            test_data_dir,
            target_size=(self.img_width, self.img_height),
            batch_size=1,
            shuffle=False,
            class_mode='categorical')
        
        n_predict=len(test_generator.filenames)
        preds = self.model.predict_generator(test_generator, n_predict)
        
        #print preds
        #print val_generator.filenames
        
        ##creare np array con prediction prendendo la predizione con percentuale maggiore
        y_pred=np.empty([0])
        for predictionElement in preds:
            index_max = np.argmax(predictionElement)
            y_pred=np.append(y_pred,index_max)
        
        #print val_generator.classes
        
        #y_test=np.asarray(test_generator.classes)
        #print y_test.shape
        #print y_pred.shape

        preds=zip(*preds)

        predictionExtended= zip(test_generator.filenames,y_pred,preds[0],preds[1])
        self.predictionList=predictionExtended
        with open(os.path.join(self.outPutPath,"predictionBest.csv"), "wb") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "predict_value","preds0","preds1"])
            writer.writerows(predictionExtended)
        
#         confusion_label=['E','S']
#         
#         y_case=np.full((len(y_pred), 1), case, dtype=int)
#         
#         # # Compute confusion matrix
#         cnf_matrix = confusion_matrix(y_case, y_pred)
#         np.set_printoptions(precision=2)
#          
#          
#         print test_generator.class_indices
#         class_names=test_generator.class_indices
#          
#         # Plot non-normalized confusion matrix
#         
#         self.plot_confusion_matrix(cnf_matrix, classes=confusion_label,
#                               title='Confusion matrix BestWeight, without normalization',best=True)
#         
#         # Plot  confusion matrix
#         self.plot_confusion_matrix(cnf_matrix, normalize=True,classes=confusion_label,
#                               title='Confusion matrix BestWeight, without normalization',best=True)
#         
#         print "END!"
        
        
