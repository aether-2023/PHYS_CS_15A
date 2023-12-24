#code snippet to test your absFFT function.  In particular, did you get the x axis right?

def testFourier():
    times = np.linspace(0,10,2000)
    f1 = 12  #in Hertz
    f2 = 20  #in Hertz
    testFunction = np.cos(times * f1 * 2 * np.pi) + (2*np.sin(times * f2 * 2 * np.pi))
    frequencies,powerSpectrum = absFFT(times,testFunction)
    
    plt.figure()
    plt.subplot(211)
    plt.plot(times,testFunction, 'g-', label='test Function')
    plt.xlabel('time, seconds')
    plt.legend()
    
    plt.subplot(212)
    plt.plot(frequencies,powerSpectrum, 'b-',label='fourier transform. Should have peaks at 12 and 20')
    plt.xlabel('frequency, Hz')
    plt.legend()
    
    
def overlayFourier():
    times = np.linspace(0,1,2000)
    f1 = 12  #in Hertz
    f2 = 20  #in Hertz
    testFunction = np.cos(times * f1 * 2 * np.pi) + (2*np.sin((times * f2 * 2 * np.pi) + 1))
    frequencies,powerSpectrum = absFFT(times,testFunction)
    
    f = 20 
    sinAmp,cosAmp = getFourierComponent(times,testFunction,f)
    fitData = sinAmp * np.sin(f * 2 * np.pi * times) + cosAmp * np.cos(f * 2 * np.pi * times)

    plt.figure()
    plt.plot(times,testFunction, 'b-', label='test Function')
    plt.plot(times,fitData, 'g-', label='best fit at %d Hz'%f)
    plt.xlabel('time, seconds')
    plt.legend()