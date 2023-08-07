"""
    File: Sound driver example
    Author: I Putu Pawesi Siantika, S.T.
    Date: July 2023

    This file is intended for give an example about how
    to use sound driver (Aplay media player).

    Prerequisites:
        Packages:
            * aplay -> media player for linux distros
"""

import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/sound'))
from sound import Aplay, SoundProcessing
# specify sound folder and it's sound file name
DIR_OF_SOUND_FILES = './assets/sounds//'
DITERIMA_SOUND = DIR_OF_SOUND_FILES + 'diterima.wav'
INSTRUKSI_SOUND = DIR_OF_SOUND_FILES + 'instruksi_hapus_item_di_app.wav'
# Create an object with Aplay media player
sound = Aplay()
# Adjust the hardware sound volume (native is PCM, SBC is DAC)
sound.volume_control(10, SoundProcessing.PCM)
# Play the first sound in blocking mode
pid1 = sound.play(DITERIMA_SOUND, True)
# Play the second sound in non-blocking mode.
pid2 = sound.play(INSTRUKSI_SOUND) 
# We can do another tasks simultaneously while playing a sound.
print(" Hey, I just playing another task here ...")
time.sleep(1)
# Since we use the non-blocking mode, we can stop the sound in 
# the middle of sound duration
sound.stop(pid2)
# EOF
