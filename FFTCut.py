#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy.fft import rfft, fftfreq
from scipy.signal import hamming, blackman
from soundfile import SoundFile
import soundfile as sf
import numpy as np
import os
from datetime import datetime

homeDir = os.path.dirname(__file__)
if homeDir == "":
    homeDir = "/home/simonherron"
    
noteLines = open(homeDir + "/Piano/PianoNoPedalV1.csv").read().split("\n")

print("Importing")

waveFile = SoundFile(homeDir + "/Piano/Raw/SpacedOmniDeNoised_1-007.wav", mode = "rb")

def logscale(x):
    return 10*np.log10(x)
    
def log2(x):
    return (np.log(x) / np.log(2))
    
def vol(x):
    o = 0
    for i in range(len(x) - 1):
        o += np.abs(x[i+1] - x[i])
        
    return o / (len(x) - 1)
    
def findTransient(signal, sampleRate):
    plt.plot(signal, ".")
    
    baseLineEndBin = round(sampleRate * 0.4) # want 0.4 secs of base line
    baseLine = signal[:baseLineEndBin]
    bLMean = np.mean(baseLine)
    bLSD = np.std(baseLine)
    
    plt.axhline(y = bLMean, linestyle = "--", color = "purple")
    plt.axhline(y = bLMean + bLSD, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + 2*bLSD, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + 3*bLSD, linestyle = "--", color = "purple")
    plt.axhline(y = bLMean + 6*bLSD, linestyle = "--", color = "purple")
    plt.axvline(x = baseLineEndBin, linestyle = "--", color = "green")


    for i in range(len(signal)):
        if ((signal[i] - bLMean) / bLSD) > 6:
            break
    
    for i in np.arange(i, 0, -1):
        if ((signal[i] - bLMean) / bLSD) < 3:
                plt.axvline(x = i, linestyle = "--", color = "red")
                plt.show()
    
                return i
               
    print("No transient found")
    quit()
               


def findSilence(signal, transientBin, sampleRate, tryNumber):
    plt.plot(signal, ".", zorder = 0)
    
    baseLineStartBin = transientBin - round(sampleRate * 0.4) # 0.4 secs of baseline
    baseLine = signal[baseLineStartBin : transientBin]
    bLMean = np.mean(baseLine)
    bLSD = np.std(baseLine)
    
    plt.axhline(y = bLMean, linestyle = "--", color = "purple")
    plt.axhline(y = bLMean + bLSD, linestyle = "--", color = "purple")
    plt.axvline(x = baseLineStartBin, linestyle = "--", color = "green")
    
    testMeanX = []
    testMeanY = []
    testSDX = []
    testSDY = []
    
    for k in range(transientBin + 500, len(signal)):
        if ((signal[k] - bLMean) / bLSD) < 1:
            block = signal[k : (k+200)]
            
            m = np.mean(block)
            testMeanX.append(k)
            testMeanY.append(m)
            if m < bLMean + 0.4 * bLSD:
                
                s = np.std(block)
                testSDX.append(k)
                testSDY.append(s)
                if np.std(block) < 1.1 * bLSD:
                    plt.scatter(testMeanX, testMeanY, color = "red", zorder = 1)
                    plt.scatter(testSDX, bLMean - bLSD + testSDY, color = "pink", zorder = 2, marker = "s")
                    
                    return k
    
    # No silence found
    print("No silence found (" + str(tryNumber) + ")")
    truncatedSignal = signal[transientBin:]
    return np.argmin(truncatedSignal) + transientBin # i.e. default to location of smallest value (must be after the transient)



