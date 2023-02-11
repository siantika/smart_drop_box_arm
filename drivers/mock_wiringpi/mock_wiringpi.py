'''
    This is a simple mock for wiringpi library
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

class GPIO:
    INPUT = 0
    OUTPUT = 1
    LOW = 0
    HIGH = 1