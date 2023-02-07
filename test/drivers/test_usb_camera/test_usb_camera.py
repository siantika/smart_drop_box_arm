import sys
import subprocess
import os
from unittest.mock import Mock, patch
sys.path.append('drivers/usb_camera') ### include the library, we want to test
from usb_camera import UsbCamera

device_address = '/dev/video2' ### in ASUS laptop, please check for other device
dir_saved_photo = 'test/image_result/'
cmd_capture_photo = ['fswebcam','-d', str(device_address), '-r', '640x480', '--save', str(dir_saved_photo)+('%Y-%m-%d_%H-%M-%S.jpg')]

class TestUsbCamera:
    def set_up(self):
        global cam
        cam = UsbCamera(device_address)

    #helper function
    def set_dir_saved_photo(self):
        self.set_up()
        cam.set_dir_saved_photo(dir_saved_photo)

    def create_photo_dir(self):
        subprocess.run(['mkdir', dir_saved_photo]) ### create directory for saving a captured image

    def del_photo_dir(self):
        subprocess.run(['rm','-rf',dir_saved_photo]) ### delete image folder if there are dump-files in previous test

    
    def test_get_hardware_address_shouldbe_correct(self):
        self.set_up()
        assert cam.get_hw_addr() == device_address
        
    def test_set_dir_saved_photo_should_be_exist(self):
        self.set_up()
        cam.set_dir_saved_photo(dir_saved_photo)
    
    def test_get_dir_saved_photo_shouldbe_correct(self):
        self.set_up()
        cam.set_dir_saved_photo(dir_saved_photo)
        assert cam.get_dir_saved_photo() == dir_saved_photo

### Tests for capturing photo ###
    def test_capture_photo_shouldbe_accessing_cmd(self):
        if not os.path.exists(dir_saved_photo):
            self.create_photo_dir()
        self.set_dir_saved_photo()
        _ret_code = cam.capture_photo()
        assert _ret_code == 0        ### produces an image in directory
        self.del_photo_dir()

    def test_cmd_capture_photo_shouldbe_correct(self):
        with patch('subprocess.run') as mock_subprocess_run:   
            self.set_dir_saved_photo()
            assert cam.get_cmd_capture_photo() == cmd_capture_photo 
         

    def test_capture_photo_shouldbe_called_once(self):
        with patch('subprocess.run') as mock_subprocess_run:    
            self.set_dir_saved_photo()
            cam.capture_photo()
            mock_subprocess_run.assert_called_once_with(cmd_capture_photo) ### dont producing files

   
    def test_capture_photo_should_saved_captured_photo_in_correct_directory(self):
        self.create_photo_dir()
        cam.capture_photo()
        assert len(os.listdir(str(dir_saved_photo))) == 1
        self.del_photo_dir()


    def test_should_be_able_to_delete_photo(self):
        self.create_photo_dir()
        self.set_dir_saved_photo()
        cam.capture_photo()
        cam.delete_photo()
        assert os.path.exists(dir_saved_photo) == 0
        
        




    

        