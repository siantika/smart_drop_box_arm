'''
    File           : keypad.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
    This code just modification from "the ref" below. Basically, i just changed the RPi library
    to wiringOP. It can read a single char input from keypad 4x4. 

    * Prerequisites *
    1. Download or put this library in your working directory project.
    2. Import it to your project file (eg. main.py)

    Example code:
        see: './example/keypad_ex.py' file!

    License: see 'licenses.txt' file in the root of project

    ref: https://forum.armbian.com/topic/24562-armbian-orange-pi-read-matrix-keypad-4x4-in-python/


'''
 
import sys
import time
if '--hw-orpi' in sys.argv:
    import wiringpi 
    from wiringpi import GPIO
    
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class Keypad:
    def __init__(self, row_pin_array, column_pin_array):
        self._row_pin_array = row_pin_array
        self._column_pin_array = column_pin_array

       
        if not(len(self._row_pin_array) == 4 and len(self._column_pin_array) == 4):
            raise ValueError('the length of each arrays items should be 4 items')
        else:
            wiringpi.wiringPiSetup()

            wiringpi.pinMode(self._row_pin_array[0], GPIO.OUTPUT)
            wiringpi.pinMode(self._row_pin_array[1], GPIO.OUTPUT)
            wiringpi.pinMode(self._row_pin_array[2], GPIO.OUTPUT)
            wiringpi.pinMode(self._row_pin_array[3], GPIO.OUTPUT)

            wiringpi.pinMode(self._column_pin_array[0], GPIO.INPUT)
            wiringpi.pinMode(self._column_pin_array[1], GPIO.INPUT)
            wiringpi.pinMode(self._column_pin_array[2], GPIO.INPUT)
            wiringpi.pinMode(self._column_pin_array[3], GPIO.INPUT)

            wiringpi.pullUpDnControl(self._column_pin_array[0], GPIO.PUD_DOWN)
            wiringpi.pullUpDnControl(self._column_pin_array[1], GPIO.PUD_DOWN)
            wiringpi.pullUpDnControl(self._column_pin_array[2], GPIO.PUD_DOWN)
            wiringpi.pullUpDnControl(self._column_pin_array[3], GPIO.PUD_DOWN)

   
    def _read_line(self, line, chars):
        self._chars = chars
        self._line = line
        self._selected_char = None
        

        wiringpi.digitalWrite(self._line, GPIO.HIGH)

        if wiringpi.digitalRead(self._column_pin_array[0]) == 1:
            self._selected_char = self._chars[0]
        
        if wiringpi.digitalRead(self._column_pin_array[1]) == 1:
            self._selected_char = self._chars[1]

        if wiringpi.digitalRead(self._column_pin_array[2]) == 1:
            self._selected_char = self._chars[2]

        if wiringpi.digitalRead(self._column_pin_array[3]) == 1:
            self._selected_char = self._chars[3]
        
        wiringpi.digitalWrite(self._line, GPIO.LOW)

        return self._selected_char
    
    def reading_input_char(self):
        self._selected_char = None
        # while self._selected_char == None:
        self._selected_char = self._read_line(self._row_pin_array[0], ['1', '2', '3', 'A'])
        self._selected_char = self._read_line(self._row_pin_array[1], ['4', '5', '6', 'B'])
        self._selected_char = self._read_line(self._row_pin_array[2], ['7', '8', '9', 'C'])
        self._selected_char = self._read_line(self._row_pin_array[3], ['*', '0', '#', 'D'])            
        time.sleep(0.2)
        return self._selected_char
    
    



