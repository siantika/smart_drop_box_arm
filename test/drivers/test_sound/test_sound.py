from unittest.mock import patch, call
import os
import sys
import datetime
sys.path.append('drivers/sound')
import configparser
import subprocess
from sound import Sound
import shutil

class TestSound:
    def set_up(self):
        global sound
        sound = Sound()

    def tear_down(self):
        pass

    def test_init_process_should_be_correct(self):
        '''
            init process should:
            
            1. file's path = ./conf/sound_conf.txt
            2. Check whether conf file is exist
            3. if conf file is exist, call readFile
            4. data read should be correct, data are: volume (float) and card (str) : [0,1] 
        '''

        self.set_up()

        assert isinstance(sound._file, configparser.ConfigParser)        
        assert sound._volume == 50.2
        assert type(sound._volume) == float
        assert sound._sound_card == 'card 0'
        assert type(sound._sound_card) == str

        self.tear_down()
         
    def test_play_sound_should_be_correct(self):
        '''
            Create dir : ./assets/sound first
            Play method has 2 args, first is music's dir, and second is music file name.
            music file name should be .wav file.
            song should play once and full duration.

        '''
        self.set_up()
        self.patcher1 = patch('subprocess.run')
        self.mock_subproccess_run = self.patcher1.start()

        sound.play('./assets/sounds','sound_taruh_barang.wav')

        assert sound._sound_dir == './assets/sounds'
        assert sound._sound_file_name == 'sound_taruh_barang.wav'
        assert os.path.splitext(sound._sound_file_name)[-1] == '.wav'

        ### play a sound
        self.mock_subproccess_run.assert_called_once_with(['aplay', './assets/sounds/sound_taruh_barang.wav'])

        self.patcher1.stop()
        self.tear_down()

    def test_stop_sound_should_be_correct(self):
        '''
            kill the PID of aplay should success
            1. knowing the aplay pid
            2. kill the pid
        '''
        self.set_up()
        self.patcher1 = patch('subprocess.run')
        self.mock_subproccess_run = self.patcher1.start()

        sound.stop()

        self.mock_subproccess_run.assert_has_calls(
            [
                call(['pid_target=$(pidof aplay)']),
                call(['kill -9 $pid_target'])
            ]
        )
        self.tear_down()


    def test_volume_control_should_be_correct(self):
        '''
            Test DAC level (0-63 MAX).
            convert from 0 - 100% to 0-63,
            set DAC level using cmd 'amixer'

        '''
        self.set_up()
        self.patcher1 = patch('subprocess.run')
        self.mock_subproccess_run = self.patcher1.start()

        sound.volume_control(80)
        
        assert sound._convert_from_persen_to_sound_level == 50
        self.mock_subproccess_run.assert_called_once_with(['amixer', 'set', 'DAC', '50'])

        self.patcher1.stop()
        self.tear_down()
        

 


        

