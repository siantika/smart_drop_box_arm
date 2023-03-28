'''
    File           : keypad.py
    Author         : I Putu Pawesi Siantika, S.T.
    Year           : Feb, 2023
    Description    : 
    
   This code helps to comunicate between keypad and orange pi. I use serial communication
   for this protocol between keypad and orange pi. The keypad will send a char (in truth is string) 
   with special chars "/r/n". So, we need to decode and strip that data and simply return it as str
   in Python.

    * Prerequisites *
    1. Download or put this library in your working directory project.
    2. Import it to your project file (eg. main.py)

    Example code:
        see: './example/keypad_ex.py' file!

    License: see 'licenses.txt' file in the root of project

    ref: https://forum.armbian.com/topic/24562-armbian-orange-pi-read-matrix-keypad-4x4-in-python/


'''
 
import sys
import serial
import platform

if platform.machine() == 'armv7l':
    import wiringpi 
    from wiringpi import GPIO
    
else:
    sys.path.append('drivers/mock_wiringpi')
    from mock_wiringpi import MockWiringPi, GPIO
    wiringpi = MockWiringPi()


class Keypad:
    def __init__(self,):
        self.ser = serial.Serial(
        port='/dev/ttyS1',  # UART1 on Orange Pi
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
        )       
    
    def reading_input_char(self):
        '''
            Reading input char from keypad. It uses serial com between keypad and this device
            (red: orange pi zero lts).
        
        '''
        char_data = None
        try:
            char_data = self.ser.readline().decode('utf-8').strip() 
        except UnicodeDecodeError as msg_error:
            print(f"Error keypad: {msg_error}")
        finally:
            if not isinstance(char_data, None):
                if len(char_data) == 0:   
                    char_data = None
            return char_data
    
    



