# -*- coding: utf-8 -*-
"""F22_102_R_CardioCheck.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KF_VRzoZCuNwBz7hYK8a5aDvw9aY5_ND

**F22-102-R-CardioCheck**

Cardiac Diagnostic Framework 

Abdullah Shakeel (i19-1717)

Ahmed Wadood (i19-1858)

Muhammad Ali (i19-1882)

A deep learning-based cardiac diagnostic framework that supports segmentation of the left ventricle in Cardiac MRI images using UNET and calculation of patient-wise Ejection Fraction.
"""

# Installing the required libraries

!pip install tensorflow --upgrade
!pip install keras --upgrade

!pip install pydicom
# !pip install tensorflow==2.11.0
!pip install keras_preprocessing
!pip install --upgrade --no-cache-dir gdown

"""**Importing necessary libraries**"""

# Commented out IPython magic to ensure Python compatibility.
import pydicom
import pickle
import cv2, re, sys
import os, fnmatch, shutil, subprocess
from IPython.utils import io
import numpy as np
np.random.seed(1234)
import matplotlib.pyplot as plt
from matplotlib import image
from collections import defaultdict
# %matplotlib inline
import warnings
warnings.filterwarnings('ignore') # we ignore a RuntimeWarning produced from dividing by zero

"""**loading dataset from google drive**"""

# MRI images link
# https://drive.google.com/file/d/1RXcK9GrIxjbw7kP9kszkPj0TqeyBxCfO/view?usp=share_link
# https://drive.google.com/file/d/16G6vLfon1qhWS0LVzVxBHxxoqOelq7pU/view?usp=sharing
# https://drive.google.com/file/d/1aRzhK2BOudTi42NL0a_pN-XorP3G7vXK/view?usp=sharing

# corresponding contour links
# https://drive.google.com/file/d/1UKJ6PdszqWrhFXMJjsvND4ERpTwBCn3I/view?usp=share_link
# https://drive.google.com/file/d/1f8jS6clvq-00cj821zQTIsOB5IXt61Xn/view?usp=share_link
# https://drive.google.com/file/d/16Xx2pgk5qJuPp2jNVgoDdgz7dwmbpo2D/view?usp=share_link

# MRI images
# Sunnybrook Cardiac MR Database DICOMPart1.zip
!gdown 1RXcK9GrIxjbw7kP9kszkPj0TqeyBxCfO
# Sunnybrook Cardiac MR Database DICOMPart2.zip
!gdown 16G6vLfon1qhWS0LVzVxBHxxoqOelq7pU
# Sunnybrook Cardiac MR Database DICOMPart3.zip
!gdown 1aRzhK2BOudTi42NL0a_pN-XorP3G7vXK

# Contours
# Sunnybrook Cardiac MR Database DICOMPart1.zip
!gdown 1UKJ6PdszqWrhFXMJjsvND4ERpTwBCn3I
# Sunnybrook Cardiac MR Database DICOMPart2.zip
!gdown 1f8jS6clvq-00cj821zQTIsOB5IXt61Xn
# Sunnybrook Cardiac MR Database DICOMPart3.zip
!gdown 16Xx2pgk5qJuPp2jNVgoDdgz7dwmbpo2D

"""**Loading DSB**"""

!gdown 1hiGdgOkY7h3_6IPyyiGeEf6jgQKrRW0x
# https://drive.google.com/file/d/1hiGdgOkY7h3_6IPyyiGeEf6jgQKrRW0x/view?usp=sharing



"""**Making folder to store extracted Dataset**"""

!mkdir "Part1"
!mkdir "Part2"
!mkdir "Part3"
!mkdir "ContourPart1"
!mkdir "ContourPart2"
!mkdir "ContourPart3"
!mkdir "SunnyBrook"
!mkdir "DSB"

"""**Unzipping the loaded dataset**"""

!unzip -u "/content/Sunnybrook Cardiac MR Database DICOMPart1.zip" -d "Part1"
!unzip -u "/content/Sunnybrook Cardiac MR Database DICOMPart2.zip" -d "Part2"
!unzip -u "/content/Sunnybrook Cardiac MR Database DICOMPart3.zip" -d "Part3"
!unzip -u "/content/kaggle_ndsb2-master.zip" -d "DSB"

