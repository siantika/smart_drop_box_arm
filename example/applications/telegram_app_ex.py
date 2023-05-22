import sys 

sys.path.append('applications/telegram_app')
from telegram_app import TelegramApp

telegram = TelegramApp()

test_raw_data = {
    'name' : 'baju safari',
    'no_resi' : '0012',
}

with open('test/applications/test_telegram_app/test.jpg', 'rb') as f:
    bin_photo = f.read()

ret = telegram.send_notification(test_raw_data, bin_photo)
print(ret)

