import sys
from unittest.mock import call, patch

sys.path.append('drivers/indicator')
sys.path.append('drivers/mock_wiringpi')
from indicator import Indicator

### codintional include the wiringpi
if sys.argv == '--hw-orpi':    
    import wiringpi
else:        
    from mock_wiringpi import MockWiringPi
    wiringpi = MockWiringPi()

TEST_PIN = 2

TEST_OUTPUT_MODE = 1

TEST_WRITE_LOW = 0
TEST_WRITE_HIGH = 1


class TestIndicator:
    def help_mock_wiringpi_methods(self):
        self.patcher1 = patch('mock_wiringpi.MockWiringPi.wiringPiSetup')
        self.patcher2 = patch('mock_wiringpi.MockWiringPi.pinMode')
        self.patcher3 = patch('mock_wiringpi.MockWiringPi.digitalRead')
        self.patcher4 = patch('mock_wiringpi.MockWiringPi.digitalWrite')

        self.mock_wiringpi_wiringPiSetup = self.patcher1.start()
        self.mock_wiringpi_pinMode = self.patcher2.start()
        self.mock_wiringpi_digitalRead = self.patcher3.start()
        self.mock_wiringpi_digitalWrite = self.patcher4.start()

        
    def test_init_arguments_should_be_correct(self):
        indicator = Indicator(2)

        ### Asert
        assert indicator._pin == TEST_PIN

    def test_init_process_should_be_correct(self):
        self.help_mock_wiringpi_methods()
        indicator = Indicator(2)

        ### Assert
        self.mock_wiringpi_wiringPiSetup.assert_called_once()
        self.mock_wiringpi_pinMode.assert_called_once_with(TEST_PIN, TEST_OUTPUT_MODE) 
        self.mock_wiringpi_digitalWrite.assert_called_once_with(TEST_PIN, TEST_WRITE_LOW)
    
    def test_turn_on_indicator_should_be_correct(self):
        self.help_mock_wiringpi_methods()
        indicator = Indicator(2)

        indicator.turn_on()
        
        ### Assert
        self.mock_wiringpi_digitalWrite.assert_called_with(TEST_PIN, TEST_WRITE_HIGH)

    def test_turn_off_indicator_should_be_correct(self):
        self.help_mock_wiringpi_methods()
        indicator = Indicator(2)
        indicator.turn_off()
        
        ### Assert
        self.mock_wiringpi_digitalWrite.assert_called_with(TEST_PIN, TEST_WRITE_LOW)

    def test_read_indicator_in_state_on_should_be_correct(self):
        self.help_mock_wiringpi_methods()
        self.mock_wiringpi_digitalRead.return_value = 1
        indicator = Indicator(2)

        _ret_val = indicator.read_state()

        #Assert
        self.mock_wiringpi_digitalRead.assert_called_once_with(TEST_PIN)
        assert _ret_val == 1


    def test_read_indicator_in_state_off_should_be_correct(self):
        self.help_mock_wiringpi_methods()
        self.mock_wiringpi_digitalRead.return_value = 0
        indicator = Indicator(2)

        _ret_val = indicator.read_state()

        #Assert
        self.mock_wiringpi_digitalRead.assert_called_once_with(TEST_PIN)
        assert _ret_val == 0