!unzip -u "/content/Sunnybrook Cardiac MR Database ContoursPart1.zip" -d "ContourPart1"
!unzip -u "/content/Sunnybrook Cardiac MR Database ContoursPart2.zip" -d "ContourPart2"
!unzip -u "/content/Sunnybrook Cardiac MR Database ContoursPart3.zip" -d "ContourPart3"

!cp -r "/content/DSB/kaggle_ndsb2-master/data_segmenter_trainset" "/content/DSB"

"""**Removing the orignal zip file because now we have extracted datset**"""

rm '/content/Sunnybrook Cardiac MR Database DICOMPart1.zip'

rm '/content/Sunnybrook Cardiac MR Database DICOMPart2.zip'

rm '/content/Sunnybrook Cardiac MR Database DICOMPart3.zip'

rm '/content/Sunnybrook Cardiac MR Database ContoursPart1.zip'

rm '/content/Sunnybrook Cardiac MR Database ContoursPart2.zip'

rm '/content/Sunnybrook Cardiac MR Database ContoursPart3.zip'

rm "/content/kaggle_ndsb2-master.zip"

rm -r "/content/DSB/kaggle_ndsb2-master"

"""**Setting all the initail path for dataset**"""

SUNNYBROOK_ROOT_PATH = 'SunnyBrook'

TRAIN_CONTOUR_PATH = os.path.join(SUNNYBROOK_ROOT_PATH,'/content/ContourPart3/Sunnybrook Cardiac MR Database ContoursPart3/TrainingDataContours')
VALID_CONTOUR_PATH = os.path.join(SUNNYBROOK_ROOT_PATH,'/content/ContourPart2/Sunnybrook Cardiac MR Database ContoursPart2/ValidationDataContours')
TEST_CONTOUR_PATH = os.path.join(SUNNYBROOK_ROOT_PATH,'/content/ContourPart1/Sunnybrook Cardiac MR Database ContoursPart1/OnlineDataContours')

TRAIN_IMG_PATH = os.path.join(SUNNYBROOK_ROOT_PATH,'/content/Part3/Sunnybrook Cardiac MR Database DICOMPart3/TrainingDataDICOM')
VALID_IMG_PATH = os.path.join(SUNNYBROOK_ROOT_PATH,'/content/Part2/Sunnybrook Cardiac MR Database DICOMPart2/ValidationDataDICOM')
TEST_IMG_PATH = os.path.join(SUNNYBROOK_ROOT_PATH,'/content/Part1/Sunnybrook Cardiac MR Database DICOMPart1/OnlineDataDICOM')

"""  There are two types of contours(Segmented images) for dataset
 
  "i" represents endocardium
 
  "o" represent epicardium
 
  we are ineterested in endocardium
"""

contour_type='i'
crop_size = 112 # Setting the cropng size = 112 so that we have a clear view of left ventricle 
sunnybrook_training_patient_dictonary = {}
sunnybrook_validation_patient_dictonary = {}
sunnybrook_testing_patient_dictonary = {}

"""**Extracting patient ID and image number from the path of image to store MRI image patient wise**"""

def case_image(ctr_path):
  # print("ctr path is ", ctr_path)
  match = re.search(r'/([^/]*)/contours-manual/IRCCI-expert/IM-0001-(\d{4})-.*', ctr_path) 
  case = match.group(1)
  img_no = int(match.group(2))
  # print("case and image numbre is ", case, img_no)
  return case, img_no

"""**Saving all the paths for Contours**"""

def map_all_contours(contour_path, contour_type, shuffle=True):
    print(contour_path)
    # contours = [os.path.join(dirpath, f)
    #     for dirpath, dirnames, files in os.walk(contour_path)
    #     for f in fnmatch.filter(files,
    #                     'IM-0001-*-'+contour_type+'contour-manual.txt')]
    patient_data_path = []
    for dirpath, dirnames, files in os.walk(contour_path):
      for f in fnmatch.filter(files,'IM-0001-*-'+contour_type+'contour-manual.txt'):
        patient_data_path.append(dirpath + "/" + f)

    if shuffle:
        print('Shuffling data')
        np.random.shuffle(patient_data_path)
    # return contours
    return patient_data_path

