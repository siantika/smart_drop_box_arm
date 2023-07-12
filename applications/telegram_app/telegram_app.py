"""
    File           : telegram_app.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Mei, 2023
    Description    : 

        Currently: Send notification with courier's photo to telegram bot using telegram API.
        The bot already created using BotFather in telegram. All bot's credentials are put in 
        config file.

    License: see 'licenses.txt' file in the root of project
"""
import configparser
import datetime
import os
import requests
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
full_path_config_file = os.path.join(parent_dir, 'conf/config.ini')
sys.path.append(os.path.join(parent_dir, 'utils'))

# should put here!
import log

class TelegramApp:
    def __init__(self) -> None:
        self.bot_token = self._read_config_file('bot_token')
        self.chat_id = self._read_config_file('chat_id')
        base_api_url = self._read_config_file('api_url')
        relative_url = f"bot{self.bot_token}/"
        self.api_url = base_api_url + relative_url + "sendPhoto"

    def _read_config_file(self, option:str)-> str:
        file = configparser.ConfigParser()
        file.read(full_path_config_file)
        raw_data =  file.get('telegram', str(option))
        return raw_data
    
    def _write_caption_report(self, raw_data_caption:dict):
        '''
            caption's format (weird indentation) affects the message's content display on phone.
            the rule for writing text in telegram message (ref: https://core.telegram.org/bots/api 
            in formatting section)

        '''
        time_now = datetime.datetime.now()
        time_now_strf = time_now.strftime("%Y\\-%m\\-%d %H:%M:%S")
        caption = \
            f"*INFO \\!* \nBarang telah diterima \\!\n\
*Nama barang*  : _{raw_data_caption['name']}_ \n\
*No resi*          : _{raw_data_caption['no_resi']}_ \n\
*Tanggal tiba* : _{time_now_strf}_ \n "  
        return caption
    
    def send_notification(self, raw_caption:dict, bin_photo)-> int:
        '''
            Call this function to send notification to telegram bot.
            
            Params:
                raw_caption (dict)  : data contained item description (name, no resi, date ordered)
                                      stored in RAM.
                bin_photo           : courier's photo in bin format.
        '''
        caption = self._write_caption_report(raw_caption)
        try:
            resp = requests.post(self.api_url, 
                             data = {"chat_id" : self.chat_id, 
                                    "caption" : caption, 
                                    "parse_mode" : "MarkdownV2", 
                                    }, files = {"photo" : bin_photo}, timeout= 30)
        except Exception as e:
            log.logger.exception(str(e))
        else:
            return resp.status_code
    

    
    
