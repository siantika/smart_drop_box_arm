'''
    This class is storing LCD payload for lcd thread and sound files name
    for playing sound.

'''
import configparser
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sound_assets_dir = os.path.join(parent_dir, './assets/sounds/')
sys.path.append(os.path.join(parent_dir, 'applications/display_app'))
full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')
from display_app import DisplayMode

""" Utility Functions """
def read_config_file(section:str, option:str)-> str:
    """ Read intended data from config file """
    file = configparser.ConfigParser()
    file.read(full_path_config_file)
    raw_data =  file.get(section, option)
    return raw_data


class LcdData:
    TIMEOUT = {
    'cmd': DisplayMode.NORMAL,
    'payload': ['INFO:', '-> WAKTU HABIS!']
    }
    ST_MSG = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["Tekan keypad", "untuk memulai .."]
    }
    RESI_VALID = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["INFO:", "NO RESI VALID !."]
    }
    RESI_FAILED = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["STATUS:", "RESI TIDAK ADA"]
    }
    DOOR_ERROR = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["WARNING:", "TUTUP PINTU!"]
    }
    NO_ITEM = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["INFO:", "BRG TDK DISMPN !"]
    }
    THANKYOU = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["  * DITERIMA *", "  Terima kasih!"]
    }
    NO_ITEM_RECEIVED = {
        'cmd': DisplayMode.NORMAL,
        'payload': ["WARNING:", "BRG TDK ADA!"]
    }
    ITEM_RECEIVED = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['INFO:', '-> BOX SDH KOSONG']
    }
    NO_RESI_SUCCESS = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['STATUS:', ' RESI DITERIMA!']
    }
    GET_SUCCESS = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['STATUS REQUEST:', ' Berhasil (200)!']
    }
    FISRT_INPUT_KEYPAD = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['Masukan resi:', '']
    }
    TAKING_ITEM = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['INFO:', '-> SILAKAN AMBIL']
    }
    AFTER_TAKING_ITEM = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['INFO:', '-> BRG DIAMBIL!']
    }
    ERROR_UNIVERSAL_PASSWORD = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['ERROR:', 'Uni pass > 4 c!']
    }
    UNREGISTERED_STATUS = {
        'cmd': DisplayMode.NORMAL,
        'payload': ['INFO:', 'UNREGISTERED !']
    }
    REGISTERED_STATUS = {
        'cmd' : DisplayMode.NORMAL,
        'payload' : ['REGISTERED TO', os.environ.get('OWNER')]
    }
    VERSION = {
        'cmd' : DisplayMode.NORMAL,
        'payload' : ['Smart Drop Box', read_config_file('device-info', 'version')]
    }

class SoundData:
    WARNING_DOOR_OPEN = os.path.join(sound_assets_dir,'tutup_pintu.wav')
    POSE_COURIRER = os.path.join(sound_assets_dir,'pose_kurir.wav')
    TAKING_PICTURE = os.path.join(sound_assets_dir,'ambil_foto.wav')
    PUT_ITEM = os.path.join(sound_assets_dir,'taruh_paket.wav')
    ACCEPTED_ITEM = os.path.join(sound_assets_dir,'diterima.wav')
    TAKING_ITEM = os.path.join(sound_assets_dir,'ambil_barang.wav')
    INSTRUCTION_DEL_ITEM = os.path.join(sound_assets_dir,'instruksi_hapus_item_di_app.wav')
    BARANG_BELUM_DITERIMA = os.path.join(sound_assets_dir,'belum_diterima.wav')