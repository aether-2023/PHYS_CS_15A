import u3
import time
import numpy as np
import matplotlib.pyplot as plt

class robot:
    def __init__(self):
        self.labjack = u3.U3()
        
        self.resistance = 500  #in Ohms
        
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
       
    def blink(self,numBlinks = 3):
        for i in range(numBlinks):
            self.setDAC0(3)
            time.sleep(0.5)
            self.setDAC0(0)
            time.sleep(0.5)
    def digitalBlink(self,numBlinks = 3):
        for i in range(numBlinks):
            self.labjack.setFIOState(4,0)
            time.sleep(0.5)
            self.labjack.setFIOState(4,1)
            time.sleep(0.5)          
    def takeIVCurve(self, maxVoltage = 5,
                          deltaVoltage = 0.1,
                          verbose = 0):
        setVoltages = np.arange(0,maxVoltage,deltaVoltage)
        currents = np.zeros(len(setVoltages))
        diodeVoltages = np.zeros(len(setVoltages))
        for i in range(len(setVoltages)):
            thisVoltage = setVoltages[i]
            self.setDAC0(thisVoltage)
            time.sleep(0.05)
            topVoltage = self.labjack.getAIN(0)
            midVoltage = self.labjack.getAIN(1)
            diodeVoltages[i] = midVoltage;
            currents[i] = (topVoltage - midVoltage)/self.resistance
        
        plt.figure('Diode I-V curve')
        plt.plot(diodeVoltages,currents)
        plt.xlabel('diode voltage')
        plt.ylabel('diode current')
        plt.show()
        if verbose:
            
            plt.figure('Input voltages')
            plt.plot(setVoltages,diodeVoltages)
            plt.xlabel('DAC setpoint')
            plt.ylabel('measured output voltage')
            plt.show()
            
    
myRobot = robot()
myRobot.takeIVCurve(verbose = 1)
myRobot.blink()
myRobot.close()