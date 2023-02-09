import sys
sys.path.insert(0,'drivers/lcd')
from lcd import Lcd

from time import sleep


lcd = Lcd(dev_addr=0x24, bus_line=0)
sleep(2)