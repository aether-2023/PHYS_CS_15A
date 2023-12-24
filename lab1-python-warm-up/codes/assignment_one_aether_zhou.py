# -*- coding: utf-8 -*-
"""
Spyder Editor

PHYS CS 15A
Aether Zhou
Week 1
"""

import matplotlib.pyplot as plt
import numpy as np
    
'''1)'''
def temperatureConvert(degreesCelsius):
    return degreesCelsius*9/5+32

'''3)'''
def temperatureConvertPrintsThrice0(degreesCelsius):
    return "%s degrees Celsius is %.1f degrees Fahrenheit." % (degreesCelsius, temperatureConvert(degreesCelsius))

def temperatureConvertPrintsThrice1(degreesCelsius):
    return "{} degrees Celsius is {:.1f} degrees Fahrenheit.".format(degreesCelsius, temperatureConvert(degreesCelsius))

def temperatureConvertPrintsThrice2(degreesCelsius):
    return f"{degreesCelsius} degrees Celsius is {temperatureConvert(degreesCelsius):.1f} degrees Fahrenheit."

def temperatureConvertPrintsThrice(degreesCelsius):
    return str(degreesCelsius)+' degrees Celsius is '+str(temperatureConvert(degreesCelsius))+' degrees Fahrenheit'

'''4)'''
def myPolynomial(x):
    return 2*x**2-3*x+2

'''5)'''
def addOddsToNWithFor(n):
    oddSum = 0
    for oddNum in range(1,n,2):
        oddSum += oddNum
    return oddSum

def addOddsToNWithWhile(n):
    oddSum = 0
    if n%2 == 0:
        oddNum = n-1
    else:
        oddNum = n-2
    while oddNum > 0:
        oddSum += oddNum
        oddNum -= 2
    return oddSum

def addOddsToNWithNumPy(n):
    oddSum = 0
    for oddNum in np.arange(1,n,2):
        oddSum += oddNum
    return oddSum

'''6)'''
def plotMyPolynomial():
    xValue = np.arange(-5.0, 5.0, 0.01)
    yValue = myPolynomial(xValue)
    
    fig, ax = plt.subplots()
    ax.plot(xValue, yValue)
    
    ax.set(xlabel='x', ylabel='f(x)', title='f(x)=2*x^2-3*x+2')
    ax.grid()
    
    plt.show()

'''7)'''
def whatShouldIWear(temperatureFahrenheit):
    if temperatureFahrenheit < 80:
        clothing = "pants"
    else:
        clothing = "shorts"
    return "Aether and Paul recommend you wear {}".format(clothing)