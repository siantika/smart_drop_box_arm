import sys
sys.path.append('drivers/sound')
from sound import Sound

DIR_OF_SOUND_FILES = './assets/sounds'
SOUND_FILE_NAME = 'sound_taruh_barang.wav'
sound = Sound()

sound.volume_control(65)

sound.play(DIR_OF_SOUND_FILES, SOUND_FILE_NAME) 

sound.stop()

