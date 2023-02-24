import sys
import time
sys.path.append('drivers/lcd')
from lcd import Lcd


### var
PIN_DEV_ADDR = 0x27
BUS_I2C_DEV = 0 ### find in CLI 'i2cdetect -y 1' 1 = bus 1 if 0 = bus 0

lcd = Lcd(PIN_DEV_ADDR, BUS_I2C_DEV)

lcd.init_lcd()

lcd.write_text(0, ' Hello Basdfaadfsfsdfsdfsdfsdli ') ### line ([0,1]), text
lcd.write_text(1, 'Om Swastyastu')

time.sleep(2) ### delay for 2 secs

lcd.clear_lcd()
lcd.write_text(1, 'Om shanti 3x Om')