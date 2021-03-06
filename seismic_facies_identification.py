# -*- coding: utf-8 -*-
"""Seismic_facies_identification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ys5Gd1jA44IWGgEFhS-gPpDwAo_Qxpo_
"""

import pandas as pd;
import numpy as np;
import tensorflow as tf;

DATA_URL = 'https://datasets.aicrowd.com/default/aicrowd-public-datasets/seamai-facies-challenge/v0.1/public/labels_train.npz'
file_path= 'drive/My Drive/SEAM/labels_train.npz'
path = tf.keras.utils.get_file(fname= 'datasets', origin= DATA_URL)

from google.colab import drive
drive.mount('/content/gdrive')

data= np.load(path);

dat= data['labels']

df= pd.DataFrame(dat[:,0,:]);
df.head(20)

np.savez_compressed('gdrive/My Drive/SEAM/labels_train.npz', labels= dat);

DATA_URL2 = 'https://datasets.aicrowd.com/default/aicrowd-public-datasets/seamai-facies-challenge/v0.1/public/data_test_1.npz'

path_test_data = tf.keras.utils.get_file('datasets2', DATA_URL2)
data_test= np.load(path_test_data);

dat_test= data_test['data']

df_test_data= pd.DataFrame(dat_test[:,0,:])
df_test_data.head(10)

np.savez_compressed('gdrive/My Drive/SEAM/data_test.npz', data_test= dat_test);

DATA_URL3 = 'https://datasets.aicrowd.com/default/aicrowd-public-datasets/seamai-facies-challenge/v0.1/public/data_train.npz';
path_train_data = tf.keras.utils.get_file('datasets3', DATA_URL3)
data_train= np.load(path_train_data);

dat_train= data_train['data']

df_train_data= pd.DataFrame(dat_train[:,0,:])
df_train_data.head(10)

np.savez_compressed('gdrive/My Drive/SEAM/data_train.npz', data_train= dat_train);

DATA_URL4 = 'https://datasets.aicrowd.com/default/aicrowd-public-datasets/seamai-facies-challenge/v0.1/public/sample_submission_1.npz';
path_sample_sub = tf.keras.utils.get_file('datasets4', DATA_URL4)
data_sample_sub= np.load(path_sample_sub);

data_sample_sub

dat_sub= data_sample_sub['prediction']

df_sub_data= pd.DataFrame(dat_sub[:,0,:])
df_sub_data.head(10)

np.savez_compressed('gdrive/My Drive/SEAM/sample_submission_data.npz', sample_sub= 'dat_sub');

print(dat_sub.shape);
print(dat_train.shape);
print(dat_test.shape);
print(dat.shape)

TRAIN_DATASET_PATH =  'gdrive/My Drive/SEAM/data_train.npz';
TRAIN_LABELS_PATH = 'gdrive/My Drive/SEAM/labels_train.npz';
TEST_DATASET_PATH = 'gdrive/My Drive/SEAM/data_test.npz';

# Load train dataset
train_dataset = np.load(TRAIN_DATASET_PATH, allow_pickle=True, mmap_mode='r')
train_dataset = train_dataset["data_train"]

# Load train labels
train_labels = np.load(TRAIN_LABELS_PATH, allow_pickle=True, mmap_mode='r')
train_labels = train_labels["labels"]

# Load test dataset
test_dataset = np.load(TEST_DATASET_PATH, allow_pickle=True, mmap_mode = 'r')
test_dataset = test_dataset["data_test"]

print(train_dataset.shape)
print(test_dataset.shape);
print(train_labels.shape)

df_train= pd.DataFrame(train_dataset[:,0,:]);
df_test= pd.DataFrame(test_dataset[:,0,:]);
df_train_labels= pd.DataFrame(train_labels[:,0,:]);
print(df_train.head(4));
print(df_test.head(4));
print(df_train_labels.head(4));

import matplotlib.pyplot as maps;

fig= maps.Figure(figsize= (15,10))
ax= fig.subplots(1,1,);
#ax= fig.add_subplot(111);
ax.imshow(train_dataset[:,100,:], cmap= 'binary');
maps.show()

fig_labels= maps.Figure(figsize= (6,10))
ax= fig_labels.add_subplot();
ax.imshow(train_labels[:,100,:]);
maps.show()

maps.rcParams["figure.figsize"] = (15, 10)
f, axarr = maps.subplots(1,2)
axarr[0].imshow(train_labels[:, 100, :])
axarr[1].imshow(train_dataset[:, 100, :], cmap= 'binary')

"""Using Principal Component Analysis (PCA) could be a good option to reduce the amount of data for training the net."""

