"""
    File           : Telgram app
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mei, 2023
    Description    : 

    This file is intended to perform telegram-functionality,
    such as, send data (text and photo ) to telegram-bot.

"""
import configparser
import datetime
import os
import requests
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')
sys.path.append(os.path.join(parent_dir, 'src/utils'))
# should put here!
import log
# Time out for sending request to telegram server
# in secs
REQUEST_TIME_OUT = 10 

# Utility functions
def read_config_file(option:str)-> str:
    """ Read intended data from config file """
    file = configparser.ConfigParser()
    file.read(full_path_config_file)
    raw_data =  file.get('telegram', str(option))
    return raw_data


class TelegramApp:
    """ Application for using telegram API throught 
        request HTTP. 
        By now, It only can send a notification (text and photo)
        to registered telegram-bot.
    """
    def __init__(self) -> None:
        """ Please write the telegram params inside config file 
        in section 'telegram' """
        self.bot_token = read_config_file('bot_token')
        self.chat_id = read_config_file('chat_id')
        base_api_url = read_config_file('api_url')
        relative_url = f"bot{self.bot_token}/"
        self.api_url = base_api_url + relative_url + "sendPhoto"

    def _write_caption_report(self, raw_data_caption:dict):
        '''
            Caption's format (weird indentation) affects the message's content display on phone.
            The rule for writing text in telegram message is in this ref: https://core.telegram.org/bots/api 
            (see formatting section)
        '''
        time_now = datetime.datetime.now()
        time_now_strf = time_now.strftime("%Y\\-%m\\-%d %H:%M:%S")
        caption = \
            f"*INFO \\!* \nBarang telah diterima \\!\n\
*Nama barang*  : _{raw_data_caption['item']}_ \n\
*No resi*          : _{raw_data_caption['no_resi']}_ \n\
*Tanggal tiba* : _{time_now_strf}_ \n "  
        return caption
    
    def send_notification(self, raw_caption:dict, bin_photo)-> int:
        '''
            Sends notification to registered telegram bot.
            Log the error message if error occurs.
            Args:
                raw_caption (dict)  : Description (name, no resi, and
                                      date ordered) will be displayed belos
                                      the photo /image.
                bin_photo           : Photo data in binary format.
            Returns:
                Http status code (int)
        '''
        caption = self._write_caption_report(raw_caption)
        try:
            resp = requests.post(self.api_url, 
                             data = {"chat_id" : self.chat_id, 
                                    "caption" : caption, 
                                    "parse_mode" : "MarkdownV2", 
                                    }, files = {"photo" : bin_photo}, timeout= REQUEST_TIME_OUT)
        except Exception as e:
            log.logger.exception(str(e))
        else:
            return resp.status_code
    

    
    
