import sys
import traceback
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import u3

class robotVer2:
    
    def __init__(self):
        self.labjack = u3.U3()
        self.__resistance = 500
        
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
        elif voltage > 5:
            print('output voltage must be <= 5')
            return
        else:
            DAC0_VALUE = self.labjack.voltageToDACBits(voltage, dacNumber = 0, is16Bits = False)
            self.labjack.getFeedback(u3.DAC0_8(DAC0_VALUE))

    
    def configLabJack(self, theDivisor = 16):
        self.labjack.configIO(NumberOfTimersEnabled = 2, FIOAnalog=3)
        self.labjack.configTimerClock(TimerClockBase = 6, TimerClockDivisor=theDivisor)

    def setPWM(self, highFraction = 1, whichTimer = 0):
        if highFraction>1 or highFraction<0:
            print('highFraction should be a real number between 0 and 1.')
            return
        i = int((1-highFraction)*65535)
        if whichTimer == 0:
            self.labjack.getFeedback(u3.Timer0Config(TimerMode = 0, Value = i))
        elif whichTimer == 1:
            self.labjack.getFeedback(u3.Timer1Config(TimerMode = 0, Value = i))
        else:
            print('There are two timers only! Please input 0 or 1.')
            return

    def plotTwoChannels(self):
        MAX_REQUESTS = 5
        SCAN_FREQUENCY = 5000
        self.labjack.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
        
        print("Start stream")
        try:
            self.labjack.streamStart()
        except:
            print("Stopping existing stream..")
            self.labjack.streamStop()
            time.sleep(0.1)
            self.labjack.streamStart()

        start = datetime.now()
        print("Start time is %s" % start)

        missed = 0
        dataCount = 0
        packetCount = 0

        allSamples0 = np.array([])
        allSamples1 = np.array([])
        for r in self.labjack.streamData():
            if r is not None:
                if dataCount >= MAX_REQUESTS:
                    break
                allSamples0 = np.concatenate((allSamples0,r['AIN0']))
                allSamples1 = np.concatenate((allSamples1,r['AIN1']))
                dataCount += 1
            else:
                print("No data ; %s" % datetime.now())

        stop = datetime.now()
        seconds=np.linspace(0,(stop-start).total_seconds(),3000)
        self.labjack.streamStop()
        print("Stream stopped.\n")
        self.labjack.close()
        
        plt.figure()
        plt.subplot(211)
        plt.xlabel('Time (s)')
        plt.ylabel('AIN0 (V)')
        plt.plot(seconds[0:50],allSamples0[0:50], 'b-', label='AIN0')
        plt.subplot(212)
        plt.xlabel('Time (s)')
        plt.ylabel('AIN1 (V)')
        plt.plot(seconds[0:50],allSamples1[0:50], 'b-', label='AIN1')
        plt.show()

    def getChannel(self, whichChannel = "AIN0" ):
        MAX_REQUESTS = 5
        SCAN_FREQUENCY = 5000
        self.labjack.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
        
        print("Start stream")
        try:
            self.labjack.streamStart()
        except:
            print("Stopping existing stream..")
            self.labjack.streamStop()
            time.sleep(0.1)
            self.labjack.streamStart()

        start = datetime.now()
        print("Start time is %s" % start)

        missed = 0
        dataCount = 0
        packetCount = 0

        allSamples = np.array([])
        for r in self.labjack.streamData():
            if r is not None:
                if dataCount >= MAX_REQUESTS:
                    break
                allSamples = np.concatenate((allSamples,r[whichChannel]))
                dataCount += 1
            else:
                print("No data ; %s" % datetime.now())

        stop = datetime.now()
        seconds=np.linspace(0,(stop-start).total_seconds(),3000)
        self.labjack.streamStop()
        print("Stream stopped.\n")
        self.labjack.close()
        return seconds, allSamples

    def plotChannel(self, whichChannel = "AIN0" ):
        times,allSamples = self.getChannel(whichChannel)
        plt.figure()
        plt.plot(times,allSamples, 'b-', label=whichChannel)
        plt.xlabel('time, seconds')
        plt.ylabel('voltage on %s' % whichChannel)
        
rb0=robotVer2()
rb0.configLabJack(160)
rb0.setDAC0(5)
rb0.setPWM(0.5,1)
rb0.setPWM(0.5,0)
rb0.plotTwoChannels()
rb0.close()
