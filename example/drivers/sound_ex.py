import sys
sys.path.append('drivers/sound')
from sound import Sound

DIR_OF_SOUND_FILES = './assets/sounds'
SOUND_FILE_NAME = 'diterima.wav'
sound = Sound()

# sound.volume_control(65) ### [0 - 100 %]

sound.play(DIR_OF_SOUND_FILES, SOUND_FILE_NAME) 


### sound.stop() still error but not used for now.!!

