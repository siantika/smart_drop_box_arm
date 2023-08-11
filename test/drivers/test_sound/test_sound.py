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
import pytest
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'src/drivers/sound'))
from sound import Aplay, SoundProcessing


class TestSoundInterfaceInAplay():
    """ Test the init state of Sound Interface class """
    def test_sound_interface_in_aplay_should_be_correct(self):
        sound = Aplay()
        assert hasattr(sound, 'play')
        assert hasattr(sound, 'stop')
        assert hasattr(sound, 'volume_control')


class TestSoundPlayAplay:
    """ Test sound aplay operations"""
    def set_up(self):
        self.sound = Aplay()
     
    def test_with_correct_file(self):
        """ Test with correct sound file (.wav)"""
        file_name1 = os.path.join(parent_dir, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        sound_thd = self.sound.play(file_name1)
        assert sound_thd.is_alive()
        # Clear the resources 
        self.sound.stop(sound_thd)

    def test_with_no_file(self):
        """ Test with no sound file 
            Do nothing
        """
        self.set_up()
        sound_thd = self.sound.play('no_file')
        # Clear the resources 
        self.sound.stop(sound_thd)

    def test_with_repeat_playing(self):
        """ Only able when using the non-blocking mode
            The sound should be played more than once.
            This test shows if this sound playing in non-blocking mode 
        """
        file_name1 = os.path.join(parent_dir, 
                                  'assets/sounds/ambil_barang.wav') 
        self.set_up()
        sound_thd = self.sound.play(file_name1, False, True)
        # The sound duration is not more than 2 secs,so
        # technically, we will wait until 5 secs and check
        # if the sound still playing (it repeats to playing the sound)
        time.sleep(6)
        # Clear the resources
        self.sound.stop(sound_thd)


class TestStopSoundAplay:
    """ Test the sound-stop operation with many conditions """
    def set_up(self):
        self.sound = Aplay()

    def test_sound_should_able_stop_song_correctly(self):
        file_name1 = os.path.join(parent_dir, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        sound_thread = self.sound.play(file_name1)
        self.sound.stop(sound_thread)
        assert sound_thread.is_alive() == False

    def test_sound_should_able_stop_song_in_the_middle_of_sound_correctly(self):
        file_name1 = os.path.join(parent_dir, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        sound_thread = self.sound.play(file_name1)
        # let the song played half of duration(approx)
        time.sleep(1)
        # stop it 
        self.sound.stop(sound_thread)
        print(sound_thread)

    def test_stop_sound_with_no_sound_playing_sound(self):
        """ It should do nothing and not crashing the program """
        self.set_up()
        self.sound.stop()


class TestSoundProcessing:
    """ Should match existance of available sound processing modes"""
    def test_sound_processing_should_store_correct_value(self):
        assert SoundProcessing.DAC == 'DAC'
        assert SoundProcessing.PCM == 'PCM'


""" Execeute the tests only in arm board (32 bit)"""
@pytest.mark.skipif(sys.platform != 'armv7l', reason="requires arm board environment (32 bit)")
class TestVolumeControl:   
    """ Using DAC method for producing sound in sbc's sound card"""
    ARM_SOUND_PROCESSING =SoundProcessing.DAC

    def set_up(self):
        self.sound = Aplay()

    def _help_get_sound_proccessing_level(self, SOUND_PROCESSING):
        """ Gets the level of volume (0-63 and not in percent)"""
        command = ['amixer', 'sget', SOUND_PROCESSING]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, _ = process.communicate()
        output = output.decode('utf-8')

        match = re.search(r'Front Left: Playback (\d+)', output)
        if match:
            value = int(match.group(1))            
        return value

    def test_volume_control_should_able_set_the_level_to_max(self):
        self.set_up()
        self.sound.volume_control(100, self.ARM_SOUND_PROCESSING)
        presentase_sound_processing_now = self._help_get_sound_proccessing_level(self.ARM_SOUND_PROCESSING)
        assert presentase_sound_processing_now == 63

    def test_volume_control_should_able_set_the_level_to_min(self):
        self.set_up()
        self.sound.volume_control(0, self.ARM_SOUND_PROCESSING)
        presentase_sound_processing_now = self._help_get_sound_proccessing_level(self.ARM_SOUND_PROCESSING)
        assert presentase_sound_processing_now == 0

    def test_volume_control_should_able_set_the_level_to_average(self):
        self.set_up()
        self.sound.volume_control(50, self.ARM_SOUND_PROCESSING)
        presentase_sound_processing_now = self._help_get_sound_proccessing_level(self.ARM_SOUND_PROCESSING)
        assert presentase_sound_processing_now == 32


class TestBlockingAplay:
    """ Test the blocking method using Aplay.
        The method only 'play' """
    def set_up(self):
        self.sound =Aplay()

    def test_with_correct_sound_file_and_blocking_mode_set_to_true(self):
        """ Should play the sound file in blocking mode """
        file_name1 = os.path.join(parent_dir, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        start_time = time.time()
        self.sound.play(file_name1, True)
        end_time = time.time()
        execution_time = end_time - start_time

        # If the method is blocking, the execution time should be close to the duration of the sound file
        # You may want to set a threshold to account for minor variations in execution time
        expected_duration = 1.0  # Replace with the actual duration of your test sound file
        assert execution_time  > expected_duration

    def test_with_correct_sound_file_and_nonblocking_mode_set_to_false(self):
        """ time excution should below expected_duration (non-blocking) """
        file_name1 = os.path.join(parent_dir, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        start_time = time.time()
        sound_thread = self.sound.play(file_name1, False)
        end_time = time.time()
        execution_time = end_time - start_time

        # If the method is blocking, the execution time should be close to the duration of the sound file
        # You may want to set a threshold to account for minor variations in execution time
        expected_duration = 1.0  # Replace with the actual duration of your test sound file
        assert execution_time  < expected_duration
        # Clean the task by stop it so it doesn't affect next test.
        time.sleep(1.0)
        self.sound.stop(sound_thread)

    def test_with_correct_sound_file_and_nonblocking_mode_default(self):
        """ time excution should below expected_duration (non-blocking) """
        file_name1 = os.path.join(parent_dir, 'assets/sounds/ambil_barang.wav') 
        self.set_up()
        start_time = time.time()
        sound_thread = self.sound.play(file_name1)
        end_time = time.time()
        execution_time = end_time - start_time

        # If the method is blocking, the execution time should be close to the duration of the sound file
        # You may want to set a threshold to account for minor variations in execution time
        expected_duration = 1.0  # Replace with the actual duration of your test sound file
        assert execution_time  < expected_duration
        # Clean the task by stoping it so it doesn't affect next test.
        time.sleep(1.0)
        self.sound.stop(sound_thread)