def refineTransient(signal, trans, binSize):
    baseLineEndBin = round((48000 // binSize) * 0.4)
    baseLineEndFrame = round(48000 * 0.4) # want 0.4 secs of base line
    rawBaseLine = signal[:baseLineEndFrame]
    bLVol = vol(rawBaseLine)
    
    binSize = 2**5
    
    i = trans
    block = signal[(i - binSize) : i]
    t = vol(block)
    cutoff = trans - 4000
    
    while (t > 1.1 * bLVol) and (i > cutoff): # i.e. no find yet
        i -= binSize
        block = signal[(i - binSize) : i]
        t = vol(block)

    return i



def findZero(signal, startFrame, direction):
    startFrame = int(startFrame)
    nextFrame = startFrame
    increment = (-1) ** (direction == "b") # -1 for b, 1 otherwise
    
    while signal[startFrame] * signal[nextFrame] > 0: # i.e. no sign change yet
        nextFrame += increment
    
    change = np.argmin(np.abs(signal[nextFrame : (nextFrame + 1)]))
    
    return nextFrame + change
    

def freqData(data, freqs, nfft):
    binSize = 2**6
    
    xbins = np.arange(0, len(data) - nfft, binSize)
    
    window = blackman(nfft, sym = False)
    output = []
    
    for theBin in xbins:
        signal = data[int(theBin) : (int(theBin) + nfft)] * window
        toAdd = []
        for f in freqs:
            toAdd.append(isolateFreq(signal, f, 48000))
        
        output.append(toAdd)
        
    return (xbins, binSize, np.transpose(output))


def isolateFreq(signal, freq, sampleRate):
    N = len(signal)
    k = round(freq * (N * 1/sampleRate))
    
    return np.abs(np.sum(signal * np.exp(-2j * np.pi * k * np.arange(N) / N)))
   
def getStrongestFreq(signal, x, direction):
    if direction == "f": # forward
        segment = signal[x : (x + 2**14)]
    else: # backward
        segment = signal[(x - 2**14) : x]
    
    freqMags = np.abs(rfft(segment)[:2**13])
    freqs = fftfreq(2**14, 1/48000)[0:2**13]
    strongestFreq = freqs[np.argmax(freqMags)]
    print("strongestFreq: " + str(strongestFreq))
    
    return strongestFreq

def main():
    startStamp = datetime.now()
    
    print("Cutting")
    firstPitch = 27*60 + 36 #23.5
    offSet = firstPitch - float(noteLines[1].split(",")[6])
    
    outputCSV = ["Velocity,Repitition,Sustain,MidiPitch,Pitch,Time,Delete,Duration,Max,TransientFrame,SilenceFrame"]
    outputPath = homeDir + "/Piano/SpacedOmni_Kontakt/"
    velocityLayers = ["pp", "mp", "f"]
    
    for noteIndex in [4, 510, 550]: #range(1, len(noteLines) - 1): # range(1, len(noteLines)-1): [4, 5, 189, 510]: #E2
        velocity, repitition, sustain, midiPitch, pitch, time, delete = noteLines[noteIndex].split(",")[1:-4]
        noteComponents = [velocity, repitition, sustain, midiPitch, pitch, time, delete]
        
        if delete != "d":
            # Import Wave
            startFrame = int((float(time) + offSet - 2) * 48000)
            endTime = noteLines[noteIndex + 1].split(",")[6] # start time of following pitch
            endFrame = int((float(endTime) + offSet) * 48000)
            waveFile.seek(startFrame)
            stereo = waveFile.read((endFrame + 48000) - startFrame) # add 1 sec to endFrame for padding
            theWave = stereo[:,0]
            otherChannel = stereo[:,1]
            
            # Determine NFFT
            expectedFreq = 441 * 2**((int(midiPitch) - 69)/12) # A4 is midipitch 69
            minExp = log2(2*expectedFreq)
            theExp = np.max([12, np.ceil(minExp)]) # never want nfft to be less than 2^10
            nfft = 2**12 #2**int(theExp)
            print("nfft: " + str(theExp))
            print("exp: "+ str(expectedFreq))
            
            #### Transient
            # FFT
            peak = np.argmax(theWave[:(4*48000)]) # look only in the first 3 seconds
            targetFreqTrans = [getStrongestFreq(theWave, peak, "f")]
            
            # Isolate Frequencies
            xbins, fftBinSize, data1 = freqData(theWave, targetFreqTrans, nfft) # maybe cut down for efficiency?
            newSignal = np.sum(data1, axis = 0)
            newSignaldB = logscale(newSignal)
            
            # Find Transient
            trans = findTransient(newSignaldB, 48000 // fftBinSize)
            transFrame = (trans * fftBinSize) + nfft
            transFrame2 = refineTransient(theWave, transFrame, fftBinSize)
            transFrame3 = findZero(theWave, transFrame2, "b")
            
            
            #### Silence
            # Silence 1
            highestFreq = np.argmax(targetFreqTrans) # not sure if targtetFreqs is sorted ascending
            newSignaldB = logscale(data1[-1, :])
            
            silence1 = findSilence(newSignaldB, trans, 48000 // fftBinSize, 1)
            silence1Frame = silence1 * fftBinSize + nfft
            plt.axvline(x = silence1, linestyle = "--", color = "orange")
            plt.axvline(x = trans, linestyle = "--", color = "red")
            plt.show()
            
            searchFrame = silence1Frame - int((silence1Frame - transFrame) / 3)
            
            plt.specgram(theWave, Fs = 48000, NFFT = nfft, interpolation = "none", noverlap = nfft - 2**6) #2**10
            plt.ylim(0, 4000)
            
            plt.axvline(x = (searchFrame - 2**14) / 48000, linestyle = "--", color = "orange")
            plt.axvline(x = searchFrame / 48000, linestyle = "--", color = "orange")
            
            
            # Silence 2
            targetFreqs2 = [getStrongestFreq(theWave, searchFrame, "b")]
            print("search: " + str(searchFrame) + " " + str(targetFreqs2[0]))
            
            while targetFreqs2[0] < (0.5 * targetFreqTrans[0]): # i.e. keep moving back until target freq is within an order of magnitude of the expected
                searchFrame = searchFrame - 2**12
                plt.axvline(x = (searchFrame - 2**14) / 48000, linestyle = "--", color = "orange")
                plt.axvline(x = searchFrame / 48000, linestyle = "--", color = "orange")
                targetFreqs2 = [getStrongestFreq(theWave, searchFrame, "b")]
                print("search: " + str(searchFrame) + " " + str(targetFreqs2[0]))
                
#            plt.plot(freqs2, logscale(freqMags), ".")
#            plt.show()
            
            print(targetFreqs2)
            
            
            for h in targetFreqTrans:
                plt.axhline(y = h, linestyle = "--", color = "red")

            for h in targetFreqs2:
                plt.axhline(y = h, linestyle = ":", color = "pink")
                
            
            plt.axvline(x = silence1Frame / 48000, linestyle = "--", color = "grey")
            plt.show()
                  
            xbins, fftBinSize, data2 = freqData(theWave, targetFreqTrans, nfft)
            newSignal = np.sum(data2, axis = 0)
            newSignaldB = logscale(newSignal)
            
            silence2 = findSilence(newSignaldB, trans, 48000 // fftBinSize, 2)
            plt.axvline(x = silence2, linestyle = "--", color = "orange")
            plt.axvline(x = trans, linestyle = "--", color = "red")
            plt.show()
            
            silence2Frame = (silence2 * fftBinSize) + nfft
            silence2Frame = findZero(theWave, silence2Frame, "f")
            
            
            
            
            # Calculate Meta Data
            theSize = silence2Frame - transFrame3
            duration = theDuration = round(theSize / 48000, 2)
            
            maxL = np.max(theWave[ : (transFrame3 + 20000)])
            maxR = np.max(otherChannel[ : (transFrame3 + 20000)])
            theMax = np.max([maxL, maxR])
            
            noteComponents.extend([str(duration), str(theMax), str(transFrame3 + startFrame), str(silence2Frame + startFrame)])
            
            # Write File
            nameComponents = ["Piano", "SpacedOmni", "NoPedal", midiPitch, pitch, str(velocityLayers.index(velocity) + 1), velocity, repitition]
            filePath = outputPath + velocity + "_" + repitition + "/" + "_".join(nameComponents) + ".wav"
            nameComponents.insert(0, str(noteIndex))
            print(" ".join(nameComponents))
            toWrite = stereo[transFrame3 : silence2Frame, :]
            sf.write(filePath, toWrite, 48000)
        
       
            
            




#            tf = int(transFrame)
#            tf2 = int(transFrame2)
#            plt.plot(range(tf + 4000), theWave[:(tf + 4000)])
##            plt.ylim([-0.03, 0.03])
#            plt.axvline(x = tf, linestyle = "--", color = "red")
#            plt.axvline(x = tf - nfft, linestyle = "--", color = "orange")
#            plt.axvline(x = tf2, linestyle = "--", color = "black")
#            plt.axvline(x = transFrame3, linestyle = "--", color = "purple")
#            plt.axvline(x = baseLineEndFrame, linestyle = "--", color = "green")
#            plt.axhline(y = 0, color = "black")
#            plt.show()
            
#            fig, ax = plt.subplots()
#            mesh = ax.pcolormesh(xbins, freqs, logscale(data))
#            fig.colorbar(mesh, ax=ax)
#            plt.show()
            
          


            
        outputCSV.append(",".join(noteComponents))
    
    outputCSVFile = open(homeDir + "/Piano/PianoNoPedalV2.csv", "wt")
    outputCSVFile.write("\n".join(outputCSV))
    outputCSVFile.close()
   
    print("Run Duration: " + str(datetime.now() - startStamp))


main()
