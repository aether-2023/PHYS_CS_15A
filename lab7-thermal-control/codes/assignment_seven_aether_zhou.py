%matplotlib qt5
import u3
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time
import pickle

class robot:
    
    def __init__(self):
        self.labjack = u3.U3()
        self.__resistance = 10000
        
    def close(self):
        self.labjack.close()
                            
    def printAnalogIns(self):
        AIN0value = self.labjack.getAIN(0)
        AIN1value = self.labjack.getAIN(1)
        AIN2value = self.labjack.getAIN(2)
        AIN3value = self.labjack.getAIN(3)
        descriptor ='A0 = %5.3f volts, A1 = %5.3f volts, A2 = %5.3f volts, A3 = %5.3f volts ' % (AIN0value, AIN1value, AIN2value, AIN3value)
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
            
    def setDAC1(self,voltage = 0):
        if voltage < 0:
            print('output voltage must be >= 0')
            return
        elif voltage > 5:
            print('output voltage must be <= 5')
            return
        else:
            DAC1_VALUE = self.labjack.voltageToDACBits(voltage, dacNumber = 1, is16Bits = False)
            self.labjack.getFeedback(u3.DAC1_8(DAC1_VALUE))

    def getRTData(self, dataNum = 100):
        resData = np.zeros(dataNum)
        index = 0
        start = datetime.now()
        while index < dataNum:
            sleep(0.05)
            topVoltage = self.labjack.getAIN(0)
            midVoltage = self.labjack.getAIN(1) 
            resData[index] = self.__resistance / (topVoltage / midVoltage - 1)
            index += 1
        stop = datetime.now()
        seconds=np.linspace(0,(stop-start).total_seconds(),dataNum)
        return seconds, resData
        
    def takeRTCurve(self, dataNum = 100):
        seconds, resData = self.getRTData(dataNum)
        
        print(resData.mean())
        
        plt.figure('R-T curve')
        plt.plot(seconds,resData)
        plt.xlabel('time (seconds)')
        plt.ylabel('resistance (ohm)')
        plt.show()
        
    def getTemperature(self):
        topVoltage = self.labjack.getAIN(0)
        midVoltage = self.labjack.getAIN(1) 
        resData = self.__resistance / (topVoltage / midVoltage - 1)
        temperatureData = 48.877-(1.845*(10**(-3)))*resData
        return temperatureData
        
    def takeTTCurve(self, dataNum = 100, timePeriod = 20):
        seconds, resData = self.getRTData(dataNum)
        temperatureData = resData*((-1.845)*(10**(-3)))+48.877
        heaterVoltData = np.zeros(dataNum)
        meanTemp = temperatureData.mean()
        
        plt.ion()
        fig = plt.figure('T-T curve')
        ax = fig.add_subplot(211)
        line1, = ax.plot(seconds, temperatureData, 'r-')
        ax.set_xlim([0,seconds[-1]+timePeriod])
        ax.set_ylim([meanTemp-2,meanTemp+2])
        ax.set_ylabel('temperature (celsius)')
        
        ax2 = fig.add_subplot(212)
        line2, = ax2.plot(seconds, heaterVoltData, 'b-')
        ax2.set_xlim([0,seconds[-1]+timePeriod])
        ax2.set_ylim([-0.5,5.5])
        ax2.set_xlabel('time (seconds)')
        ax2.set_ylabel('voltage (volt)')
        
        start = datetime.now()
        newDataNum = 0
        newVoltage = 0
        while (datetime.now() - start).total_seconds() < timePeriod:
            sleep(0.05)
            newDataNum += 1
            temperature = self.getTemperature()
            newVoltage = self.heaterVoltage(newVoltage, meanTemp, self.getTemperature())
            self.setDAC1(newVoltage)
            heaterVoltData = np.append(heaterVoltData, newVoltage)
            temperatureData = np.append(temperatureData,self.getTemperature())
            intervalTime = (datetime.now() - start).total_seconds()/newDataNum
            seconds = np.append(seconds, seconds[-1]+intervalTime)
            
            line1.set_xdata(seconds)
            line1.set_ydata(temperatureData)
            line2.set_xdata(seconds)
            line2.set_ydata(heaterVoltData)
            fig.canvas.draw()
            fig.canvas.flush_events()

    def heaterVoltage(self, currentVolt, stableTemp, temperature, onVoltage = 5, offVoltage = 0):
        #(time>5) & (time<25)
        if temperature < stableTemp-0.2:
            return onVoltage
        elif temperature > stableTemp+0.2:
            return offVoltage
        else:
            return currentVolt
    
    
        
    def boxcarAverager(self, dataNum = 100, timePeriod = 20):
        seconds, resData = self.getRTData(dataNum)
        temperatureData = resData*((-1.845)*(10**(-3)))+48.877
        heaterVoltData = np.zeros(dataNum)
        meanTemp = temperatureData.mean()
        
        plt.ion()
        fig = plt.figure('T-T curve')
        ax = fig.add_subplot(211)
        line1, = ax.plot(seconds, temperatureData, 'r-')
        ax.set_xlim([0,seconds[-1]+timePeriod])
        ax.set_ylim([meanTemp-2,meanTemp+2])
        ax.set_ylabel('temperature (celsius)')
        
        ax2 = fig.add_subplot(212)
        line2, = ax2.plot(seconds, heaterVoltData, 'b-')
        ax2.set_xlim([0,seconds[-1]+timePeriod])
        ax2.set_ylim([-0.5,5.5])
        ax2.set_xlabel('time (seconds)')
        ax2.set_ylabel('voltage (volt)')
        
        start = datetime.now()
        newDataNum = 0
        newVoltage = 0
        while (datetime.now() - start).total_seconds() < timePeriod:
            sleep(0.05)
            newDataNum += 1
            temperatureMean = temperatureData[-100:].mean()
            newVoltage = self.heaterVoltage(newVoltage, meanTemp, temperatureMean)
            self.setDAC1(newVoltage)
            heaterVoltData = np.append(heaterVoltData, newVoltage)
            temperatureData = np.append(temperatureData,self.getTemperature())
            intervalTime = (datetime.now() - start).total_seconds()/newDataNum
            seconds = np.append(seconds, seconds[-1]+intervalTime)
            
            line1.set_xdata(seconds)
            line1.set_ydata(temperatureData)
            line2.set_xdata(seconds)
            line2.set_ydata(heaterVoltData)
            fig.canvas.draw()
            fig.canvas.flush_events()
    
r01 = robot()
r01.setDAC0(5)
r01.boxcarAverager(100,100)
r01.takeTTCurve(50,10)
r01.takeRTCurve(30)
r01.getTemperature()    