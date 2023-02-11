from unittest.mock import patch, call
import sys
sys.path.append('drivers/door')
sys.path.append('drivers/mock_wiringpi')
from door import Door


test_pin_door = 3
test_pin_sense_door = 4

class TestDoor:
    def help_mock_wiringpi_methods(self):
        self.patcher1 = patch('mock_wiringpi.MockWiringPi.wiringPiSetup')
        self.patcher2 = patch('mock_wiringpi.MockWiringPi.pinMode')
        self.patcher3 = patch('mock_wiringpi.MockWiringPi.digitalRead')
        self.patcher4 = patch('mock_wiringpi.MockWiringPi.digitalWrite')

        self.mock_wiringpi_wiringPiSetup = self.patcher1.start()
        self.mock_wiringpi_pinMode = self.patcher2.start()
        self.mock_wiringpi_digitalRead = self.patcher3.start()
        self.mock_wiringpi_digitalWrite = self.patcher4.start()


    def set_up(self):
        global door
        self.help_mock_wiringpi_methods()
        door = Door(test_pin_door, test_pin_sense_door)

    def tear_down(self):
        patch.stopall()


    def test_init_process_should_be_has_correct_arguments(self):
        '''
            When creating an object from door class, it should:
            1. Contains pin for door lock and sense_door's pin
            2. sense_door sensor should be 0 (door lock)
        '''
        self.set_up()

        assert door._pin_door_solenoid == test_pin_door
        assert door._pin_sense_door == test_pin_sense_door
        assert door._state_of_door == 0

        self.tear_down()

    def test_init_process_should_be_has_correct_method(self):
        '''
            init methods:
            1. wiringPiSetup() should be called once
            1. pin door = OUTPUT (1) and pin sense_door = INPUT (0)!
            2. Door lock should in lock mode (lock = LOW || unlock = HIGH) --> prevent door auto open 
               when device is restarted
            
        '''
        self.set_up()

        self.mock_wiringpi_wiringPiSetup.assert_called_once()
        self.mock_wiringpi_pinMode.assert_has_calls(
            [
                call(test_pin_door, 1),
                call(test_pin_sense_door, 0)
            ]
        )
        self.mock_wiringpi_digitalWrite.assert_called_once_with(test_pin_door,0)
        self.tear_down()

    def test_lock_door_should_be_correctly(self):
        '''
            
        '''
        self.set_up()
        door.lock_door()

        self.mock_wiringpi_digitalWrite.assert_called_with(test_pin_door, 0)

        self.tear_down()


    def test_unlock_door_should_be_correctly(self):
        '''
            
        '''
        self.set_up()
        door.unlock_door()

        self.mock_wiringpi_digitalWrite.assert_called_with(test_pin_door, 1)
        
        self.tear_down()

    
    def test_sense_door_state_should_be_correct(self):
        '''
            1. Testing acording digital read to pin sense_door
            2. return value should 1 (closed) adn 0 (open)
        '''
        self.set_up()
        ### sense door sensor tells the door is open 
        # should return 1 (hardware = normally closed)
        self.mock_wiringpi_digitalRead.return_value = 1
        ret_val = door.sense_door_state()
       
        assert ret_val == 1

        ### sense door sensor tells the door is close
        # should return 0 (hardware = normally closed)
        self.mock_wiringpi_digitalRead.return_value = 0
        ret_val = door.sense_door_state()

        assert ret_val == 0

        self.mock_wiringpi_digitalRead.assert_called_with(test_pin_sense_door)

        self.tear_down()


