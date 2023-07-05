"""
Module: sound driver
author: I Putu Pawesi Siantika, S.T.
date  : Feb 2023, refactored in Jul 2023

This module provides classes for simple operation that sound usually does
(play, stop, and volume control).
It works only for 'wav' file!

Classes:
- SoundInterface (abstract base class) = Represents sound interface.
- Aplay = Implementation for aplay package on linux
- NonBlockingPlayInterface (abstract base class) = Represents non blocking 
  method interface for playing sound.
- NonBlockingAplay  = Implementation for aplay-play nonblocking play sound.

"""

import multiprocessing as mp
import os
import subprocess
from abc import ABC, abstractmethod

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class SoundProcessing:
    """ Contains options flag for sound processing used in Aplay"""
    PCM = 'PCM'
    DAC = 'DAC'


class SoundInterface(ABC):
    """ Represents abstract base class for simple sound operations"""
    @abstractmethod
    def play(self, file_name:str)-> int:
        """ plays a sound"""
        pass

    @abstractmethod
    def stop(self, pid:int)-> None:
        """ stops the ongoing sound """
        pass

    @abstractmethod
    def volume_control(self, level_percent:int) -> None:
        """ Controls hardware volume"""
        pass


class Aplay(SoundInterface):
    """ 
        Implementation for media player using aplay package that
        compatible with linux distros.
    """

    def play(self, file_name:str)-> int:
        """ 
            Plays a sound. Only support wav type.
                args:
                    file_name (str) : file name of song and its path
                returns:
                    pid of aplay executed (int)
        """
        non_block = NonBlockingAplay(file_name)
        pid = non_block.play_nonblocking()
        return pid

    def stop(self, pid:int) -> None:
        """
            Stops ongoing sound by brute-force the process to be killed
                args:
                    pid (int) : pid of aplay process that wants to be killed.
        """
        if pid != 0:
            pid_to_str = str(pid)
            subprocess.run(
                [
                'kill',
                '-9',
                pid_to_str,
                ]
            )

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


class NonBlockingPlayInterface(ABC):
    """
        Represents abstract base class for non blocking playing sound method.
    """
    def __init__(self, file_name:str) -> None:
        """ 
            Constructor checking file song.
                args:
                    file_name (str) : full path + file name of sound.
                raises:
                    FileNotFoundError : when path contains filename is not exist.
            """
        if file_name == "":
            raise FileNotFoundError("Name of file song must be filled !")
        self._file_name = file_name

    @abstractmethod
    def _play(self)->None:
        """ Represents private play method """
        pass

    @abstractmethod
    def play_nonblocking(self)->int:
        """ Represents play sound in non blocking process """
        pass


class NonBlockingAplay(NonBlockingPlayInterface):
    """ 
        Non blocking process is achieved by create a separate task for each 
        sound file played.    
    """

    def _play(self)-> None:
        """ Private method to play sound in aplay package """
        subprocess.run([
            'aplay',
            str(self._file_name),
            ],)

    def play_nonblocking(self)-> int:
        """ 
        Creates separate process to perform non-blocking operation
            returns:
                pid of aplay (int): 0 means no aplay is running, otherwise
                                it returns aplay PID.
        """
        thread = mp.Process(target=self._play)
        thread.start()
        process_aplay = subprocess.run([
            'pidof', 
            'aplay',
        ], stdout=subprocess.PIPE)
        aplay_pid = process_aplay.stdout.decode('utf-8')\
            .strip('\n')
        
        return 0 if aplay_pid == '' else int(aplay_pid)
