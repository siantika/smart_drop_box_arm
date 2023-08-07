"""
Module: camera_ex.py
author: I Putu Pawesi Siantika, S.T.
date  : 2023

This module provides example how to use camera driver.

NOTE:
  + Don't forget to install 'fswebcam' package on your linux distro.

"""
import os
import sys
import time

# include camera driver using absolute path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(abs_path, 'drivers/camera'))

#Should invokde camera module below the sys.path.append!
from camera import UsbCamera, UsbCameraSetting

#Variable
dir_hw_address = '/dev/video0' ### use 'lsusb /dev/vid*' to find usb camera's address
file_name_photo = '2023-06-11_01-23-19.jpg' ### Fill this var with the precise file_name (see: /asssets/photos)
dir_saved_photo = './assets/photos/'
resolution = '680x480'

# Initialize object setting for USBcamera.
camera_setting = UsbCameraSetting()
# Set the picture resolution
camera_setting.resolution = resolution
# Create an UsbCamera object
camera = UsbCamera(dir_hw_address, camera_setting)
# Set directory path for saving photos (MUST fill this first)
camera.photo_directory=dir_saved_photo
# capture photo
ret_opt = camera.capture_photo()
# display status capture photo operation:
# if ret_opt = 1 means camera has problem
# if ret_opt = 0 means camera works.
print(f'Status capture photo operation: {ret_opt}')
# Get all photos file name in list
file_name = camera.get_all_photos_file_name()
print(f"File names: {file_name}")
#wait until 5 secs then delete the photos
time.sleep(5)
# delete specific foto. You must specified the file name of exist file in photo directory
# unles it will raise FileErrorNotFound
# Uncomment if you want to use it
#camera.delete_photo(file_name_photo)

# Delete all photos in photo directory folder
camera.delete_all_photos()

#EOF