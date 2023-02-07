import subprocess
import os

class UsbCamera:
   
    def __init__(self, dir_hw_addr):
        self.hw_addr = str(dir_hw_addr)   
   
    def get_hw_addr(self):
        return self.hw_addr

    def set_dir_saved_photo(self, dir_saved_photo):
       self._dir_saved_photo = dir_saved_photo
       
    def get_dir_saved_photo(self):
        return self._dir_saved_photo

    def get_cmd_capture_photo(self):
        return ['fswebcam', '-d', str(self.hw_addr), '-r', '640x480', '--save', str(self.get_dir_saved_photo())+('%Y-%m-%d_%H-%M-%S.jpg')]
    
    def capture_photo(self):
      _ret_code = subprocess.run(self.get_cmd_capture_photo())
      return _ret_code.returncode
    
    def delete_photo(self):
        if os.listdir(self.get_dir_saved_photo()):
            subprocess.run(['rm', '-rf', self.get_dir_saved_photo()])




        