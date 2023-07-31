"""
Module: sound driver
Author: I Putu Pawesi Siantika, S.T.
Date  : Feb 2023, refactored in Jul 2023

This module provides classes for simple operation that sound usually does
(play, stop, and volume control).
It works only for 'wav' file type and on machine that runs linux distros!

Classes:
- SoundInterface (abstract base class) = Represents sound interface.
- Aplay = Implementation for aplay package on linux
- NonBlockingAplay = Operations in non blocking mode using Aplay media player.
  method interface for playing sound.
- BlockingAplay  = Operations in blocking mode using Aplay media player.
"""

import multiprocessing as mp
import os
import subprocess
from abc import ABC, abstractmethod
import time

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
    def _get_pid_aplay(self)-> int:
        """ Returns pid of current aplay
            Returns:
                pid of current aplay (int) : 0 means No aplay is running
                                        , otherwise it returns the pid of aplay.
        """
        process_aplay = subprocess.run([
            'pidof', 
            'aplay',
        ], stdout=subprocess.PIPE)
        pid = process_aplay.stdout.decode('utf-8')\
            .strip('\n')
        return 0 if pid == '' else int(pid)

    def play(self, file_name:str, blocking:bool= None,
             repeat:bool = None )-> mp.Process | None:
        """ 
            Plays a sound. Only support wav type.
                args:
                    file_name (str) : file name of song and its path.
                    blocking (bool) : playing mode. Default is None (means
                    non blocking mode, if it is True = blocking, 
                    otherwise it is blocking)
                    repeat(bool) : repeat playing the sound.
                returns:
                    pid of running aplay (int) for non-blocking mode,
                    returns None for blocking mode.
        """
        if blocking == None or blocking == False:    
            mode = NonBlockingAplay()
            sound_thread = mode.play(file_name, repeat)
            return sound_thread
        else:
            mode = BlockingAplay()
            mode.play(file_name)

    def stop(self, sound_thread:mp.Process = None) -> None:
        """
            Stops ongoing sound by brute-forcing the process/task that playing
            sound file. Only valid in non-blocking mode.
                args:
                    pid (int) : pid of aplay process that wants to be killed.
        """
        if sound_thread is None:
            return None
        
        if  sound_thread.is_alive() and sound_thread:
            non_block = NonBlockingAplay()
            non_block.stop(sound_thread)


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


class NonBlockingAplay:
    """ 
        Non blocking process is achieved by creating a separate task for each 
        sound file played. Stopping the sound need to be done by killing the task
        using PID returned from play method (in this clas, we use 'stop' method).
        It uses multiprocessing module/library for and Aplay package (media player).  
    """

    def play_execution(self, file_name:str, repeat:bool=False)-> None:
        """ Private method for playing sound in aplay media player """
        if repeat:
            while True:  
                subprocess.run([
                    'aplay',
                    str(file_name),
                    ],)
        else:
            subprocess.run([
                'aplay',
                str(file_name),
                ],)
    
    def _get_pid_aplay(self)-> int:
        """ Returns pid of current aplay
            Returns:
                pid of current aplay (int) : 0 means No aplay is running
                                        , otherwise it returns the pid of aplay.
        """
        # Put some delay for processing
        time.sleep(0.3)
        process_aplay = subprocess.run([
            'pidof', 
            'aplay',
        ], stdout=subprocess.PIPE)
        pid = process_aplay.stdout.decode('utf-8')\
            .strip('\n')
        return 0 if pid == '' else int(pid)

    def play(self, file_name:str, repeat:bool = False)-> mp.Process:
        """ 
        Plays a non-blocking sound by creating separate task.
            Args:
                file_name (str) : full path of the sound file.
            Returns:
                pid of aplay (int): 0 means no aplay is running,
                                   otherwise it returns aplay PID.
        """
        sound_thread = mp.Process(target=self.play_execution, 
                            args=(file_name, repeat, ))
        sound_thread.start()
        # get a current aplay pid
        return sound_thread
    
    def stop(self, sound_thread:mp.Process) -> None:
        """ 
            Stop the sound that playing in non-blocking mode 
            Args:
                sound_thread (mp.Process) : an object of mp.Process
                                            instance

        """
        sound_thread.kill()
        time.sleep(0.3)
            
        
    
class BlockingAplay:
    """ Plays a sound in blocking mode using Aplay package 
        We cannot stop the sound that playing in blocking mode.
    """
    def play(self, file_name:str)->None:
        """ Plays the sound in blocking mode
            Args:
                file_name (str) : full path of the sound file.
        """
        subprocess.run([
            'aplay',
            str(file_name),
            ],)
        
# EOF