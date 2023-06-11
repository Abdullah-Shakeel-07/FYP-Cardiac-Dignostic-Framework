import tensorflow as tf
from keras.models import Model, load_model
from keras.layers import Input, BatchNormalization, Activation, Dense, Dropout
from keras.layers.core import Lambda, RepeatVector, Reshape
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D, GlobalMaxPool2D
from keras.layers import concatenate, add
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.optimizers import Adam
from keras_preprocessing.image import img_to_array, array_to_img, img_to_array,load_img
from flask import Flask, render_template, request
import numpy as np
import PIL
import pickle
import cv2

app = Flask(__name__)


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
    
  return volume

def calc_ejection_fraction(contours, spacing):
  # Calculate the left ventricular end-diastolic volume (LVEDV)
  lvedv = calc_volume(contours, spacing)/1000
#   print("lvedv ", lvedv)
  # Calculate the left ventricular end-systolic volume (LVESV)
  lvesv = calc_volume(contours[:len(contours) // 2], spacing)/1000
#   print("lvesv ", lvesv)
  # Check if the LVESV is greater than the LVEDV (which would indicate that the point of maximum contraction occurs before the midpoint of the cardiac cycle)
  if lvesv > lvedv:
    lvesv = calc_volume(contours[len(contours) // 2:], spacing)/1000
  
  # Calculate the ejection fraction
  ejection_fraction = (lvedv - lvesv) / lvedv
#   print("EF is ", ejection_fraction)
  return ejection_fraction

# Define the home page route
@app.route('/')
def home():
    return render_template('index.html')

# Define the route to handle the file upload
@app.route('/upload', methods=['POST'])
def upload():
    loaded_model = load_model('model.h5')
    # Get the uploaded file
    image = request.files['file1']
    spacing = request.files['file2']

    # Load the numpy array
    imgarr = np.load(image, allow_pickle=True)
    spacingarr = np.load(spacing, allow_pickle=True)

    no_image = imgarr.shape[0]
    shape =  imgarr.shape[1:]
    print(no_image, shape)

    # Make a prediction using the model
    preds_mask = loaded_model.predict(imgarr, verbose=1)
    preds_mask_t = (preds_mask > 0.5).astype(np.uint8)
    EF = calc_ejection_fraction(preds_mask_t, spacingarr)

    # Render the results template with the output
    return render_template('results.html', output=EF, slices = no_image, shapes = shape)

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=False)
