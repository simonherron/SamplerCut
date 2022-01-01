#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy.fft import rfft, fftfreq
from scipy.signal import flattop, hamming
from soundfile import SoundFile
import numpy as np

noteLines = open("/Users/simonherron/Sampler/Piano/PianoNoPedal.csv").read().split("\n")

print("Importing Wave")
waveFile = SoundFile("/Users/simonherron/Sampler/Piano/08/Spaced Omni_08.wav", mode = "rb")
waveFile.seek(0)
theWave = waveFile.read()[:,0]

print("Cutting")

def logscale(x):
    return 10*np.log10(x)
    
def vol(x):
    o = 0
    for i in range(len(x) - 1):
        o += np.abs(x[i+1] - x[i])
        
    return o / (len(x) - 1)
    
def findTransientAndSilence(data, sampleRate):
    baseLineEndFrame = round(sampleRate * 0.4) # want 0.4 secs of base line
    baseLine = data[:baseLineEndFrame]
    bLMean = np.mean(baseLine)
    bLSD = np.std(baseLine)
    
    plt.axhline(y = bLMean, linestyle = "--", color = "purple")
    plt.axhline(y = bLMean + 2*bLSD, linestyle = "--", color = "purple")
    plt.axhline(y = bLMean + 3*bLSD, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + 4*bLSD, linestyle = "--", color = "purple")
    
    for i in range(len(data)):
        if ((data[i] - bLMean) / bLSD) > 6:
            break
    
    for i in np.arange(i, 0, -1):
        if ((data[i] - bLMean) / bLSD) < 3:
            break
                
    transient = i
    
    testMeanX = []
    testMeanY = []
    testSDX = []
    testSDY = []
    
    for k in range(transient + 500, len(data)):
        if ((data[k] - bLMean) / bLSD) < 1:
            block = data[k : (k+200)]
            
            m = np.mean(block)
            testMeanX.append(k)
            testMeanY.append(m)
            
            if m < bLMean + 0.2 * bLSD:
                
                s = np.std(block)
                testSDX.append(k)
                testSDY.append(s)
            
                if np.std(block) < 1.1 * bLSD:
                    break
    
#    plt.scatter(testMeanX, testMeanY, color = "red", zorder = 1)
#    plt.scatter(testSDX, bLMean - bLSD + testSDY, color = "pink", zorder = 2, marker = "s")
    
    return (transient, k)

def refineTransient(trans, binSize, n, bLVol):
    bins = np.linspace(trans, trans - 32 * 30, 29).astype(int)
    
    print(bLVol)
    
    for i in bins:
        block = theWave[(i - 32) : i]
        t = vol(block)
        print(t)
        if t < 1.1 * bLVol:
            return i
    
    print("no find")
    return trans


def findZero(startFrame, direction):
    startFrame = int(startFrame)
    nextFrame = startFrame
    increment = (-1) ** (direction == "b") # -1 for b, 1 otherwise
    
    while theWave[startFrame] * theWave[nextFrame] > 0: # i.e. no sign change yet
        nextFrame += increment
    
    change = np.argmin(np.abs(theWave[nextFrame : (nextFrame + 1)]))
    
    return nextFrame + change
    
#    block = theWave[(startFrame - 100) : (startFrame + 100)]
#
#    print(block)
#    print(np.min(block))
#
#    plt.plot(block, ".")
#    plt.show()

def freqData(startFrame, endFrame, targetFreq):
    binSize = 2**6 # 2*86
    nfft = 2**10
    
    xbins = np.arange(startFrame, endFrame, binSize)
    harmonics = 3
    freqs = targetFreq * np.arange(1, harmonics + 1)
    
    window = hamming(nfft, sym = False)
    output = []
    
    for theBin in xbins:
        signal = theWave[int(theBin) : (int(theBin) + nfft)] * window
        toAdd = []
        for f in freqs:
            toAdd.append(isolateFreq(signal, f, 48000))
        
        output.append(toAdd)
        
    return (xbins, binSize, freqs, nfft, np.transpose(output))


def isolateFreq(signal, freq, sampleRate):
    N = len(signal)
    allFreqs = 5
    k = round(freq * (N * 1/sampleRate))
    
    return np.abs(np.sum(signal * np.exp(-2j * np.pi * k * np.arange(N) / N)))
    

def cut():
    firstPitch = 23.5
    offSet = firstPitch - float(noteLines[1].split(",")[6])
    
    for noteIndex in [128, 482, 488]: #E2
        velocity, repitition, sustain, midiPitch, pitch, time, delete = noteLines[noteIndex].split(",")[1:-4]
        if delete != "d":
            startFrame = int((float(time) + offSet - 1) * 48000)
            endTime = noteLines[noteIndex + 1].split(",")[6] # start time of following pitch
            endFrame = (float(endTime) + offSet + 1) * 48000
            targetFreq = 440 * 2**((int(midiPitch) - 69)/12) # A4 is midipitch 69
            
            xbins, fftBinSize, freqs, nfft, data = freqData(startFrame, endFrame, targetFreq)
            newSignal = logscale(np.sum(data, axis = 0))
                        
            trans, silence = findTransientAndSilence(newSignal, 48000 // fftBinSize)
            
            baseLineEndFrame = round(48000 * 0.4) # want 0.4 secs of base line
            rawBaseLine = theWave[startFrame : (startFrame + baseLineEndFrame)]
            rawBLVol = vol(rawBaseLine)
            
            transFrame = (startFrame + trans * fftBinSize) + nfft
            transFrame2 = refineTransient(transFrame, fftBinSize, nfft, rawBLVol)
            transFrame3 = findZero(transFrame2, "b")
            
            silenceFrame = (startFrame + silence * fftBinSize) + nfft
            silenceFrame2 = findZero(silenceFrame, "f")

            # Calculate Meta Data
            theSize = silenceFrame2 - transFrame3
            duration = theDuration = round(theSize / 48000, 2)
            
            


#            print("Plotting")
#            plt.plot(newSignal, ".", zorder = 0)

#            plt.axvline(x = trans, linestyle = "--", color = "red")
##            plt.axvline(x = (48000 // fftBinSize) * 0.4, linestyle = "--", color = "green")
##            plt.axvline(x = silence, linestyle = "--", color = "orange")
#            plt.scatter(trans, newSignal[trans], color = "red", zorder = 2)
#            plt.show()
#
#
#            tf = int(transFrame)
#            tf2 = int(transFrame2)
#            plt.plot(range(startFrame, tf + 4000), theWave[startFrame : (tf + 4000)])
#            plt.ylim([-0.03, 0.03])
#            plt.axvline(x = tf, linestyle = "--", color = "red")
#            plt.axvline(x = tf2, linestyle = "--", color = "black")
#            plt.axvline(x = transFrame3, linestyle = "--", color = "purple")
#            plt.axvline(x = startFrame + baseLineEndFrame, linestyle = "--", color = "green")
#
#            plt.axhline(y = 0, color = "black")
#
#            plt.show()
            
   


cut()
