'''
    This class is storing LCD payload for lcd thread and sound files name
    for playing sound.

'''
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sound_assets_dir = os.path.join(parent_dir, './assets/sounds/')
class LcdData:
    TIMEOUT = {
    'cmd': 'keypad',
    'payload': ['INFO:', '-> WAKTU HABIS!']
    }
    ST_MSG = {
        'cmd': 'routine',
        'payload': ["Tekan keypad", "untuk memulai .."]
    }
    RESI_VALID = {
        'cmd': 'keypad',
        'payload': ["INFO:", "NO RESI VALID !."]
    }
    RESI_FAILED = {
        'cmd': 'keypad',
        'payload': ["STATUS:", "RESI TIDAK ADA"]
    }
    DOOR_ERROR = {
        'cmd': 'routine',
        'payload': ["WARNING:", "TUTUP PINTU!"]
    }
    NO_ITEM = {
        'cmd': 'routine',
        'payload': ["INFO:", "BRG TDK DISMPN !"]
    }
    THANKYOU = {
        'cmd': 'routine',
        'payload': ["  * DITERIMA *", "  Terima kasih!"]
    }
    NO_ITEM_RECEIVED = {
        'cmd': 'routine',
        'payload': ["WARNING:", "BRG TDK ADA!"]
    }
    ITEM_RECEIVED = {
        'cmd': 'routine',
        'payload': ['INFO:', '-> BOX SDH KOSONG']
    }
    NO_RESI_SUCCESS = {
        'cmd': 'keypad',
        'payload': ['STATUS:', ' RESI DITERIMA!']
    }
    GET_SUCCESS = {
        'cmd': 'routine',
        'payload': ['STATUS REQUEST:', ' Berhasil (200)!']
    }
    FISRT_INPUT_KEYPAD = {
        'cmd': 'keypad',
        'payload': ['Masukan resi:', '']
    }
    TAKING_ITEM = {
        'cmd': 'keypad',
        'payload': ['INFO:', '-> SILAKAN AMBIL']
    }
    AFTER_TAKING_ITEM = {
        'cmd': 'keypad',
        'payload': ['INFO:', '-> BRG DIAMBIL!']
    }
    ERROR_UNIVERSAL_PASSWORD = {
        'cmd': 'routine',
        'payload': ['ERROR:', 'Uni pass > 4 c!']
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