'''
A= train_labels[:, 100, :];
N= 400; # number of dimensions to be taken
A= A.T;
C= np.matmul(A, np.transpose(A))
u,e,vh= np.linalg.svd(C); # This step is time taking and should not be run multiple 
# times, prefer commenting it after execution
Diag_e= e;
s_e= 0;
p= [];
ts_e= np.sum(e);
for i in range(0, len(e)):
    s_e= s_e+ e[i];
    p.append(s_e/ts_e);

e= Diag_e;
e= np.diag(e);
c= np.matmul(u[:,0:N],np.matmul(e[0:N,0:N], vh[0:N,:]));  # Mode 1
Z= np.matmul(A.T,u[:,0:N]);
Ax= np.matmul(Z, np.transpose(u[:,0:N]))
Ax= Ax.T
'''

'''maps.rcParams["figure.figsize"] = (15, 10)
f, axarr = maps.subplots(1,2)
axarr[0].imshow(Ax.T)
axarr[1].imshow(train_dataset[:, 100, :], cmap= 'binary')'''

"""The aboce images give quite an indication that PCA cannot solve the problem. Data might be compressed but it can take a toll on accuracy.

Let's start with a simple CNN that takes in the image and predicts the labels.

There are two ways for this method as well. Simply taking each image and working on it, or taking 3 or 5 sections and using them as a multiple channels for the input. The input and output sections will have to be padded then. Before starting do not forget the data is in the shaepe (Z,X,Y).
"""

# Taking a single section
# For now, we will make vertical slices along X-axis. Since CNN takes input in the format (m, n_x, n_y, n_c).
# For now n_c= 1
# The dimension of each image will therefore be (X,Z,1) and there will be Y samples.
# Initial shape= (Z,X,Y)
print(train_dataset.shape);
train_data= np.moveaxis(train_dataset, 0, -1);
train_data= np.moveaxis(train_data, 0, 1);
print(train_data.shape);
# The data is now in the shape (Y,X,Z)
train_data= np.reshape(train_data, (590, 782, 1006, 1));
print(train_data.shape);
# Channels made, the data is now good for training.
# Ohh wait, we forgot to reshape the labels

print(train_labels.shape);
labels= np.moveaxis(train_labels, 0, -1);
labels= np.moveaxis(labels, 0, 1);
labels= np.reshape(labels, (590, 782, 1006, 1));
print(labels.shape);

# Let's check if we've done the right way
maps.rcParams["figure.figsize"] = (15, 10)
f, axarr = maps.subplots(1,2)
axarr[0].imshow(labels[:, 100, :,0])
axarr[1].imshow(train_data[:, 100, :, 0], cmap= 'binary')

maps.rcParams["figure.figsize"] = (15, 10)
f, axarr = maps.subplots(1,2)
axarr[0].imshow(labels[:, 100, :,0].T)
axarr[1].imshow(train_data[:, 100, :, 0].T, cmap= 'binary')
# Here we go...

# CNN model
inputs= tf.keras.Input(shape= (782, 1006, 1), name= 'Input');

conv1 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
conv1 = tf.keras.layers.BatchNormalization()(conv1)
conv1 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
conv1 = tf.keras.layers.BatchNormalization()(conv1)

pool1 = tf.keras.layers.MaxPooling2D((2, 2))(conv1) # Downsampling

conv2 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
conv2 = tf.keras.layers.BatchNormalization()(conv2)

pool2 = tf.keras.layers.MaxPooling2D((2, 2))(conv2) # Downsampling

conv3 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(pool2)
conv3 = tf.keras.layers.BatchNormalization()(conv3)
conv3 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(conv3)
conv3 = tf.keras.layers.BatchNormalization()(conv3)

pool3 = tf.keras.layers.MaxPooling2D((2, 2))(conv3) # Downsampling

conv4 = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same')(pool3)
conv4 = tf.keras.layers.BatchNormalization()(conv4)

pool4 = tf.keras.layers.MaxPooling2D((2, 2))(conv4) #Downsampling

# DECODER

conv5 = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same')(pool4)
conv5 = tf.keras.layers.BatchNormalization()(conv5)

up1 = tf.keras.layers.UpSampling2D((2, 2))(conv5) # Upsampling
up1= tf.keras.layers.ZeroPadding2D(padding= ((1, 0), (1, 0)))(up1) # Zero Padding to correct the dimensions 

conv6 = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same')(up1)
conv6 = tf.keras.layers.BatchNormalization()(conv6)

up2= tf.keras.layers.UpSampling2D((2, 2))(conv6)
up2= tf.keras.layers.ZeroPadding2D(padding= ((1, 0), (1, 0)))(up2) # Zero Padding to correct the dimensions 
#up2 = tf.keras.layers.concatenate([tf.keras.layers.UpSampling2D((1, 1))(conv6), conv4], axis=-1) # Upsampling and skipping

conv7 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(up2)
conv7 = tf.keras.layers.BatchNormalization()(conv7)
#conv7 = tf.keras.layers.Dropout(0.2)(conv7)
conv7 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(conv7)
conv7 = tf.keras.layers.BatchNormalization()(conv7)

