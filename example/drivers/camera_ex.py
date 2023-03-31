import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/usb_camera'))

from usb_camera import UsbCamera

### var
dir_hw_address = '/dev/video0' ### use 'lsusb /dev/vid*' to find usb camera's address
file_name_photo = '2023-03-19_18-48-09.jpg' ### please fill this var first
dir_saved_photo = './assets/photos/'

 
camera = UsbCamera(dir_hw_address)

### set directory path for saving photos
camera.set_dir_saved_photo(dir_saved_photo)

### capture photo and return the code (succeed = 1 || failed = 0)
status_captured = camera.capture_photo()


#get file name
file_name = camera.get_photo_name()
print(f"nama file: {file_name[0]}")

### wait until 5 secs then delete the photos
time.sleep(5)
# delete specific foto
#camera.delete_photo(file_name_photo)



# delete all photos
camera.delete_all_photos_in_folder()