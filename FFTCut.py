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
#    plt.plot(signal, ".")
    
    baseLineEndBin = round(sampleRate * 0.4) # want 0.4 secs of base line
    baseLine = signal[:baseLineEndBin]
    bLMean = np.mean(baseLine)
    bLSD = np.std(baseLine)
    
#    plt.axhline(y = bLMean, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + bLSD, linestyle = "--", color = "purple")

#    plt.axhline(y = bLMean + 6*bLSD, linestyle = "--", color = "purple")
#    plt.axvline(x = baseLineEndBin, linestyle = "--", color = "green")


    for i in range(len(signal)):
        if ((signal[i] - bLMean) / bLSD) > 6:
            break
    
    for i in np.arange(i, 0, -1):
        if ((signal[i] - bLMean) / bLSD) < 3:
#                plt.axvline(x = i, linestyle = "--", color = "red")
#                plt.show()
    
                return i
               
    print("No transient found")
    quit()
               


def findSilence(signal, transientBin, sampleRate, tryNumber):
    plt.plot(signal, ".", zorder = 0)
    
    baseLineStartBin = transientBin - round(sampleRate * 1) # 1 sec of baseline
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
            block = signal[k : (k+400)]
            
            m = np.mean(block)
            testMeanX.append(k)
            testMeanY.append(m)
            if m < bLMean + 0.4  * bLSD:
                
                s = np.std(block)
                testSDX.append(k)
                testSDY.append(s)
                if np.std(block) < 1.1 * bLSD:
                    plt.scatter(testMeanX, testMeanY, color = "red", zorder = 1)
                    plt.scatter(testSDX, bLMean - bLSD + testSDY, color = "pink", zorder = 2, marker = "s")
                    
                    return k
    
    # No silence found
    print("No silence found (" + str(tryNumber) + ")")
    
    plt.scatter(testMeanX, testMeanY, color = "red", zorder = 1)
    plt.scatter(testSDX, bLMean - bLSD + testSDY, color = "pink", zorder = 2, marker = "s")
    
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
    

def isolateFreq(data, freq, nfft):
    binSize = 2**6
    
    xbins = np.arange(0, len(data) - nfft, binSize)
    
    window = blackman(nfft, sym = False)
    output = []
    
    for theBin in xbins:
        signal = data[int(theBin) : (int(theBin) + nfft)] * window
        output.append(freqContribution(signal, freq, 48000))
        
    return (xbins, binSize, output)


def freqContribution(signal, freq, sampleRate):
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
    
#    print("strongestFreq: " + str(strongestFreq))
    
    return strongestFreq

def main():
    startStamp = datetime.now()
    
    print("Cutting")
    firstPitch = 27*60 + 36 #23.5
    offSet = firstPitch - float(noteLines[1].split(",")[6])
    
    outputCSV = ["Velocity,Repitition,Sustain,MidiPitch,Pitch,Time,Delete,Duration,Max,TransientFrame,SilenceFrame"]
    outputPath = homeDir + "/Piano/SpacedOmni_Kontakt/"
    velocityLayers = ["pp", "mp", "f"]
    
    for noteIndex in range(1, len(noteLines) - 1): # range(1, len(noteLines)-1): [4, 5, 189, 510]: #E2
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
            theExp = np.max([13, np.ceil(minExp)]) # never want nfft to be less than 2^10
            nfft = 2**int(theExp)
#            print("nfft: " + str(theExp))
#            print("exp: "+ str(expectedFreq))
            
            #### Transient
            # Isolate Frequency
            peak = np.argmax(theWave[:(4*48000)]) # look only in the first 3 seconds
            targetFreq_Trans = getStrongestFreq(theWave, peak, "f")
            xbins, fftBinSize, data = isolateFreq(theWave, targetFreq_Trans, nfft)
            newSignaldB = logscale(data)
            
            # Find Transient
            trans = findTransient(newSignaldB, 48000 // fftBinSize)
            transFrame = (trans * fftBinSize) + nfft
            transFrame2 = refineTransient(theWave, transFrame, fftBinSize)
            transFrame3 = findZero(theWave, transFrame2, "b")
            
            
            #### Silence
            # Silence 1
            silence1 = findSilence(newSignaldB, trans, 48000 // fftBinSize, 1)
            silence1Frame = silence1 * fftBinSize + nfft
            silence1Frame = findZero(theWave, silence1Frame, "f")
            
            plt.axvline(x = silence1, linestyle = "--", color = "grey")
            plt.axvline(x = trans, linestyle = "--", color = "red")
            plt.savefig("/Users/simonherron/Sampler/Piano/Graphs/" + str(noteIndex) + "_1.png")
            plt.close()
            
            # Silence 2
            searchFrame = silence1Frame #- int((silence1Frame - transFrame) / 3)
            targetFreq_Silence = getStrongestFreq(theWave, searchFrame, "b")
#            print("search: " + str(searchFrame) + " " + str(targetFreq_Silence))
            
            
            
#            plt.specgram(theWave, Fs = 48000, NFFT = 2**12, interpolation = "none", noverlap = 2**12 - 2**6) #2**10
#            plt.ylim(0, 4000)
#            plt.axvline(x = (searchFrame - 2**14) / 48000, linestyle = "--", color = "orange")
#            plt.axvline(x = searchFrame / 48000, linestyle = "--", color = "orange")
            
            
            
            while targetFreq_Silence < (0.5 * targetFreq_Trans): # i.e. keep moving back until target freq is within an order of magnitude of the expected
                searchFrame = searchFrame - 2**12
                
#                plt.axvline(x = (searchFrame - 2**14) / 48000, linestyle = "--", color = "orange")
#                plt.axvline(x = searchFrame / 48000, linestyle = "--", color = "orange")
                
                targetFreq_Silence = getStrongestFreq(theWave, searchFrame, "b")
                
#                print("search: " + str(searchFrame) + " " + str(targetFreq_Silence))
            
#            print(targetFreq_Trans)
#            print(targetFreq_Silence)
            
#            plt.axhline(y = targetFreq_Trans, linestyle = "--", color = "red")
#            plt.axhline(y = targetFreq_Silence, linestyle = ":", color = "pink")
#            plt.axvline(x = silence1Frame / 48000, linestyle = "--", color = "grey")
            
#            plt.show()
                  
            xbins, fftBinSize, data = isolateFreq(theWave, targetFreq_Silence, nfft)
            newSignaldB = logscale(data)
            
            silence2 = findSilence(newSignaldB, trans, 48000 // fftBinSize, 2)
            plt.axvline(x = silence2, linestyle = "--", color = "orange")
            plt.axvline(x = silence1, linestyle = "--", color = "grey")
            plt.axvline(x = trans, linestyle = "--", color = "red")
            plt.savefig("/Users/simonherron/Sampler/Piano/Graphs/" + str(noteIndex) + "_2.png")
            plt.close()
            
            silence2Frame = (silence2 * fftBinSize) + nfft
            silence2Frame = findZero(theWave, silence2Frame, "f")
            
            # Take latter
            silence3Frame = np.max([silence1Frame, silence2Frame])
            
            
            
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
        
       
            
          


            
        outputCSV.append(",".join(noteComponents))
    
    outputCSVFile = open(homeDir + "/Piano/PianoNoPedalV2.csv", "wt")
    outputCSVFile.write("\n".join(outputCSV))
    outputCSVFile.close()
   
    print("Run Duration: " + str(datetime.now() - startStamp))


main()
