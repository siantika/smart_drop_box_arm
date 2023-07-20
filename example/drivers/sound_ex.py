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
# Play the first sound
pid1 = sound.play(DITERIMA_SOUND)
# give delay for next command (it uses multithread)
# So we can simultaneously execute another syntax while plyaing a sound.
# play the second sound after the first sound is complete
# Since sound play created separate task for playing first song,
# we need to wait the first task  till finish, but we can do another tasks
# that including sound operations.
# Ex: I will print text after  I played first sound.
print("Just do another tasks ...")
time.sleep(1) # wait until 1 sec
pid2 = sound.play(INSTRUKSI_SOUND) 
while pid2 == 1:
    pid2 = sound.play(INSTRUKSI_SOUND)  
time.sleep(1)
# stop the second sound after 1 second
sound.stop(pid2)
# EOF
