from unittest.mock import patch, call
import time
import sys


sys.path.append('drivers/keypad')
sys.path.append('drivers/mock_wiringpi')

from keypad import Keypad


class TestKeypad:

    def help_mock_wiringpi_methods(self):
        self.patcher1 = patch('mock_wiringpi.MockWiringPi.wiringPiSetup')
        self.patcher2 = patch('mock_wiringpi.MockWiringPi.pinMode')
        self.patcher3 = patch('mock_wiringpi.MockWiringPi.digitalRead')
        self.patcher4 = patch('mock_wiringpi.MockWiringPi.digitalWrite')
        self.patcher5 = patch('mock_wiringpi.MockWiringPi.pullUpDnControl')

        self.mock_wiringpi_wiringPiSetup = self.patcher1.start()
        self.mock_wiringpi_pinMode = self.patcher2.start()
        self.mock_wiringpi_digitalRead = self.patcher3.start()
        self.mock_wiringpi_digitalWrite = self.patcher4.start()
        self.mock_wiringpi_pullUpDnControl = self.patcher5.start()

    def set_up(self):
        global keypad
        self.help_mock_wiringpi_methods()
        keypad = Keypad([2,3,4,5], [6,7,8,9]) ### 1st arg = L || 2nd arg = C

    def tear_down(self):
        patch.stopall()


    def test_init_process_should_be_correct(self):
        '''
            init process --> aray pin of L (row) 4 items, aray pin of C (column) 4 items, pin Mode for L
            is OUTPUT, C is INPUT (pull down).
        '''

        self.set_up()
     
        assert keypad._row_pin_array == [2,3,4,5]
        assert keypad._column_pin_array == [6,7,8,9]

        self.mock_wiringpi_wiringPiSetup.assert_called_once()
        self.mock_wiringpi_pinMode.assert_has_calls(
            [
                call(2,1), ### output mode
                call(3,1),
                call(4,1),
                call(5,1),   

                call(6,0), ### input mode
                call(7,0),
                call(8,0),
                call(9,0),                              
            ]
        )

        self.mock_wiringpi_pullUpDnControl.assert_has_calls(
            [
                call(6,1), ### input mode pull down (1) see mock_wiringpi lib !
                call(7,1),
                call(8,1),
                call(9,1),                              
            ]

        )

        self.tear_down()

    def test_init_proccess_should_handle_lenth_arrays_pin_correctly(self):
        '''
            the length of each array should not exceeding or least than 4.
        '''

        ### exceeding 4 items should raise an ValueError
        self.help_mock_wiringpi_methods()
        try:
            keypad = Keypad([2,2], [4,8,5,4,8,6,5,10,7])
        except ValueError as ve:
            assert str(ve) == 'the length of each arrays items should be 4 items'
        else:
            assert False

        self.tear_down()



    '''
    each keypad will be tested with hardware, dificukt to construct the tests since it paths many.
    
    '''
    def test_read_line_should_be_executed_correctly(self):
        '''
            just verify the methods called exactly
        '''
        self.set_up()
        keypad._read_line(1, ['1', '2', '3', 'A'])

        self.mock_wiringpi_digitalWrite.assert_has_calls(
            [
                call(1,1), # line 1 = HIGH
                call(1,0) # line 1 = LOW
            ]
        )
 