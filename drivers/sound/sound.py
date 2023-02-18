'''
    File           : sound.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
    This code becomes a driver for sound and orange pi zero lts (armbian). It uses aplay and
    alsamixer packages. It can play sound (.wav only, using aplay in CLI), stop it (kill the process in CLI), and 
    control the volume (amixer in CLI). It loads config file in './conf/config.ini' (you have to create it manually). You can change the setting there
    (volume level and sound card). Here is the 'config.ini' content:
    #############################
        [setting]
        sound_card = card 0 
        volume = 50.2

    #############################
        sound_card --> you can see the list with "aplay -l" in CLI
        volume =  min 0 -- max 100% . but it converts to (1 - 63) based on orange pi zero lts

    Tested on orange pi (armbian jammy 22-11.4) and AMD (ubuntu 20.04 , arch linux, FAILED).

    * Prerequisites *
    1. 'config.ini' file then put in './conf/config.ini' dir.
    2. Download or put this library in your working directory project.
    3. Import it to your project file (eg. main.py)

    Example code:
        see: './example/sound_ex.py' file!

    License: see 'licenses.txt' file in the root of project

'''
import configparser
import datetime
import os
import subprocess


_SOUND_CONF_FILE_PATH = './conf/config.ini'
_SOUND_CONF_FILE_PATH_FALSE = './conf/confiasdg.ini' ### only for testing

class Sound:
    def __init__(self):
        self._now = datetime.datetime.now()

        self._file = configparser.ConfigParser()
        try:
            self._file.read(_SOUND_CONF_FILE_PATH)
            self._volume = self._file.getfloat('setting', 'volume')
            self._sound_card = self._file.get('setting', 'sound_card')

        except configparser.NoSectionError:
            if not os.path.exists('./log'):
                try:
                    os.makedirs('./log')

                except OSError as e:
                    print(e)

            with open('./log/log.txt', 'a') as file:
                file.write("["+self._now.strftime("%Y-%m-%d %H:%M:%S")+"]" + " -->  No config file was found!\n")

    
    def play(self, sound_dir, sound_file_name):
        self._sound_dir = sound_dir
        self._sound_file_name = sound_file_name

        subprocess.run(['aplay', str(self._sound_dir + "/" + self._sound_file_name)])

    def stop(Self):
        try:                
            subprocess.run(['pid_target=$(pidof aplay)'])
            subprocess.run(['kill -9 $pid_target'])
        except FileNotFoundError as e:
            print(e)

    def volume_control(self, level_volume_persen: int):
        self._convert_from_persen_to_sound_level = level_volume_persen / 100 * 63
        self._convert_from_persen_to_sound_level = int(round(self._convert_from_persen_to_sound_level,0))
        
        subprocess.run(['amixer', 'set', 'DAC', str(self._convert_from_persen_to_sound_level)])

        