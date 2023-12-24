#from https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
# see excellent documentation there

import matplotlib.pyplot as plt
import numpy as np
import csv
from scipy.optimize import curve_fit

def loadTides(filename = 'tidetable.txt'):

    tideEntries = csv.reader(open(filename),delimiter='\t')
    for i in range(14):    #what do the next two lines do? where does that 14 come from?
        next(tideEntries)  #tideEntries is an iterable object. What does this mean?   
    
    tideHeights = []
    for row in tideEntries:
        tideHeights.append(float(row[3]))
    #tideHeights = [float(row[3]) for row in tideEntries]  #see https://www.geeksforgeeks.org/iterate-over-a-list-in-python/ - what is 'list comprehension
    return(np.asarray(tideHeights))

def plotTides():
    tideHeights = loadTides()
    timeInHours = np.arange(len(tideHeights))
    plt.figure()
    plt.plot(timeInHours,tideHeights, 'b-', label='tide Height')
    plt.legend()
    plt.show()
    
def plotTwoTides():
    earlyTideHeights = loadTides('tidetable.txt')
    earlyTimeInHours = np.arange(len(earlyTideHeights))
    lateTideHeights = loadTides('tidetable2.txt')
    lateTimeInHours = np.arange(len(lateTideHeights)) + earlyTimeInHours.max()
    plt.figure()
    plt.plot(earlyTimeInHours,earlyTideHeights, 'b-', label='early tide heights')
    plt.plot(lateTimeInHours,lateTideHeights, 'r-', label='late tide heights')
    plt.xlabel('time, hours')
    plt.ylabel('height, meters')
    plt.title('Santa Barbara tide heights')
    plt.legend()
    plt.show()
    
    
def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def curveFit():
    xdata = np.linspace(0, 4, 50)
    y = func(xdata, 2.5, 1.3, 0.5)
    np.random.seed(1729)
    #look at this line, and compare it to what you just did. This is written rather pythonically
    y_noise = 0.2 * np.random.normal(size=xdata.size)
    ydata = y + y_noise
    plt.figure()
    plt.plot(xdata, ydata, 'b-', label='data')
    
    popt, pcov = curve_fit(func, xdata, ydata)
    print(popt)
    
    #QUESTION: What does that * mean? this is a bit advanced. see https://treyhunner.com/2018/10/asterisks-in-python-what-they-are-and-how-to-use-them/#:~:text=will%20be%20raised.-,Asterisks%20for%20packing%20arguments%20given%20to%20function,arguments%20given%20to%20the%20function.&text=Python's%20print%20and%20zip%20functions%20accept%20any%20number%20of%20positional%20arguments.
    plt.plot(xdata, func(xdata, *popt), 'r-',
             label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
    
    popt, pcov = curve_fit(func, xdata, ydata, bounds=(0, [3., 1., 0.5]))
    #print('aa' popt)
    
    plt.plot(xdata, func(xdata, *popt), 'g--',
             label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.show()
 
plotTwoTides()