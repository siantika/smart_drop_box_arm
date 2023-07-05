import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(parent_dir, 'drivers/sound'))
from sound import Aplay, SoundProcessing

DIR_OF_SOUND_FILES = './assets/sounds'
SOUND_FILE_NAME = 'diterima.wav'
sound = Aplay()
sound.volume_control(10, SoundProcessing.DAC)
