"""
Module: Sound driver
Author: I Putu Pawesi Siantika, S.T.
Date  : Feb 2023, refactored in Jul 2023

This module provides classes for simple operation that sound usually does
(play, stop, and volume control).
It works only for 'wav' file type and on machine that runs linux distros!

Classes:
- SoundInterface (abstract base class) = Represents sound interface.
- Aplay = Implementations for aplay package on linux
- AplaPlayMode = Implementations of play mode in aplay media player.
  It handles repetition mode of playing a sound
"""

import multiprocessing as mp
import os
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class SoundProcessing:
    """ Contains options flag for sound processing used in Aplay media player"""
    PCM = 'PCM'
    DAC = 'DAC'


class SoundInterface(ABC):
    """ Represents abstract base class for simple sound operations 
        ( play a sound, stop a sound, and control the sound-hardware's volume)"""
    @abstractmethod
    def play(self, file_name:Path)-> any:
        """ Plays a sound"""
        pass

    @abstractmethod
    def stop(self, process:any)-> None:
        """ Stops the ongoing sound """
        pass

    @abstractmethod
    def volume_control(self, level_percent:int) -> None:
        """ Controls the sound-hardware's volume"""
        pass


class Aplay(SoundInterface):
    """ 
        Implementation for media player using aplay package that
        compatible with linux distros.
    """

    def play(self, file_name:Path, blocking:bool= None,
             repeat:bool = False )-> mp.Process | None:
        """ 
            Plays a sound. Only support wav type.
                Args:
                    file_name (str) : file name of song and its path.
                    blocking (bool) : playing mode. Default is None (means
                    non blocking mode, if it is True = blocking, 
                    otherwise it is blocking)
                    repeat(bool) : enable 'repeat' playing sound
                Returns:
                    mp.Process object if non-blocking play or None if
                    blocking play.
        """
        play_mode = AplayPlayMode()
        if blocking:
            play_mode.play_blocking_mode(file_name)
        else:
            return play_mode.play_non_blocking_mode(file_name, repeat)

    def stop(self, sound_thread:mp.Process = None) -> None:
        """
            Stops ongoing sound by brute-forcing the process/task that playing
            sound file. Only valid in non-blocking mode.
                args:
                    sound_thread (mp.Process) : processing object of sound 
                    that playing.
        """
        if sound_thread == None:
            return None
        
        if sound_thread.is_alive():
            sound_thread.kill()
            time.sleep(0.3)

    def volume_control(self, level_percent:int, audio_processing:SoundProcessing)-> None:
        """
            Controls hardware volume level.
                args:
                    level_percent (int) : 0 (minimum) - 100 (max) (sound level range) 
                    audio_processing (str): 
        """
        convert_from_persen_to_sound_level = level_percent / 100 * 63
        convert_from_persen_to_sound_level = int(round(convert_from_persen_to_sound_level,0))
        subprocess.run(
            [
                'amixer','set', audio_processing, str(convert_from_persen_to_sound_level)
            ], check=True)


class AplayPlayMode:
    """ 
        Non blocking process is achieved by creating a separate task for each 
        sound file played. Stopping the sound need to be done by killing the task
        using PID returned from play method (in this clas, we use 'stop' method).
        It uses multiprocessing module/library for and Aplay package (media player).  
    """
    def _excute_aplay_subprocess(self, file_name:Path):
        """ excute subprocess that runs aplay method 
           to play a sound """
        subprocess.run([
            'aplay',
            str(file_name),
            ],)
        
    def _determinator_repeat(self, file_name:Path, repeat:bool=False)-> None:
        """ Determines the repetition for playing a sound.
            It is intended for non-blocking mode only.
        """
        if repeat:
            while True:
                self._excute_aplay_subprocess(file_name)
        else:
            self._excute_aplay_subprocess(file_name)


    def play_non_blocking_mode(self, file_name:Path, 
                               repeat:bool = False)-> mp.Process:
        """ 
        Plays a non-blocking sound by creating separate task.
            Args:
                file_name (Path) : full path of the sound file.
                repeat (bool) : Default is False. Indicator for
                determine the repetition of playing one sound
            Returns:
                A mp.Process objetc that runs the play-sound 
                thread.

        """
        sound_thread = mp.Process(target=self._determinator_repeat, 
                            args=(file_name, repeat, ))
        sound_thread.start()
        return sound_thread
    
    def play_blocking_mode(self, file_name:Path)->None:
        """ Plays the sound in blocking mode
            Args:
                file_name (Path) : full path of the sound file.
        """
        self._excute_aplay_subprocess(file_name)

# EOF