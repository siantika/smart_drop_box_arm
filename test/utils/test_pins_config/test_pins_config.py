import sys
sys.path.append('utils')
from pins_config import PinsConfig


class TestPinsConfig:    
    def test_pins_from_pins_configuration_class_should_be_correct(self):
        PIN_PD_OUT = 9
        PIN_SCK = 10
        PIN_DOOR_LOCK = 7
        PIN_DOOR_SENSE = 5
       
        pins = PinsConfig()

        assert pins.PD_OUT_WEIGHT == PIN_PD_OUT
        assert pins.SCK_WEIGHT == PIN_SCK
        assert pins.GPIO_DOOR_LOCK == PIN_DOOR_LOCK
        assert pins.GPIO_DOOR_SENSE == PIN_DOOR_SENSE

    