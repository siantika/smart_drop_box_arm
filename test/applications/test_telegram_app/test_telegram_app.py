import sys
sys.path.append('applications/telegram_app')
from telegram_app import TelegramApp

class TestTelegramApp:
    def test_telegram_app_should_has_attributes_correctly(self):
        """
            This constructor will receives 2 data, first is caption data
            (item_name, no_resi, and date_ordered) and second is photo file
            in binary format.
        """

        telegram = TelegramApp()

        assert hasattr(telegram, 'bot_token')
        assert hasattr(telegram, 'chat_id')
        assert hasattr(telegram, 'api_url')

    def test_bot_token_should_be_correct(self):
        telegram = TelegramApp()

        assert telegram.bot_token == "6056340407:AAEW9tR5pg7v22B23qMhLi3TVlY5eKly9qg"

    def test_chat_id_should_be_correct(self):
        telegram = TelegramApp()
        assert telegram.chat_id == '679839756'

    def test_api_url_should_be_correct(self):
        telegram = TelegramApp()
        assert telegram.api_url == 'https://api.telegram.org/bot6056340407:AAEW9tR5pg7v22B23qMhLi3TVlY5eKly9qg/sendPhoto'


    def test_send_post_request_to_telegram_api_should_be_correct(self):
        test_raw_caption = {'name': 'spidol',
                    'no_resi': '0025',
                    'date_ordered': '2023-03-01 10:18:45',
                    }
        with open('test/applications/test_telegram_app/test.jpg', 'rb') as f:
            test_bin_photo = f.read()

        telegram = TelegramApp()
        return_code = telegram.send_notification(test_raw_caption, test_bin_photo)
        assert return_code == 200

