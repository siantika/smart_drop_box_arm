'''
    This is a simple mock for wiringpi library using on native dev
    (Laptop)
'''

class MockWiringPi:

    def wiringPiSetup(self):
        return None

    def pinMode(self, pin, mode):
        return pin, mode

    def digitalWrite(self, pin, state):
        return pin, state

    def digitalRead(self, pin):
        '''
            return 0 = LOW || 1 = HIGH
        '''
        return 0
    
    def pullUpDnControl(self, pin, mode):
        return pin, mode

class GPIO:
    INPUT = 0
    OUTPUT = 1
    LOW = 0
    HIGH = 1
    PUD_OFF = 0
    PUD_DOWN = 1
    PUD_UP = 2