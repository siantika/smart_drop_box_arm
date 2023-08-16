"""
Module: test_camera
author: I Putu Pawesi Siantika, S.T.
date  : 2023

This module performs unit tests for camera driver.

Classes:
- TestUsbCamera : Common functionalities tests
- TestUsbCameraExecution: Capturing photo tests
- TestUsbDeletePhotod: Deleting photo tests.

"""
import os
import sys
import pytest 
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'src/drivers/camera'))

from camera import *

class TestUsbCamera:
    def set_up(self):
        self.cam_set = UsbCameraSetting()
        self.cam_set.resolution = CameraResolution._640x480
        self.cam = UsbCamera('/dev/video0', self.cam_set)

    def tear_down(self):
        del self.cam_set
        del self.cam

    def test_usb_camera_instance(self):
        self.set_up()
        assert isinstance(self.cam, Camera)
        self.tear_down()
    
    def test_camera_attributes(self):
        self.set_up()
        assert hasattr(self.cam, 'dir')
        self.tear_down()

    def test_camera_interface(self):
        self.set_up()
        self.cam.photo_directory = 'assets/photos'
        assert hasattr(self.cam, 'photo_directory')
        assert hasattr(self.cam, 'generate_file_name')
        assert hasattr(self.cam, 'capture_photo')
        assert hasattr(self.cam, 'get_all_photos_file_name')
        assert hasattr(self.cam, 'delete_photo')
        assert hasattr(self.cam, 'delete_all_photos')
        self.tear_down()

    def test_setter_method_photo_directory(self):
        '''setter should assign dir atttribute'''
        self.set_up()
        self.cam.photo_directory = './assets/photos'
        assert self.cam.dir == './assets/photos'
        self.tear_down()

    def test_setter_method_handle_none(self):
        '''Should raise a TypeError if photo directory attr hasn't not filled'''
        self.set_up()
        with pytest.raises(TypeError):
            dir =  self.cam.photo_directory
        self.tear_down()

    def test_getter_method_photo_directory(self):
        '''getter should return dir atttribute'''
        self.set_up()
        self.cam.photo_directory = 'assets/photos'
        ret = self.cam.photo_directory
        assert ret == 'assets/photos'
        self.tear_down()

    def test_generate_file_name(self):
        '''Should generate date-time format! '''
        self.set_up()
        ret = self.cam.generate_file_name()
        assert ret == datetime.now().strftime('%Y-%m-%d_%H-%M-%S.jpg')
        self.tear_down()

    def test_get_all_photos_name(self):
        '''Should return list of all photos name in photo directory'''
        # read photos for test reference
        full_path_photo = os.path.join(abs_path, "assets/photos")
        read_files = os.listdir(full_path_photo)
        
        # Test setup
        self.set_up()
        self.cam.photo_directory = 'assets/photos'

        ret = self.cam.get_all_photos_file_name()
        assert ret == read_files

    def test_delete_all_photos(self):
        '''Delete all photos in photo directory'''
        self.set_up()
        self.cam.photo_directory = 'assets/photos'
        self.cam.delete_all_photos()

        #check the number of files in photo directory folder
        full_path_photo = os.path.join(abs_path, "assets/photos")
        files = os.listdir(full_path_photo)

        #number should be 0 (empty)
        assert len(files) == 0
        self.tear_down()


class TestUsbDeletePhoto:
    def set_up(self):
        self.cam_set = UsbCameraSetting()
        self.cam_set.resolution = CameraResolution._640x480
        self.cam = UsbCamera('/dev/video0', self.cam_set)

    def tear_down(self):
        del self.cam_set
        del self.cam

    def _help_find_file_in_folder(self, folder_path, file_name):
        for file in os.listdir(folder_path):
            if file == file_name:
                return "File found !"
        return None  # File not found

    def test_delete_photo(self):
        '''Delete a specific photo file in photo directory folder'''
        self.set_up()
        self.cam.photo_directory = 'assets/photos'
        self.cam.capture_photo()
        # Since it only capture once, the new photo is located in index 0
        file_name = self.cam.get_all_photos_file_name()[0]
        self.cam.delete_photo(file_name)

        #check the number of files in photo directory folder
        full_path_photo = os.path.join(abs_path, "assets/photos")
        ret = self._help_find_file_in_folder(full_path_photo, file_name)
        assert ret == None
        self.tear_down()

    def test_delete_all_photos_handle_no_file(self):
        '''If no files inside photo directory folder,
           No error should be occured'''
        self.set_up()
        self.cam.photo_directory = 'assets/photos'
        self.cam.delete_all_photos()
        self.tear_down()

    def test_delete_photo_handle_no_file(self):
        '''If no files inside photo directory folder,
           it raises FileNotFound(inherit from os.remove)'''
        with pytest.raises(FileNotFoundError):
            self.set_up()
            self.cam.photo_directory = 'assets/photos'
            self.cam.delete_photo('test_photo.jpg')
            self.tear_down()


class TestUsbCameraExecution:
    def set_up(self):
        self.cam_set = UsbCameraSetting()
        self.cam_set.resolution = CameraResolution._640x480

    def tear_down(self):
        directory_path = './assets/photos'
        # List all files in the directory
        file_list = os.listdir(directory_path)
        # Loop through the files and remove each one
        for filename in file_list:
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                else:
                    print(f"Skipped: {file_path} (not a file)")
            except Exception as e:
                print(f"Error while removing {file_path}: {e}")
        del self.cam_set
        del self.cam

    def test_capture_photo(self):
        '''should capture photo successfully and returning 0'''
        self.set_up()
        self.cam = UsbCamera('/dev/video0', self.cam_set)
        self.cam.photo_directory = './assets/photos'
        ret = self.cam.capture_photo()[0]
        assert ret == 0
        self.tear_down()

    def test_capture_photo_no_camera(self):
        '''Returning 1 if no camera hardware was found on device'''
        self.set_up()
        self.cam = UsbCamera('/dev/videoasd0', self.cam_set)
        self.cam.photo_directory = './assets/photos'
        ret = self.cam.capture_photo()[0]
        assert ret == 1
        self.tear_down()

    def test_should_return_success_operation_and_saved_photo_dir(self):
        """ Should return success and correct photo-saved dir"""
        dir_saved_photo = None
        self.set_up()
        self.cam = UsbCamera('/dev/video0', self.cam_set)
        self.cam.photo_directory = './assets/photos'
        ret = self.cam.capture_photo()

        # Get photo file dir
        file_name = os.listdir(os.path.join(abs_path, self.cam.photo_directory))[0]
        dir_saved_photo = os.path.join(self.cam.photo_directory,
                                       file_name)
        assert ret[0] == 0
        assert ret[1] == str(dir_saved_photo)
        self.tear_down()
        

class TestEnumResolution:
    """ Tests enumeration of resolution for camera"""
    def test_with_exist_camera_resolution(self):
        """ Should returns 640x480 in string 
            (UsbCamera setting attribute)
        """
        camera_setting = UsbCameraSetting()
        camera_setting.resolution = CameraResolution._640x480
        camera = UsbCamera('/dev/video0', camera_setting)
        assert camera._setting.resolution == "640x480"

    def test_with_non_exist_camera_resolution(self):
        """ Should raise an Attribute Error"""
        with pytest.raises(AttributeError):
            camera_setting = UsbCameraSetting()
            camera_setting.resolution = CameraResolution.asdsa
            camera = UsbCamera('/dev/video0', camera_setting)




        
