import pytest




class UsbCamera:
    def __init__(self, dirHwAddr):
        self.hwAddr = dirHwAddr

    def getHwAddr(self):
        return self.hwAddr

 


        