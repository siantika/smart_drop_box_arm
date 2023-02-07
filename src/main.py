import sys
sys.path.insert(0,'drivers/usb_camera')
from usb_camera import UsbCamera

cam = UsbCamera('/dev/video2')

cam.setDirSavedPhoto('')
cam.capturePicture()
