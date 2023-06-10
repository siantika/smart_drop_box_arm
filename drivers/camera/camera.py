"""
Module: camera_module
author: I Putu Pawesi Siantika, S.T.
date  : 2023

This module provides classes for capturing and managing photos using a camera.

Classes:
- Camera (abstract base class): Defines the common interface for cameras.
- UsbCamera (inherits Camera): Implementation of a USB camera (GEMBIRD brand).
- UsbCameraSetting: Settings for a USB camera.

"""
from abc import ABC, abstractmethod
import subprocess
import os

abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class Camera(ABC):
    """Abstract base class for a camera."""
    dir: str = None

    @property
    @abstractmethod
    def photo_directory(self) -> str:
        """Get the directory where photos are saved."""
        pass

    @photo_directory.setter
    @abstractmethod
    def photo_directory(self, directory: str) -> None:
        """Set the directory where photos are saved."""
        pass

    @abstractmethod
    def generate_file_name(self)-> str:
        '''Generate file name for a single photo'''
        pass

    @abstractmethod
    def capture_photo(self) -> str:
        """Capture a photo using the camera."""
        pass

    @abstractmethod
    def get_all_photos_file_name(self) -> list:
        """Get the file names of all saved photos in directory."""
        pass

    @abstractmethod
    def delete_photo(self, file_name: str) -> None:
        """Delete a specific photo by file name."""
        pass

    @abstractmethod
    def delete_all_photos(self) -> None:
        """Delete all photos in the photo directory."""
        pass


class UsbCameraSetting:
    """Setting for a USB camera."""

    res: str = None

    @property
    def resolution(self):
        """Get the resolution setting for the USB camera."""
        return self.res

    @resolution.setter
    def resolution(self, resolution):
        """Set the resolution setting for the USB camera."""
        self.res = resolution


class UsbCamera(Camera):
    """Implementation of a USB camera."""

    def __init__(self, hw_address, setting: UsbCameraSetting)-> None:
        """
        Initialize a USB camera instance.

        Args:
            hw_address: The hardware address of the USB camera.
            setting: The setting object for the USB camera.
        """
        self._hw_addr = str(hw_address)
        self._setting = setting

    @property
    def photo_directory(self)->str:
        """Get the directory where photos are saved."""
        if self.dir is None:
            raise TypeError('Photo directory should be filled!')
        return self.dir

    @photo_directory.setter
    def photo_directory(self, directory)-> None:
        """Set the directory where photos are saved."""
        self.dir = directory

    def generate_file_name(self) -> str:
        """Generate date-time format for file name.""" 
        file_name = '%Y-%m-%d_%H-%M-%S.jpg'
        return file_name

    def capture_photo(self)-> str:
        """Capture a photo using the USB camera.
           Return: success operation = 0,
                   failed operation  = 1
                   (int)
        """
        # create an absolute path for photo file
        abs_photo_path = os.path.join(self.dir, self.generate_file_name())
        ret_opt = subprocess.run([
            'fswebcam',                    # fswebcam package for Linux
            '-d',                          # camera device address
            self._hw_addr,
            '-r',                          # photo resolution
            self._setting.resolution,
            '--save',
            abs_photo_path
        ],capture_output=True, text=True, check=True)

        #add successful operation checking
        return 1 if 'stat: No such file or directory' in ret_opt.stderr \
            else 0
    
    def get_all_photos_file_name(self)-> list:
        """Get the file names of all saved photos."""
        full_path_photo = os.path.join(abs_path, self.dir)
        files = os.listdir(full_path_photo)
        return files
    
    def delete_all_photos(self)-> None:
        """Delete all photos in the photo directory folder."""
        full_path_photo = os.path.join(abs_path, self.dir)
        files = os.listdir(full_path_photo)
        for file in files:
            os.remove(os.path.join(full_path_photo, file))

    def delete_photo(self, file_name)-> None:
        """Delete a specific photo base on file name."""
        full_path_file = os.path.join(self.dir, file_name)
        os.remove(full_path_file)