train_ctrs = map_all_contours(TRAIN_CONTOUR_PATH, contour_type, shuffle=True)
test_ctrs = map_all_contours(TEST_CONTOUR_PATH, contour_type,shuffle=True)
valid_ctrs = map_all_contours(VALID_CONTOUR_PATH, contour_type,shuffle=True)

#looking at the unique patients
names = []
for string in train_ctrs:
  match = re.search(r'TrainingDataContours/(.+?)/', string)
  if match:
      extracted_string = match.group(1)
      names.append(extracted_string)
for string in valid_ctrs:
  match = re.search(r'ValidationDataContours/(.+?)/', string)
  if match:
      extracted_string = match.group(1)
      names.append(extracted_string)

for string in test_ctrs:
  match = re.search(r'OnlineDataContours/(.+?)/', string)
  if match:
      extracted_string = match.group(1)
      names.append(extracted_string)

np.unique(names)

"""**Storing patient ID as key and there contour's path as value**"""

def store_patient_data_path(ctrs):
  temp_dict = defaultdict(list)
  for i in ctrs:
    match = re.search(r'/([^/]*)/contours-manual/IRCCI-expert/IM-0001-(\d{4})-.*', i)
    key = match.group(1)
    temp_dict[key].append(i)
  return temp_dict

sunnybrook_training_patient_contours = store_patient_data_path(train_ctrs)
sunnybrook_validation_patient_contours = store_patient_data_path(valid_ctrs)
sunnybrook_testing_patient_contours = store_patient_data_path(test_ctrs)

# inx = 0
# for k in sunnybrook_training_patient_dictonary.keys():
#   inx += len(sunnybrook_training_patient_dictonary[k])
# print(inx)

"""**Reading contours file**"""

def read_contour(contour, data_path):
    case_nmumber, img_number = case_image(contour)
    filename = 'IM-0001-%04d.dcm' % (img_number)
    full_path = os.path.join(data_path, case_nmumber, "DICOM",  filename)
    # print("path is ", full_path)
    # f = dicom.read_file(full_path)
    f = pydicom.dcmread(full_path)
    spacing = (float(f.PixelSpacing[0]), float(f.PixelSpacing[1]), float(f.SliceThickness))
    img = f.pixel_array.astype('int')
    mask = np.zeros_like(img, dtype='uint8')
    coords = np.loadtxt(contour, delimiter=' ').astype('int')
    cv2.fillPoly(mask, [coords], 1)
    # print("hello there")
    # print("printing shapes ", np.shape(img), " and ", np.shape(mask))
    if img.ndim < 3:
        img = img[..., np.newaxis]
        mask = mask[..., np.newaxis]
    # img, mask = 0,0
    # print("again printing shapes ", np.shape(img), " and ", np.shape(mask))
    return img, mask, spacing

"""**Croping the MRI images and contours for better results**"""

def center_crop(ndarray, crop_size):
    
    h, w, d = ndarray.shape
    # center crop
    h_offset = int((h - crop_size) / 2)
    w_offset = int((w - crop_size) / 2)
    cropped = ndarray[h_offset:(h_offset+crop_size),
                      w_offset:(w_offset+crop_size), :]

    return cropped

def export_all_contours(contours, data_path, crop_size):
    print('\nProcessing {:d} images and labels ...\n'.format(len(list(contours))))
    images = np.zeros((len(list(contours)), crop_size, crop_size, 1))
    masks = np.zeros((len(list(contours)), crop_size, crop_size, 1))
    spacing = []
    for idx, contour in enumerate(contours):
      # print("hello path is ", idx, " and ", contour)
      img, mask, temp_spacing = read_contour(contour, data_path)
      img = center_crop(img, crop_size=crop_size)
      mask = center_crop(mask, crop_size=crop_size)
      images[idx] = img
      masks[idx] = mask
      spacing.append(temp_spacing)
    return images, masks, spacing

"""**Extracting MRI images and contour for training and validation**"""

# pass data patient by patient

print('Processing Training Data ...')
img_train, mask_train, space_train = export_all_contours(train_ctrs, TRAIN_IMG_PATH, crop_size=crop_size)

