import sys
import time
sys.path.append('drivers/usb_camera')
from usb_camera import UsbCamera

### var
dir_hw_address = '/dev/video0' ### use 'lsusb /dev/vid*' to find usb camera's address
file_name_photo = '' ### please fill this var first
dir_saved_photo = './assets/photos/'


camera = UsbCamera(dir_hw_address)

### set directory path for saving photos
camera.set_dir_saved_photo(dir_saved_photo)

### capture photo and return the code (succeed = 1 || failed = 0)
status_captured = camera.capture_photo()


### wait until 5 secs then delete the photos
time.sleep(5)
camera.delete_photo(file_name_photo)