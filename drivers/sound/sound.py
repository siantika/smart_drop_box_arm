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
        subprocess.run(['pid_target=$(pidof aplay)'])
        subprocess.run(['kill -9 $pid_target'])

    def volume_control(self, level_volume_persen):
        self._convert_from_persen_to_sound_level = level_volume_persen / 100 * 63
        self._convert_from_persen_to_sound_level = int(round(self._convert_from_persen_to_sound_level,0))
        
        subprocess.run(['amixer', 'set', 'DAC', str(self._convert_from_persen_to_sound_level)])

        