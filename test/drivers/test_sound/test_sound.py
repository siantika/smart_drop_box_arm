"""
Module: test sound driver
author: I Putu Pawesi Siantika, S.T.
date  : in July 2023

This module performs unit tests for sound driver.

Classes:
- TestSoundInterfaceInAplay: Test the interface methods in Aplay package 
- TestSoundPlayAplay: Test play sound method to able in non blocking process,
                      returns PID, and returns 0 (int) when file sound is not valid/exist. 
- TestStopSoundAplay: Test stop sound at the midle of sound, random duration stop,
                      and no sound is played.
- TestSoundProcessing: Test the processing sound data.
- TestVolumeControl: Test volume control in min, average, and max.
"""
import time
import sys
import os
import subprocess
import re
ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(ABS_PATH, 'drivers/sound'))
from sound import Aplay, SoundProcessing
import pytest

# Choose sound processing mode base on operating system
if sys.platform == 'armv7l':
    # default orange pi zero lts sound card
    SOUND_PROCESSING = SoundProcessing.DAC
else:
    SOUND_PROCESSING = SoundProcessing.PCM


class TestSoundInterfaceInAplay():
    def set_up(self):
        self.sound = Aplay()

    def tear_down(self):
        while True:     
            process_aplay = subprocess.run([
                'pidof', 
                'aplay',
            ], stdout=subprocess.PIPE)
            aplay_pid = process_aplay.stdout.decode('utf-8').strip('\n')
            if aplay_pid == '':
                break
            time.sleep(1)

    def test_sound_interface_in_aplay_should_be_correct(self):
        self.set_up()
        assert hasattr(self.sound, 'play')
        assert hasattr(self.sound, 'stop')
        assert hasattr(self.sound, 'volume_control')


class TestSoundPlayAplay:
    def set_up(self):
        self.sound = Aplay()

    def tear_down(self):
        ''' Make sure sound played until finished each of test case'''
        while True:     
            process_aplay = subprocess.run([
                'pidof', 
                'aplay',
            ], stdout=subprocess.PIPE)
            aplay_pid = process_aplay.stdout.decode('utf-8').strip('\n')
            if aplay_pid == '':
                break
            time.sleep(1)

    def test_sound_should_play_a_song_without_blocking(self):
        file_name1 = os.path.join(ABS_PATH, 'assets/sounds/ambil_barang.wav') 
        self.set_up()

        self.sound.play(file_name1)

        process = subprocess.run(
            [
                'pidof',
                'aplay',
            ], capture_output=True, text= True
        )

        assert process.stdout.strip('\n') != ''
        self.tear_down()
     
    def test_sound_play_should_return_pid(self):
        file_name1 = os.path.join(ABS_PATH, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        ret = self.sound.play(file_name1)
        assert isinstance(ret, int)
        self.tear_down()

    def test_sound_play_should_return_0_if_no_file_(self):
        self.set_up()
        ret = self.sound.play('no_file')
        assert ret == 0
        

class TestStopSoundAplay:
    def set_up(self):
        self.sound = Aplay()

    def tear_down(self):
        pass

    def test_sound_should_able_stop_song_correctly(self):
        file_name1 = os.path.join(ABS_PATH, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        pid = self.sound.play(file_name1)
        self.sound.stop(pid)
        #check pid again
        process_aplay = subprocess.run([
                'pidof', 
                'aplay',
            ], stdout=subprocess.PIPE)
        aplay_pid = process_aplay.stdout.decode('utf-8').\
            strip('\n')
        assert aplay_pid == ''

    def test_sound_should_able_stop_song_in_the_midle_of_song_correctly(self):
        file_name1 = os.path.join(ABS_PATH, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        pid = self.sound.play(file_name1)
        # let the song played half of duration(approx)
        time.sleep(0.5)
        # kill it
        self.sound.stop(pid)
        #check pid again
        process_aplay = subprocess.run([
                'pidof', 
                'aplay',
            ], stdout=subprocess.PIPE)
        aplay_pid = process_aplay.stdout.decode('utf-8').\
            strip('\n')
        assert aplay_pid == ''

    def test_sound_should_able_handling_when_song_isnot_played(self):
        self.set_up()
        self.sound.stop(0) # no song is played


class TestSoundProcessing:
    """ Should match existance of available sound processing modes"""
    def test_sound_processing_should_store_correct_value(self):
        assert SoundProcessing.DAC == 'DAC'
        assert SoundProcessing.PCM == 'PCM'


class TestVolumeControl:
    def set_up(self):
        self.sound = Aplay()

    def _help_get_sound_proccessing_level(self, sound_processing):
        """ Gets the level of volume (0-63 and not in percent)"""
        command = ['amixer', 'sget', sound_processing]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, _ = process.communicate()
        output = output.decode('utf-8')

        match = re.search(r'Front Left: Playback (\d+)', output)
        if match:
            value = int(match.group(1))            
        return value

    def test_volume_control_should_able_set_the_level_to_max(self):
        self.set_up()
        self.sound.volume_control(100, SOUND_PROCESSING)
        presentase_sound_processing_now = self._help_get_sound_proccessing_level(SOUND_PROCESSING)
        assert presentase_sound_processing_now == 63

    def test_volume_control_should_able_set_the_level_to_min(self):
        self.set_up()
        self.sound.volume_control(0, SOUND_PROCESSING)
        presentase_sound_processing_now = self._help_get_sound_proccessing_level(SOUND_PROCESSING)
        assert presentase_sound_processing_now == 0

    def test_volume_control_should_able_set_the_level_to_average(self):
        self.set_up()
        self.sound.volume_control(50, SOUND_PROCESSING)
        presentase_sound_processing_now = self._help_get_sound_proccessing_level(SOUND_PROCESSING)
        assert presentase_sound_processing_now == 32


        

