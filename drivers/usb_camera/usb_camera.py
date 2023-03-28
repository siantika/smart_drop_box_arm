import subprocess
import os

'''
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
    This code becomes a driver for usb camera (GEMBIRD) and linux-based orange pi board. It uses fswebcam
    package to run the command. It can capture a photo, store it, and delete it (specific file).
    The resolution is 640x480 and the file name generated automatically with the date-time when photo is captured.
    
    Tested on orange pi (armbian jammy 22-11.4) and amd (ubuntu 20.04 , arch linux).

    * Prerequisites *
    1. Install ffmpeg package for linux --> " sudo apt install ffmpeg -y " in CLI.
    2. Download or put this library in your working directory project.
    3. Import it to your project file (eg. main.py)

    Example code:
        see: './example/camera.py' file!

    License: see 'licenses.txt' file in the root of project

'''

class UsbCamera:
    def __init__(self, dir_hw_addr):
        '''
            desc    : initialize variable stored hardware's address for USB camera
            params  : dir_hw_addr (str) --> the address of usb cam (eg. /dev/video0)
            ret     : -
        '''
        self.hw_addr = str(dir_hw_addr)   
   
    def _get_hw_addr(self):
        return self.hw_addr
    
    def _get_cmd_capture_photo(self):
        return ['fswebcam', '-d', str(self.hw_addr), '-r', '640x480', '--save', str(self.get_dir_saved_photo())+('%Y-%m-%d_%H-%M-%S.jpg')]
    

    def set_dir_saved_photo(self, dir_saved_photo):
       self._dir_saved_photo = dir_saved_photo
       
    def get_dir_saved_photo(self):
        return self._dir_saved_photo


    def capture_photo(self):
        '''
            desc    : Capturing photos and save it to a choosed directory. Resolution of pict is 640x480. Photos name = date time.
            params  : -
            ret     : return_code (int)--> [succeeded: 0, failed: 1 ]
        '''
        _ret_code = subprocess.run(self._get_cmd_capture_photo())
        return _ret_code.returncode
    

    def delete_photo(self, file_name):    
        '''
            desc    : Deleting photos in choosed directory. 
            params  : file_name (str) --> eg. 'foto1.jpg'
            ret     : -
        '''
        self._file_name = file_name
        self._full_path_file = str(self.get_dir_saved_photo()) + str(file_name)

        try:             
            if os.listdir(self.get_dir_saved_photo()):
                os.remove(self._full_path_file)
        except FileNotFoundError as e:
            raise FileNotFoundError('No file was found!')
        

    def delete_all_photos_in_folder(self):
        '''
            desc    : Deleting all photos in the chosen directory. 
            params  : -
            ret     : -
        '''
        try:             
            files = os.listdir(self.get_dir_saved_photo())
            for file in files:
                os.remove(os.path.join(self.get_dir_saved_photo(), file))
        except FileNotFoundError as e:
            raise FileNotFoundError('No such directory was found!')
        
    
    def get_photo_name(self)-> list:
        '''
            desc    : Deleting all photos in the chosen directory. 
            params  : -
            ret     : list[str] files name or empty list
        '''
        files = os.listdir(self.get_dir_saved_photo())

        # print out the file names
        return files

                



        