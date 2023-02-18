import sys
import subprocess
import os
import unittest
from unittest.mock import Mock, patch
sys.path.append('drivers/usb_camera') ### include the library, we want to test
from usb_camera import UsbCamera

"""
    This test requires USB CAMERA HARDWARE!.
    Methods with prefix 'test_' will be excetuded!
"""

device_address = '/dev/video0' ### in ASUS laptop, please check for other device
dir_saved_photo = './assets/photos/'
cmd_capture_photo = ['fswebcam','-d', str(device_address), '-r', '640x480', '--save', str(dir_saved_photo)+('%Y-%m-%d_%H-%M-%S.jpg')]

class TestUsbCamera(unittest.TestCase):
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

    
    def test_get_hardware_address_should_be_correct(self):
        self.set_up()
        assert cam._get_hw_addr() == device_address
        
    def test_set_dir_saved_photo_should_be_exist(self):
        self.set_up()
        cam.set_dir_saved_photo(dir_saved_photo)
    
    def test_get_dir_saved_photo_should_be_correct(self):
        self.set_up()
        cam.set_dir_saved_photo(dir_saved_photo)
        assert cam.get_dir_saved_photo() == dir_saved_photo

    ### Tests for capturing photo ###
    def test_capture_photo_should_be_accessing_cmd(self):
        if not os.path.exists(dir_saved_photo):
            self.create_photo_dir()
        self.set_dir_saved_photo()
        _ret_code = cam.capture_photo()
        assert _ret_code == 0        ### produces an image in directory
        self.del_photo_dir()

    def test_cmd_capture_photo_should_be_correct(self):  
        self.set_dir_saved_photo()
        assert cam._get_cmd_capture_photo() == cmd_capture_photo 
        

    def test_capture_photo_should_be_called_once(self):
        with patch('subprocess.run') as mock_subprocess_run:    
            self.set_dir_saved_photo()
            cam.capture_photo()
            mock_subprocess_run.assert_called_once_with(cmd_capture_photo) ### dont producing files

   
    def test_capture_photo_should_saved_captured_photo_in_correct_directory(self):
        self.create_photo_dir()
        cam.capture_photo()
        assert len(os.listdir(str(dir_saved_photo))) == 1
        self.del_photo_dir()

    @patch('os.remove')
    @patch('os.listdir')
    def test_should_be_able_to_delete_photo(self, mock_os_listdir, mock_os_remove):
        '''
            delete specific photo by file name
        '''
        mock_os_listdir.return_value = 1
        self.ret_code = cam.delete_photo('foto1.jpg')

        assert cam._file_name == 'foto1.jpg'
        assert cam._full_path_file == str(dir_saved_photo) + 'foto1.jpg'
        mock_os_remove.assert_called_once_with("./assets/photos/foto1.jpg")

    ### still can't find testing method for tr and except!, abandon this code! (next release will be fixed)
    # @patch('os.listdir')
    # def test_delete_photo_should_be_handled_no_file_correctly(self,  mock_os_listdir):
    #     '''
    #         when no file or directory for saving photo, raise an FileNotFoundError!
    #     '''
    #     mock_os_listdir.return_value = 0

    #     cam.delete_photo('foto1.jpg')

    #     assert

            

        





    

        