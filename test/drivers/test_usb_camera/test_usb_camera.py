import sys
sys.path.append('drivers/usb_camera')
from usb_camera import UsbCamera

# var
deviceAddres = '/dev/video0'

class TestUsbCamera:
    def setUp(self):
        global cam
        cam = UsbCamera(deviceAddres)
    
    def testGetHwAddressShouldBeCorrect(self):
        self.setUp()
        assert cam.getHwAddr() == deviceAddres



    

        