import sys
from unittest.mock import patch

import requests
sys.path.append('applications/telegram_app')
from telegram_app import TelegramApp

class TestTelegramApp:
    def test_telegram_app_should_has_attributes_correctly(self):
        """
            This constructor will receive 2 data, the first is caption data
            (item_name, no_resi, and date_ordered) and the second is photo file
            in binary format.
        """

        telegram = TelegramApp()

        assert hasattr(telegram, 'bot_token')
        assert hasattr(telegram, 'chat_id')
        assert hasattr(telegram, 'api_url')

    def test_send_post_request_to_telegram_api_should_be_correct(self):
        """ Should invoke requests.post method once """
        with patch.object(requests, 'post') as mock_req_post:
            mock_req_post.return_value.status_code = None
            test_raw_caption = {'item': 'spidol',
                        'no_resi': '0025',
                        'date_ordered': '2023-03-01 10:18:45',
                        }
            with open('test/applications/test_telegram_app/test.jpg', 'rb') as f:
                test_bin_photo = f.read()
            telegram = TelegramApp()
            return_code = telegram.send_notification(test_raw_caption, 
                                                     test_bin_photo)
            mock_req_post.assert_called_once()
            
            

