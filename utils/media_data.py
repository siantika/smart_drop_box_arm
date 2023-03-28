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
    WARNING_DOOR_OPEN = 'tutup_pintu.wav'
    POSE_COURIRER = 'pose_kurir.wav'
    TAKING_PICTURE = 'ambil_foto.wav'
    PUT_ITEM = 'taruh_paket.wav'
    ACCEPTED_ITEM = 'diterima.wav'
    TAKING_ITEM = 'ambil_barang.wav'
    INSTRUCTION_DEL_ITEM = 'instruksi_hapus_item_di_app.wav'