up3 = tf.keras.layers.UpSampling2D((2, 2))(conv7) # Upsampling
up3= tf.keras.layers.ZeroPadding2D(padding= ((1, 0), (1, 0)))(up3) # Zero Padding to correct the dimensions 

conv8 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(up3)
conv8 = tf.keras.layers.BatchNormalization()(conv8)
conv8 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(conv8)
conv8 = tf.keras.layers.BatchNormalization()(conv8)

up4= tf.keras.layers.UpSampling2D((2, 2))(conv8)
#up4 = tf.keras.layers.concatenate([tf.keras.layers.UpSampling2D((2, 2))(conv8), conv2], axis=-1) # Upsampling and skipping

conv9 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(up4)
conv9 = tf.keras.layers.BatchNormalization()(conv9)
conv9 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(conv9)
conv9 = tf.keras.layers.BatchNormalization()(conv9)

up5= tf.keras.layers.UpSampling2D((1, 1))(conv9)

conv10 = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(up5)
conv10 = tf.keras.layers.BatchNormalization()(conv10)
conv10 = tf.keras.layers.Conv2D(8, (3, 3), activation='relu', padding='same')(conv10)
conv10 = tf.keras.layers.BatchNormalization()(conv10)
conv10 = tf.keras.layers.Conv2D(4, (3, 3), activation='relu', padding='same')(conv10)
conv10 = tf.keras.layers.BatchNormalization()(conv10)

outputs = tf.keras.layers.Conv2D(1, (1, 1) , padding='same')(conv10) # Getting the last layers with the 6 classes

model= tf.keras.Model(inputs= inputs, outputs= outputs, name= 'simple_CNN_Model');

# Let's view the model
tf.keras.utils.plot_model(model, show_shapes= True)
model.summary()

tf.keras.utils.plot_model(model, show_shapes= True)

# updatable plot
# a minimal example (sort of)

class PlotLosses(tf.keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []
        
        self.fig = maps.Figure()
        
        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        
        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        self.i += 1
        
        clear_output(wait=True)
        maps.plot(self.x, self.losses, label="loss")
        maps.plot(self.x, self.val_losses, label="val_loss")
        maps.legend()
        maps.show();
        
plot_losses = PlotLosses()

model.compile(optimizer= tf.keras.optimizers.Adamax(learning_rate= 0.01), loss= 'mean_squared_error', metrics= ["accuracy"])

batch_size= 1
history= model.fit(x= train_data, y= labels, 
                      batch_size= batch_size, epochs= 2, 
                      validation_data= (train_data[-100:-1], labels[-100:-1]), 
                      validation_batch_size= batch_size)

pre= model.predict(train_data[101:102,:,:,:])
pre= np.round(pre)
pre= np.array(pre, dtype= int)

maps.rcParams["figure.figsize"] = (15, 10)
f, axarr = maps.subplots(1,2)
axarr[0].imshow(labels[101, :, :,0].T)
axarr[1].imshow(pre[0,:,:,0].T)
# Here we go...

# Taking a single section
# For now, we will make vertical slices along X-axis. Since CNN takes input in the format (m, n_x, n_y, n_c).
# For now n_c= 1
# The dimension of each image will therefore be (X,Z,1) and there will be Y samples.
# Initial shape= (Z,X,Y)
print(test_dataset.shape);
test_data= np.moveaxis(test_dataset, 0, -1);
test_data= np.moveaxis(test_data, 0, 1);
print(test_data.shape);
# The data is now in the shape (Y,X,Z)
test_data= np.reshape(test_data, (251, 782, 1006, 1));
print(test_data.shape);
# Channels made, the data is now good for training.

test_label= model.predict(test_data[0:1,:,:,:]);

maps.rcParams["figure.figsize"] = (15, 10)
f, axarr = maps.subplots(1,2)
axarr[0].imshow(test_label[0,:,:,0].T)
axarr[1].imshow(test_data[0,:,:,0].T, cmap= 'binary')
# Here we go...

test_label= model.predict(test_data[0:1,:,:,:]);

pred= np.zeros_like(test_data);

for i in range(0, 251):
  dat1= test_data[i:i+1,:,:,:];
  pred_temp1 = model.predict(dat1);
  del dat1;
  pred[i,:,:,:]= np.round(pred_temp1);

pred= pred[:,:,:,0];
print(pred.shape);

pred= np.moveaxis(pred, 0, -1);
pred= np.moveaxis(pred, 0, 1);
print(pred.shape);

assert pred.shape == test_dataset.shape, "The shape of the prediction file does not match that of the test dataset."

print(pred.shape, np.unique(pred))

pred[pred == 7] = 6

pred= pred.astype(int)
print(pred.shape, np.unique(pred))