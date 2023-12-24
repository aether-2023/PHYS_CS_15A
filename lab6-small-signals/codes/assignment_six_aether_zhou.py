import u3
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import pickle
import matplotlib.colors as colors
from datetime import datetime
import time
import sys
import traceback
from scipy.signal import savgol_filter

class robot:
    
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
        
    def blink(self, n = 3):
        while n > 0:
            n-=1
            self.setDAC0(2)
            sleep(1)
            self.setDAC0(0)
            sleep(1)
    
    def takeIVCurve(self, maxVoltage = 5, deltaVoltage = 0.1, verbose = 0):
        setVoltages = np.arange(0,maxVoltage,deltaVoltage)
        currents = np.zeros(len(setVoltages))
        diodeVoltages = np.zeros(len(setVoltages))
        for i in range(len(setVoltages)):
            thisVoltage = setVoltages[i]
            self.setDAC0(thisVoltage)
            sleep(0.05)
            topVoltage = self.labjack.getAIN(0)
            midVoltage = self.labjack.getAIN(1)
            diodeVoltages[i] = midVoltage;
            currents[i] = (topVoltage - midVoltage)/self.__resistance
        
        plt.figure('I-V curve')
        plt.plot(diodeVoltages,currents)
        plt.xlabel('voltage')
        plt.ylabel('current')
        plt.show()
        if verbose:
            
            plt.figure('Input voltages')
            plt.plot(setVoltages,diodeVoltages)
            plt.xlabel('DAC setpoint')
            plt.ylabel('measured output voltage')
            plt.show()
        
    def takeIVCurves(self, maxVoltage = 5, deltaVoltage = 0.1):
        print("input -1 to exit")
        print("repeated trial name will cause lost of data")
        trials = 0
        dataFiles = []
        while 1:
            print("current trials: "+str(dataFiles))
            tName = input('input the next trial name: ')
            if tName == '-1':
                break
            else:
                trials+=1
                dataFiles.append(tName)
            
            setVoltages = np.arange(0,maxVoltage,deltaVoltage)
            currents = np.zeros(len(setVoltages))
            diodeVoltages = np.zeros(len(setVoltages))
            for i in range(len(setVoltages)):
                thisVoltage = setVoltages[i]
                self.setDAC0(thisVoltage)
                sleep(0.05)
                topVoltage = self.labjack.getAIN(0)
                midVoltage = self.labjack.getAIN(1)
                diodeVoltages[i] = midVoltage;
                currents[i] = (topVoltage - midVoltage)/self.__resistance
            self.setDAC0(0)
            
            aData=open(tName,'wb')
            pickle.dump([diodeVoltages,currents],aData)
            aData.close()
        
        plt.figure("I-V diagram for LED")
        colors_list = list(colors._colors_full_map.values())
        colorNum = len(colors_list)
        while trials >0:
            trials-=1
            aData=open(dataFiles[trials],'rb')
            xData, yData = pickle.load(aData)
            aData.close()
            plt.plot(xData, yData, colors_list[np.random.randint(0, colorNum)], label=dataFiles[trials])
            
        plt.xlabel("Voltage (V)")
        plt.ylabel("current (A)")
        plt.legend()
        plt.show()
        
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

    def getChannel(self, whichChannel = "AIN0" ):
        MAX_REQUESTS = 25
        SCAN_FREQUENCY = 5000
        self.labjack.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
        
        print("Start stream")
        try:
            self.labjack.streamStart()
        except:
            print("Stopping existing stream0.")
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
                #print(r[whichChannel])
                allSamples = np.concatenate((allSamples,r[whichChannel]))
                dataCount += 1
            else:
                print("No data ; %s" % datetime.now())

        stop = datetime.now()
        seconds=np.linspace(0,(stop-start).total_seconds(),15000)
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
    
    def getTraceData(self, whichChannel = "AIN1"):
        MAX_REQUESTS = 25
        SCAN_FREQUENCY = 5000
        self.labjack.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
        
        print("Start stream")
        try:
            self.labjack.streamStart()
        except:
            print("Stopping existing stream0.")
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
        seconds=np.linspace(0,(stop-start).total_seconds(),15000)
        self.labjack.streamStop()
        print("Stream stopped.\n")
        self.labjack.close()
        return seconds, allSamples
    
    def takeFastLightTrace(self,whichChannel = "AIN1"):
        times,allSamples = self.getTraceData(whichChannel)
        plt.figure()
        plt.plot(times,allSamples, 'b-')
        plt.xlabel('time, seconds')
        plt.ylabel('light level, voltage')
        
    def absFFT(self,times, amplitude):
        result = (np.abs(np.fft.fft(amplitude))/len(amplitude))
        freq = len(times)/times[-1]*np.abs(np.fft.fftfreq(len(times)))
        return  freq, result
        
    def fftSignal(self, whichChannel = "AIN1"):
        times,allSamples = self.getTraceData(whichChannel)
        frequencies, powerSpectrum = self.absFFT(times, allSamples)
        
        plt.figure()
        plt.subplot(211)
        plt.plot(times,allSamples, 'g-', label='light level')
        plt.xlabel('time, seconds')
        plt.legend()

        plt.subplot(212)
        plt.plot(frequencies[1:500],powerSpectrum[1:500], 'b-',label='fourier transform')
        plt.xlabel('frequency, Hz')
        plt.legend()
        
        plt.show()
        
        temp0 = powerSpectrum.copy()
        temp0.sort()
        snr = 20 * np.log(temp0[-2]/temp0[-4]) / np.log(10)
        print('The signal to noise ratio is '+str(snr)+' dB')
        
    def getTwoChannels(self, duration = 5):
        MAX_REQUESTS = 5*duration
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
        seconds=np.linspace(0,(stop-start).total_seconds(),3000*duration)
        self.labjack.streamStop()
        print("Stream stopped.\n")
        self.labjack.close()
        
        return seconds, allSamples0, allSamples1
    
    def plotTwoChannels(self):
        seconds, allSamples0, allSamples1 = self.getTwoChannels()
        
        plt.figure()
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (V)')
        plt.plot(seconds,allSamples0, 'r-', label='sensor')
        plt.plot(seconds,allSamples1, 'b-', label='LED')
        plt.legend()
        plt.show()
        
    def lockinDetect(self, duration = 5):
        seconds, allSamples0, allSamples1 = self.getTwoChannels(duration)
        smoothSignal = savgol_filter(allSamples0, 5001, 3)
        smoothLEDVoltage = savgol_filter(allSamples1, 5001, 3)
        
        signal = allSamples0 - smoothSignal
        LEDVoltage = allSamples1 - smoothLEDVoltage
        
        lockinsignal = signal * LEDVoltage
        finalsignal = savgol_filter(lockinsignal, 5001, 3)
        
        plt.figure()
        plt.subplot(311)
        plt.plot(seconds,signal, label='detector voltage')
        plt.ylabel('voltage, volts')
        plt.legend()
        
        plt.subplot(312)
        plt.plot(seconds, LEDVoltage,label='LED voltage')
        plt.ylabel('voltage, volts')
        plt.legend()
        
        plt.subplot(313)
        plt.plot(seconds, lockinsignal, label = 'signal voltage')
        plt.plot(seconds, finalsignal, label = 'smooth signal voltage')
        plt.ylabel('voltage, volts')
        plt.legend()
        
        plt.show()
        
myRobot = robot()

myRobot.configLabJack(64)
#myRobot.setDAC0(0)

#myRobot.blink()
myRobot.setPWM(0.5)

#myRobot.plotChannel("AIN0")
#myRobot.takeFastLightTrace()

#myRobot.plotTwoChannels()
#myRobot.fftSignal("AIN0")
myRobot.lockinDetect(50)
        
        