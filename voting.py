##########################################################################
#                                                                        #
#    Implementation of Distinguishing Between Natural and Computer-      #
#        Generated Images Using Convolutional Neural Networks            #
#                               (NIvsCG)                                 #
#               Majority Voting & Final Test Accuracies                  #
#                                                                        #
##########################################################################

from __future__ import print_function
import numpy as np
import sys, os
import keras
from keras.preprocessing.image import *
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization
from keras.layers import Conv2D, MaxPooling2D
from keras import optimizers, regularizers
from time import time
from keras.callbacks import TensorBoard, ReduceLROnPlateau, ModelCheckpoint
from PIL import Image

# Load model
model = load_model('NIvsCG_model.h5')

# optimizer
adam = optimizers.Adam(lr=1e-8)

# loss function is binary crossentropy (for binary classification)
model.compile(loss='binary_crossentropy',
              optimizer=adam,
              metrics=['accuracy'])

imageLabel = []
testLabel = []
imageTmp = []
testTmp = []
oriImageLabel = []  # one dimension list
oriTestLabel = []  # one dimension list

# TODO: implement majority voting algorithm and prediction using the model trained

patchesTxt = 'utils/output-data/test/output.txt'
patches = open(patchesTxt, 'r')
i = 0

print('Classifying patches...')
for line in patches:
    patch = line.split()
    if i < 200:
        img = Image.open('utils/output-data/test/' + patch[0])
        img = img.resize((233, 233))
        imageTmp.append(int(patch[1]))
        arr = np.array((img_to_array(img)),)
        arr = arr.reshape((1, 233, 233, 3))
        prediction = model.predict(arr)
        testTmp.append(prediction)
        i = i + 1
    else:
        oriImageLabel.extend(imageTmp)
        oriTestLabel.extend(testTmp)
        imageLabel.append(imageTmp)
        testLabel.append(testTmp)
        imageTmp = []
        testTmp = []
        i = 0

print('The number of full-sized testing images is:', len(imageLabel))

imageCropNum = [len(x) for x in imageLabel]
imageCropNumNp = np.array(imageCropNum)
imageLabelNp = np.array(imageLabel)
testLabelNp = np.array(testLabel)

#  Computing average accuracy on patches
result = np.array(oriImageLabel) == np.array(oriTestLabel)

personal_result = result[:200*200] # (200 images * 200 patches per image)
prcg_result = result[:200*200]
print('The number of patches:', len(oriImageLabel), len(prcg_result), len(personal_result))
print('The average accuracy on patches:')
print('The personal (NI) accuracy is:', personal_result.sum()*1.0/len(personal_result))
print('The prcg (CG) accuracy is:', prcg_result.sum()*1.0/len(prcg_result))
print('CG patches misclassified as natural patches (CGmcNI) is:', (len(prcg_result) - prcg_result.sum())*1.0/len(prcg_result))
print('natural patches misclassified as CG patches (NImcCG) is:', (len(personal_result) - personal_result.sum())*1.0/len(personal_result))
print('The average accuracy is:', result.sum()*1.0/len(result))

#  Computing average accuracy on full-sized images (29 patches and majority voting)
result = np.arange(len(imageLabel))
for x in range(len(imageLabel)):
    tmp = np.array(imageLabelNp[x]) == np.array(testLabelNp[x])
    result[x] = np.sum(tmp[:-1]) > imageCropNumNp[x]//2 - 1

prcg_result = result[:200]
personal_result = result[200:]
print('The average accuracy on full-sized images after majority voting: ', len(prcg_result), len(personal_result))
print('The google (NI) accuracy is:', personal_result.sum()*1.0/len(personal_result))
print('The prcg (CG) accuracy is:', prcg_result.sum()*1.0/len(prcg_result))
print('CG images misclassified as natural images (CGmcNI) is:', (len(prcg_result) - prcg_result.sum())*1.0/len(prcg_result))
print('natural images misclassified as CG images (NImcCG) is:', (len(personal_result) - personal_result.sum())*1.0/len(personal_result))
print('The average accuracy is:', result.sum()*1.0/len(result))