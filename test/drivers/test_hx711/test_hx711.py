'''
    we test existing code. So, i just test the required methods for orange pi zero and the project
    NOTE: Failed to test threading!
'''

from unittest.mock import patch, call
import sys
sys.path.append('drivers/hx711')
sys.path.append('drivers/mock_wiringpi')
from hx711 import Hx711



test_pd_sck = 10
test_pdo = 9


class TestHx711:
    def help_mock_wiringpi_methods(self):
        self.patcher1 = patch('mock_wiringpi.MockWiringPi.wiringPiSetup')
        self.patcher2 = patch('mock_wiringpi.MockWiringPi.pinMode')
        self.patcher3 = patch('mock_wiringpi.MockWiringPi.digitalRead')
        self.patcher4 = patch('mock_wiringpi.MockWiringPi.digitalWrite')
        self.patcher5 = patch('time.sleep')
        self.patcher6 = patch('threading.Lock')

        self.mock_wiringpi_wiringPiSetup = self.patcher1.start()
        self.mock_wiringpi_pinMode = self.patcher2.start()
        self.mock_wiringpi_digitalRead = self.patcher3.start()
        self.mock_wiringpi_digitalWrite = self.patcher4.start()
        self.mock_time_sleep = self.patcher5.start()
        self.mock_threading_lock = self.patcher6.start()


    def set_up(self):
        global sensor
        self.help_mock_wiringpi_methods()
        sensor = Hx711(test_pd_sck, test_pdo)

    def tear_down(self):
        patch.stopall()