print('Processing Validation Data ...')
img_vad, mask_vad, space_vad = export_all_contours(valid_ctrs, VALID_IMG_PATH, crop_size=crop_size)

# print('Processing Test Data ...')
# img_test, mask_test, space_vad = export_all_contours(test_ctrs, TEST_IMG_PATH, crop_size=crop_size)

"""**Plotting Origanl Image and contour**"""

for idx, contour in enumerate(train_ctrs):
  img, mask, spacing = read_contour(contour, TRAIN_IMG_PATH)
  f, axarr = plt.subplots(1, 2)
  axarr[0].imshow(img[:,:,0])
  axarr[1].imshow(mask[:,:,0])
  plt.show()
  break

"""**Plotting proceseed MRI image and Contours**"""

f, axarr = plt.subplots(2,2)
axarr[0,0].imshow(img_train[0,:,:,0])
axarr[0,1].imshow(mask_train[0,:,:,0])
axarr[1,0].imshow(img_train[1,:,:,0])
axarr[1,1].imshow(mask_train[1,:,:,0])
plt.show()

f, axarr = plt.subplots(2,2)
axarr[0,0].imshow(img_vad[2,:,:,0])
axarr[0,1].imshow(mask_vad[2,:,:,0])
axarr[1,0].imshow(img_vad[3,:,:,0])
axarr[1,1].imshow(mask_vad[3,:,:,0])
plt.show()

print(f"Train image shape {img_train.shape} and Train mask shape {mask_train.shape}")
print(f"Validation image shape {img_vad.shape} and Validation mask shape {mask_vad.shape}")
# print(f"Test image shape {img_test.shape} and Test mask shape {mask_test.shape}")

