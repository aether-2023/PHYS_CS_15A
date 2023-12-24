import sys
import traceback
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import u3


def plotChannel(whichChannel = "AIN0" ):
    # MAX_REQUESTS is the number of packets to be read.
    MAX_REQUESTS = 5
    # SCAN_FREQUENCY is the scan frequency of stream mode in Hz
    SCAN_FREQUENCY = 5000
   
    d = u3.U3()
    # To learn the if the U3 is an HV

    # Set the FIO0 and FIO1 to Analog (d3 = b00000011)
    #d.configIO(FIOAnalog=3,NumberOfTimersEnabled = 2) #don't call this if you've set up PWM to do something you care about.
    #print("Configuring U3 stream")
    d.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
    
    
    
    
    #d.streamStop() #this is not strictly necessary but makes things more robust; without it it crashes if a steam has already been started
   
    print("Start stream")
    try:
        d.streamStart()
    except:
        print("Stopping existing stream..")
        d.streamStop()
        time.sleep(0.1)
        d.streamStart()
        
    start = datetime.now()
    print("Start time is %s" % start)

    missed = 0
    dataCount = 0
    packetCount = 0

    allSamples = np.array([])
    for r in d.streamData():
        if r is not None:
            # Our stop condition
            if dataCount >= MAX_REQUESTS:
                break


            # Comment out these prints and do something with r
            #print("Average of %s AIN0, %s AIN1 readings: %s, %s" %
            #      (len(r["AIN0"]), len(r["AIN1"]), sum(r["AIN0"])/len(r["AIN0"]), sum(r["AIN1"])/len(r["AIN1"])))
            allSamples = np.concatenate((allSamples,r[whichChannel]))
            dataCount += 1
            #packetCount += r['numPackets']
        else:
            # Got no data back from our read.
            # This only happens if your stream isn't faster than the USB read
            # timeout, ~1 sec.
            print("No data ; %s" % datetime.now())
    
    
    stop = datetime.now()
    d.streamStop()
    print("Stream stopped.\n")
    d.close()
    plt.figure()
    plt.plot(range(len(allSamples)),allSamples, 'b-', label=whichChannel)
    
plotChannel("AIN0")