'''
    we test existing code. So, i just test the required methods for orange pi zero and the project
    NOTE: Failed to test threading!
'''

import os
from unittest.mock import patch, call
import sys
import platform
import pytest
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'src/drivers/weight'))
sys.path.append(os.path.join(parent_dir, 'src/drivers/mock_wiringpi'))
from weight import *

TEST_PIN_PD_SCK = 10
TEST_PIN_DOUT = 9


class TestHx711:
    def set_up(self):
        self.weight = HX711Driver(TEST_PIN_DOUT, TEST_PIN_PD_SCK)
    
    def test_init_should_get_correct_args(self):
        """ Should get 2 pins for operating HX711 driver """
        weight = HX711Driver(9,10)
        assert weight._pin_dout == 9
        assert weight._pin_pd_sck == 10

    def test_init_should_initialize_hx711_lib(self):
        self.set_up()
        assert isinstance(self.weight._hx711, Hx711Lib)
    
    def test_reference_unit_should_called_correctly(self):
        """Mock Hx711 driver"""
        patcher1 = patch('weight.Hx711Lib.set_reference_unit')
        mock_ref_unit_lib = patcher1.start()

        self.set_up()
        self.weight.set_reference_unit(113)
        mock_ref_unit_lib.assert_called_once_with(113)
    
    def test_calibrate_sensor_should_called_correctly(self):
        """ Test calibrate-process in hx711 driver according to example code """
        patcher1 = patch('weight.Hx711Lib.reset')
        patcher2 = patch('weight.Hx711Lib.tare')
        mock_reset = patcher1.start()
        mock_tare = patcher2.start()
        
        self.set_up()
        self.weight.calibrate()
        mock_reset.assert_called_once()
        mock_tare.assert_called_once()

    def test_get_weight_should_called_correctly(self):
        patcher1 = patch('weight.Hx711Lib.get_weight')
        mock_get_weight = patcher1.start()
        self.set_up()
        self.weight.get_weight()
        mock_get_weight.assert_called_once()

    
    @pytest.mark.skipif(platform.machine() is not 'armv7l' , reason="requires arm environment")
    def test_get_weight_should_read_belows_zero(self):
        """ When no items put on sensor, sensor should return 0 reading value.
            Only test on orange pi zero board/other-SBC"""
        self.set_up()
        weight_val = self.weight.get_weight()
        assert weight_val < 1.0
         

    def test_power_up_should_called_correcly(self):
        patcher1 = patch('weight.Hx711Lib.power_up')
        mock_power_up = patcher1.start()
        self.set_up()
        self.weight.power_up()
        mock_power_up.assert_called_once()

    def test_power_down_should_called_correcly(self):
        patcher1 = patch('weight.Hx711Lib.power_down')
        mock_power_up = patcher1.start()
        self.set_up()
        self.weight.power_down()
        mock_power_up.assert_called_once()


        


