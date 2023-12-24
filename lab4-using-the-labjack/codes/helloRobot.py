import u3

class robot:
    def __init__(self):
        self.labjack = u3.U3()
        
    def close(self):
        self.labjack.close()
                            
    def printAnalogIns(self):
        
        AIN0value = self.labjack.getAIN(0)
        AIN1value = self.labjack.getAIN(1)
        descriptor ='A0 = %5.3f volts, A1 = %5.3f volts ' % (AIN0value, AIN1value)
        print(descriptor)
       
    def setDAC0(self,voltage = 0):
        if voltage < 0:
            print('output voltage must be >= 0')
            return
        if voltage > 5:
            print('output voltage must be <= 5')
            return
        
        DAC0_VALUE = self.labjack.voltageToDACBits(voltage, dacNumber = 0, is16Bits = False)
        self.labjack.getFeedback(u3.DAC0_8(DAC0_VALUE))
       

    
myRobot = robot()
myRobot.setDAC0(3)
myRobot.close()