!mkdir "Training_data"
base_folder = '/content/Training_data/'
index = 0
for k in range(len(img_train)):
    print("\nTraining patient ", k)
    folder_name = f'patient{index}'
    folder_path = os.path.join(base_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    np.save(f"/content/Training_data/patient{index}/patientMRI_{index}.npy", img_train[k])
    np.save(f"/content/Training_data/patient{index}/patientContour_{index}.npy", mask_train[k])
    index += 1

!mkdir "Validation_data"
base_folder = '/content/Validation_data/'
index = 0
for k in range(len(img_vad)):
    print("\nValidation patient ", k)
    folder_name = f'patient{index}'
    folder_path = os.path.join(base_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    np.save(f"/content/Validation_data/patient{index}/patientMRI_{index}.npy", img_vad[k])
    np.save(f"/content/Validation_data/patient{index}/patientContour_{index}.npy", mask_vad[k])
    index += 1

np.shape(img_train)





"""**UNET Model**"""

# importing all the necessary libraries for UNET
import tensorflow as tf
from keras.models import Model, load_model
from keras.layers import Input, BatchNormalization, Activation, Dense, Dropout
from keras.layers.core import Lambda, RepeatVector, Reshape
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D, GlobalMaxPool2D
from keras.layers import concatenate, add
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.optimizers import Adam
# from keras.preprocessing.image import ImageDataGenerator,  
from keras_preprocessing.image import img_to_array, array_to_img, img_to_array,load_img
# from tensorflow.keras.utils import img_to_array
from keras.utils.vis_utils import plot_model

"""**Function to Add 2 convolutional layer to network**"""

def conv2d_block(input_tensor, n_filters, kernel_size = 3, batchnorm = True):
    # adding first layer
    x = Conv2D(filters = n_filters, kernel_size = (kernel_size, kernel_size),\
              kernel_initializer = 'he_normal', padding = 'same')(input_tensor)
    if batchnorm:
        x = BatchNormalization()(x)
    x = Activation('relu')(x)
    
    # adding second layer
    x = Conv2D(filters = n_filters, kernel_size = (kernel_size, kernel_size),\
              kernel_initializer = 'he_normal', padding = 'same')(input_tensor)
    if batchnorm:
        x = BatchNormalization()(x)
    x = Activation('relu')(x)
    
    return x

"""**Defining UNET model**"""

def get_unet(input_img, n_filters = 16, dropout = 0.1, batchnorm = True):
    # Contracting Path
    c1 = conv2d_block(input_img, n_filters * 1, kernel_size = 3, batchnorm = batchnorm)   # convolutional layer
    p1 = MaxPooling2D((2, 2))(c1)                                                         # Max pooling layer
    p1 = Dropout(dropout)(p1)                                                             # Dropout 
    
    c2 = conv2d_block(p1, n_filters * 2, kernel_size = 3, batchnorm = batchnorm)
    p2 = MaxPooling2D((2, 2))(c2)
    p2 = Dropout(dropout)(p2)
    
    c3 = conv2d_block(p2, n_filters * 4, kernel_size = 3, batchnorm = batchnorm)
    p3 = MaxPooling2D((2, 2))(c3)
    p3 = Dropout(dropout)(p3)
    
    c4 = conv2d_block(p3, n_filters * 8, kernel_size = 3, batchnorm = batchnorm)
    p4 = MaxPooling2D((2, 2))(c4)
    p4 = Dropout(dropout)(p4)
    
    c5 = conv2d_block(p4, n_filters = n_filters * 16, kernel_size = 3, batchnorm = batchnorm)
    
    # Expansive Path
    u6 = Conv2DTranspose(n_filters * 8, (3, 3), strides = (2, 2), padding = 'same')(c5)        # Transposed convolutional layer
    u6 = concatenate([u6, c4])                                                                 # concatenation leyer
    u6 = Dropout(dropout)(u6)                                                                  # Dropout layer
    c6 = conv2d_block(u6, n_filters * 8, kernel_size = 3, batchnorm = batchnorm)               # convolutional layer
    
    u7 = Conv2DTranspose(n_filters * 4, (3, 3), strides = (2, 2), padding = 'same')(c6)
    u7 = concatenate([u7, c3])
    u7 = Dropout(dropout)(u7)
    c7 = conv2d_block(u7, n_filters * 4, kernel_size = 3, batchnorm = batchnorm)
    
    u8 = Conv2DTranspose(n_filters * 2, (3, 3), strides = (2, 2), padding = 'same')(c7)
    u8 = concatenate([u8, c2])
    u8 = Dropout(dropout)(u8)
    c8 = conv2d_block(u8, n_filters * 2, kernel_size = 3, batchnorm = batchnorm)
    
    u9 = Conv2DTranspose(n_filters * 1, (3, 3), strides = (2, 2), padding = 'same')(c8)
    u9 = concatenate([u9, c1])
    u9 = Dropout(dropout)(u9)
    c9 = conv2d_block(u9, n_filters * 1, kernel_size = 3, batchnorm = batchnorm)
    
    outputs = Conv2D(1, (1, 1), activation='sigmoid')(c9)                                     # applying sigmoid on last layer
    model = Model(inputs=[input_img], outputs=[outputs])
    return model

"""**Setting parameter for model**"""

im_width = 112
im_height = 112
input_img = Input((im_height, im_width, 1), name='img')
model = get_unet(input_img, n_filters=16, dropout=0.05, batchnorm=True)
# model.compile(optimizer=Adam(), loss="binary_crossentropy", metrics=["accuracy"])
model.compile(optimizer=tf.keras.optimizers.Adam(), loss="binary_crossentropy", metrics=["accuracy"])

"""**Model Summary**"""

model.summary()

"""**Plotting the model**"""

plot_model(model, show_shapes=True, show_layer_names=True)

"""**Callback**"""

callbacks = [
    EarlyStopping(patience=10, verbose=1),
    ReduceLROnPlateau(factor=0.1, patience=5, min_lr=0.00001, verbose=1),
    ModelCheckpoint('model-tgs-salt.h5', verbose=1, save_best_only=True, save_weights_only=True)
]

"""**Training**"""

def Train_function(model, train_images,train_mask, validation_images, validation_maks, batch_size, epoch,callbacks ):
  print("Training ")
  results = model.fit(train_images, train_mask, batch_size=batch_size, epochs=epoch, callbacks=callbacks,\
                    validation_data=(validation_images, validation_maks))
  return results

epoch = 50
batch_size = 32
results = Train_function(model, img_train, mask_train, img_vad, mask_vad, batch_size, epoch, callbacks)

"""**Learning Curve**"""

plt.figure(figsize=(8, 8))
plt.title("Learning curve")
plt.plot(results.history["loss"], label="loss")
plt.plot(results.history["val_loss"], label="val_loss")
plt.plot( np.argmin(results.history["val_loss"]), np.min(results.history["val_loss"]), marker="x", color="r", label="best model")
plt.xlabel("Epochs")
plt.ylabel("log_loss")
plt.legend();

"""**Exporting the model in pickle file**"""

model.load_weights('model-tgs-salt.h5')
pickle.dump(model, open('model.pkl', 'wb'))
model.save('model.h5')

"""**Saving model to google drive**"""

from google.colab import drive
drive.mount('/content/drive')

!cp /content/model-tgs-salt.h5 /content/drive/MyDrive/FYP/FYP-CardiacMRI/Model_and_weights

!cp /content/model.pkl /content/drive/MyDrive/FYP/FYP-CardiacMRI/Model_and_weights

!cp /content/model.png /content/drive/MyDrive/FYP/FYP-CardiacMRI/Model_and_weights

!cp /content/model.h5 /content/drive/MyDrive/FYP/FYP-CardiacMRI/Model_and_weights

"""**Function to plot the results**"""

import random
def plot_sample(X, y, preds, binary_preds, ix=None):
    """Function to plot the results"""
    if ix is None:
        ix = random.randint(0, len(X))
    print("index is ",ix)

    has_mask = y[ix].max() > 0

    fig, ax = plt.subplots(1, 4, figsize=(20, 10))
    ax[0].imshow(X[ix, ..., 0], cmap='seismic')
    if has_mask:
        ax[0].contour(y[ix].squeeze(), colors='k', levels=[0.5])
    ax[0].set_title('mask')

    ax[1].imshow(y[ix].squeeze())
    ax[1].set_title('binary mask')

    ax[2].imshow(preds[ix].squeeze(), vmin=0, vmax=1)
    if has_mask:
        ax[2].contour(y[ix].squeeze(), colors='k', levels=[0.5])
    ax[2].set_title('predicted mask')
    
    ax[3].imshow(binary_preds[ix].squeeze(), vmin=0, vmax=1)
    if has_mask:
        ax[3].contour(y[ix].squeeze(), colors='k', levels=[0.5])
    ax[3].set_title('predicted binary mask');

"""**Testing**"""

def Testing(model, test_dict, number_of_patient):
  model.load_weights('model-tgs-salt.h5')
  patient_reach = 0
  for k in test_dict.keys():
    patient_reach +=1
    print("\nTesting patient ", k)
    img_temp, mask_temp , temp_spacing = export_all_contours(test_dict[k], TEST_IMG_PATH, crop_size=crop_size)
    preds_mask = model.predict(img_temp, verbose=1)
    preds_mask_t = (preds_mask > 0.5).astype(np.uint8)
    model.evaluate(mask_temp, preds_mask_t, verbose=1)
    plot_sample(img_temp, mask_temp, preds_mask, preds_mask_t)
    if patient_reach == number_of_patient:
      break
  return results

results = Testing(model, sunnybrook_testing_patient_contours, 2)

sunnybrook_testing_patient_contours.keys()

"""**Calculating Ejection Fraction**"""

import cv2
def calc_volume(contours, spacing):
  # Calculate the volume by summing the volumes of each slice
  volume = 0
  i =0
  for (contour, space) in zip(contours, spacing):
  
    # using area 
    temp_contour = contour.astype(np.uint8)
    update_contour, hierarchy = cv2.findContours(temp_contour, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    try:
      cnt = update_contour[0]
      area = cv2.contourArea(cnt)
    # Assume a slice thickness of 1 for the volume calculation
      slice_volume = area * 1
      volume += slice_volume
    
    except:
      print("hello")
      pass
    i+=1

    # # using sapcing
    # contour_volume = np.sum(contour) * space[0] * space[1] * space[2]
    # volume += contour_volume
    
  return volume

def calc_ejection_fraction(contours, spacing):
  # Calculate the left ventricular end-diastolic volume (LVEDV)
  lvedv = calc_volume(contours, spacing)/1000
  # print("lvedv ", lvedv)
  # Calculate the left ventricular end-systolic volume (LVESV)
  lvesv = calc_volume(contours[:len(contours) // 2], spacing)/1000
  # print("lvesv ", lvesv)
  # Check if the LVESV is greater than the LVEDV (which would indicate that the point of maximum contraction occurs before the midpoint of the cardiac cycle)
  if lvesv > lvedv:
    lvesv = calc_volume(contours[len(contours) // 2:], spacing)/1000
  
  # Calculate the ejection fraction
  ejection_fraction = (lvedv - lvesv) / lvedv
  print("EF is ", ejection_fraction)
  return ejection_fraction

"""**Calculating ejection fraction on orignal contours and predicted contours**"""

patient_ , orignalEF, EF_ = [], [], []
img_temp, mask_temp , temp_spacing = [], [], []
for k in sunnybrook_testing_patient_contours.keys():
  print("Calculating EF ", k)
  img_temp, mask_temp , temp_spacing = export_all_contours(sunnybrook_testing_patient_contours[k], TEST_IMG_PATH, crop_size=crop_size)
  preds_mask = model.predict(img_temp, verbose=1)
  preds_mask_t = (preds_mask > 0.5).astype(np.uint8)
  model.evaluate(mask_temp, preds_mask_t, verbose=1)
  # plot_results(img_temp, mask_temp, preds_mask)
  # plot_sample(img_temp, mask_temp, preds_mask, preds_mask_t, 0)
  temp_ef = calc_ejection_fraction(preds_mask_t, temp_spacing)
  orignal_ef = calc_ejection_fraction(mask_temp, temp_spacing)
  patient_.append(k)
  EF_.append(temp_ef)
  orignalEF.append(orignal_ef)

"""**Plotting Ejection fraction of orignal contuors and predicted contours**"""

fig, ax = plt.subplots(1, 1, figsize=[18,5])
plt.plot(patient_, EF_, '+', color='r', label="pred", linestyle='-')
plt.plot(patient_, orignalEF, '*', color='b', label="actual", linestyle='-')
plt.legend()

# Testing for frontend

# Saving the testing dataset

!mkdir "Testing_data"
base_folder = '/content/Testing_data/'
index = 0
for k in sunnybrook_testing_patient_contours.keys():
    print("\nTesting patient ", k)
    img_temp, mask_temp , temp_spacing = export_all_contours(sunnybrook_testing_patient_contours[k], TEST_IMG_PATH, crop_size=crop_size)
    print(np.shape(img_temp))
    folder_name = f'patient{index}'
    folder_path = os.path.join(base_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    np.save(f"/content/Testing_data/patient{index}/patientMRI_{index}.npy", img_temp)
    np.save(f"/content/Testing_data/patient{index}/patientContour_{index}.npy", mask_temp)
    np.save(f"/content/Testing_data/patient{index}/patientspacing_{index}.npy", temp_spacing)
    index += 1

# !mkdir "Training_data"
# base_folder = '/content/Training_data/'
# index = 0
# for k in sunnybrook_training_patient_contours.keys():
#     print("\nTraining patient ", k)
#     img_temp, mask_temp , temp_spacing = export_all_contours(sunnybrook_training_patient_contours[k], TRAIN_IMG_PATH, crop_size=crop_size)
#     print(np.shape(img_temp))
#     folder_name = f'patient{index}'
#     folder_path = os.path.join(base_folder, folder_name)
#     os.makedirs(folder_path, exist_ok=True)

#     np.save(f"/content/Training_data/patient{index}/patientMRI_{index}.npy", img_temp)
#     np.save(f"/content/Training_data/patient{index}/patientContour_{index}.npy", mask_temp)
#     np.save(f"/content/Training_data/patient{index}/patientspacing_{index}.npy", temp_spacing)
#     index += 1

# !mkdir "Validation_data"
# base_folder = '/content/Validation_data/'
# index = 0
# for k in sunnybrook_validation_patient_contours.keys():
#     print("\nValidation patient ", k)
#     img_temp, mask_temp , temp_spacing = export_all_contours(sunnybrook_validation_patient_contours[k], VALID_IMG_PATH, crop_size=crop_size)
#     print(np.shape(img_temp))
#     folder_name = f'patient{index}'
#     folder_path = os.path.join(base_folder, folder_name)
#     os.makedirs(folder_path, exist_ok=True)

#     np.save(f"/content/Validation_data/patient{index}/patientMRI_{index}.npy", img_temp)
#     np.save(f"/content/Validation_data/patient{index}/patientContour_{index}.npy", mask_temp)
#     np.save(f"/content/Validation_data/patient{index}/patientspacing_{index}.npy", temp_spacing)
#     index += 1

print(sunnybrook_training_patient_contours.keys())
print(sunnybrook_validation_patient_contours.keys())
print(sunnybrook_testing_patient_contours.keys())

# Downloading the testing dataset

!zip -r /content/train.zip /content/Training_data

!zip -r /content/valid.zip /content/Validation_data

!zip -r /content/test.zip /content/Testing_data

from google.colab import files
files.download("/content/test.zip")

# Loading the model from google drive

loaded_model = load_model('/content/drive/MyDrive/FYP/FYP-CardiacMRI/Model_and_weights/model.h5')

import cv2
def calc_volume_test(contours, spacing):
  # Calculate the volume by summing the volumes of each slice
  volume = 0
  i =0
  for (contour, space) in zip(contours, spacing):
  
    # using area 
    temp_contour = contour.astype(np.uint8)
    update_contour, hierarchy = cv2.findContours(temp_contour, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    try:
      cnt = update_contour[0]
      area = cv2.contourArea(cnt)
    # Assume a slice thickness of 1 for the volume calculation
      slice_volume = area * 1
      volume += slice_volume
    
    except:
      print("hello")
      pass
    i+=1

    # # using sapcing
    # contour_volume = np.sum(contour) * space[0] * space[1] * space[2]
    # volume += contour_volume
    
  return volume

def calc_ejection_fraction_test(contours, spacing):
  # Calculate the left ventricular end-diastolic volume (LVEDV)
  lvedv = calc_volume_test(contours, spacing)/1000
  print("lvedv ", lvedv)
  # Calculate the left ventricular end-systolic volume (LVESV)
  lvesv = calc_volume_test(contours[:len(contours) // 2], spacing)/1000
  print("lvesv ", lvesv)
  # Check if the LVESV is greater than the LVEDV (which would indicate that the point of maximum contraction occurs before the midpoint of the cardiac cycle)
  if lvesv > lvedv:
    lvesv = calc_volume(contours[len(contours) // 2:], spacing)/1000
  
  # Calculate the ejection fraction
  ejection_fraction = (lvedv - lvesv) / lvedv
  print("EF is ", ejection_fraction)
  return ejection_fraction

for k in range(index):
    print("Patient ", k)
    folder_name = f'patient{k}'
    folder_path = os.path.join(base_folder, folder_name)
    # print(folder_path+f"/patientspacing_{k}.npy")
    img = np.load(folder_path+f"/patientMRI_{k}.npy")
    msk = np.load(folder_path+f"/patientContour_{k}.npy")
    spcing = np.load(folder_path+f"/patientspacing_{k}.npy")
    
    preds_mask = loaded_model.predict(img, verbose=1)
    preds_mask_t = (preds_mask > 0.5).astype(np.uint8)

    temp_ef = calc_ejection_fraction_test(preds_mask_t, spcing)
    print("EF", temp_ef)

for k in range(index-1):
    img = np.load(f"/content/Testing_data/patientMRI_{k}.npy")
    msk = np.load(f"/content/Testing_data/patientContour_{k}.npy")
    spcing = np.load(f"/content/Testing_data/patientspacing_{k}.npy")
    
    preds_mask = loaded_model.predict(img, verbose=1)
    preds_mask_t = (preds_mask > 0.5).astype(np.uint8)
    loaded_model.evaluate(msk, preds_mask_t, verbose=1)
    plot_sample(img, msk, preds_mask, preds_mask_t)



print("Shape of MIR image", np.shape(img))
print("Shape of Contour", np.shape(msk))

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(img[10])
axarr[1].imshow(msk[10])
plt.show()

