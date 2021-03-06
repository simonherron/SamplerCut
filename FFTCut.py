#!/usr/bin/env python3

import matplotlib.pyplot as plt
#from scipy.fft import rfft, fftfreq
from scipy.signal import hamming
from soundfile import SoundFile
import soundfile as sf
import numpy as np
import os

homeDir = os.path.dirname(__file__)
if homeDir == "":
    homeDir = "/home/simonherron"

noteLines = open(homeDir + "/Piano/PianoNoPedalV1.csv").read().split("\n")

print("Importing Wave")
waveFile = SoundFile(homeDir + "/Piano/08/Spaced Omni_08.wav", mode = "rb")
waveFile.seek(0)
stereo = waveFile.read()
theWave = stereo[:,0]
otherChannel = stereo[:,1]

print("Cutting")

def splitList(x, cores):
    remainder = len(x) % cores
    if remainder != 0:
        x = np. append(x, np.repeat(None, cores - remainder))
        
    m = x.reshape((len(x) // cores, cores))
    return m.transpose()


splitList(np.arange(37), 4)



def logscale(x):
    return 10*np.log10(x)
    
def vol(x):
    o = 0
    for i in range(len(x) - 1):
        o += np.abs(x[i+1] - x[i])
        
    return o / (len(x) - 1)
    
def findTransientAndSilence(data, sampleRate):
    baseLineEndBin = round(sampleRate * 0.4) # want 0.4 secs of base line
    baseLine = data[:baseLineEndBin]
    bLMean = np.mean(baseLine)
    bLSD = np.std(baseLine)
    
#    plt.axhline(y = bLMean, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + 2*bLSD, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + 3*bLSD, linestyle = "--", color = "purple")
#    plt.axhline(y = bLMean + 4*bLSD, linestyle = "--", color = "purple")
#
    for i in range(len(data)):
        if ((data[i] - bLMean) / bLSD) > 6:
            break
    
    for i in np.arange(i, 0, -1):
        if ((data[i] - bLMean) / bLSD) < 3:
            break
                
    transient = i
#
#    testMeanX = []
#    testMeanY = []
#    testSDX = []
#    testSDY = []
    
    for k in range(transient + 500, len(data)):
        if ((data[k] - bLMean) / bLSD) < 1:
            block = data[k : (k+200)]
            
            m = np.mean(block)
#            testMeanX.append(k)
#            testMeanY.append(m)
            if m < bLMean + 0.2 * bLSD:
                
                s = np.std(block)
#                testSDX.append(k)
#                testSDY.append(s)
                if np.std(block) < 1.1 * bLSD:
                    break
    
#    plt.scatter(testMeanX, testMeanY, color = "red", zorder = 1)
#    plt.scatter(testSDX, bLMean - bLSD + testSDY, color = "pink", zorder = 2, marker = "s")
    
    return (transient, k)

def refineTransient(trans, binSize, n, bLVol):
    binSize = 2**5
    
    i = trans
    block = theWave[(i - binSize) : i]
    t = vol(block)
    cutoff = trans - 4000
    
    while (t > 1.1 * bLVol) and (i > cutoff): # i.e. no find yet
        i -= binSize
        block = theWave[(i - binSize) : i]
        t = vol(block)

    return i



def findZero(startFrame, direction):
    startFrame = int(startFrame)
    nextFrame = startFrame
    increment = (-1) ** (direction == "b") # -1 for b, 1 otherwise
    
    while theWave[startFrame] * theWave[nextFrame] > 0: # i.e. no sign change yet
        nextFrame += increment
    
    change = np.argmin(np.abs(theWave[nextFrame : (nextFrame + 1)]))
    
    return nextFrame + change
    

def freqData(startFrame, endFrame, targetFreq):
    binSize = 2**6 # 2**6
    nfft = 2**14
    
    xbins = np.arange(startFrame, endFrame, binSize)
    harmonics = 6
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
    

def main():
    firstPitch = 23.5
    offSet = firstPitch - float(noteLines[1].split(",")[6])
    
    outputCSV = ["Velocity,Repitition,Sustain,MidiPitch,Pitch,Time,Delete,Duration,Max,TransientFrame,SilenceFrame"]
    outputPath = homeDir + "/Piano/SpacedOmni_Kontakt/"
    velocityLayers = ["pp", "mp", "f"]
    
    for noteIndex in [2, 510, 568]: # range(1, len(noteLines)-1): # # #[128, 482, 488]: #E2
        velocity, repitition, sustain, midiPitch, pitch, time, delete = noteLines[noteIndex].split(",")[1:-4]
        noteComponents = [velocity, repitition, sustain, midiPitch, pitch, time, delete]
        
        if delete != "d":
            # DFT
            startFrame = int((float(time) + offSet - 1) * 48000)
            endTime = noteLines[noteIndex + 1].split(",")[6] # start time of following pitch
            endFrame = (float(endTime) + offSet + 1) * 48000
            targetFreq = 440 * 2**((int(midiPitch) - 69)/12) # A4 is midipitch 69
            
            xbins, fftBinSize, freqs, nfft, data = freqData(startFrame, endFrame, targetFreq)
            
            # Baseline
            baseLineEndBin = round((48000 // fftBinSize) * 0.4)
            baseLineEndFrame = round(48000 * 0.4) # want 0.4 secs of base line
            rawBaseLine = theWave[startFrame : (startFrame + baseLineEndFrame)]
            rawBLVol = vol(rawBaseLine)
            bLHarmonics = logscale(np.mean(data[:baseLineEndBin], axis = 1))
            
            # Find Peak
            allHarmonics = np.sum(data, axis = 0)
            peak = np.argmax(allHarmonics)
            
            # Sort Harmonics
            peakHarmonics = logscale(np.mean(data[:, peak : (peak + 1)], axis = 1))
            
            bLMean = np.mean(bLHarmonics)
            bLSD = np.std(bLHarmonics)
            
            loudestHarmonic = np.argmax(peakHarmonics)
            h = loudestHarmonic
            for h in range(loudestHarmonic + 1, len(peakHarmonics)):
                if (peakHarmonics[h] - bLMean) / bLSD < 2:
                    h = h - 1
                    break
            
            keptHarmonics = np.arange(0, h + 1) # in order to include h itself
            print(keptHarmonics)
#            data = data[keptHarmonics]
#            freqs = freqs[keptHarmonics]
            newSignal = logscale(np.sum(data[keptHarmonics], axis = 0))

#
#            plt.plot(peakHarmonics)
#            plt.scatter(range(len(bLHarmonics)), bLHarmonics, color = "red")
#            plt.show()

#            plt.plot(newSignal, ".", zorder = 0)
            

            
            trans, silence = findTransientAndSilence(newSignal, 48000 // fftBinSize)
            
#            plt.axvline(x = trans, linestyle = "--", color = "red")
#            plt.axvline(x = (48000 // fftBinSize) * 0.4, linestyle = "--", color = "green")
#            plt.axvline(x = silence, linestyle = "--", color = "orange")
#            plt.scatter(trans, newSignal[trans], color = "red", zorder = 2)
#            plt.show()
            
   
            
            # Refine
            transFrame = (startFrame + trans * fftBinSize) + nfft
            transFrame2 = refineTransient(transFrame, fftBinSize, nfft, rawBLVol)
            transFrame3 = findZero(transFrame2, "b")
            
            silenceFrame = (startFrame + silence * fftBinSize) + nfft
            silenceFrame2 = findZero(silenceFrame, "f")
            
            # Calculate Meta Data
            theSize = silenceFrame2 - transFrame3
            duration = theDuration = round(theSize / 48000, 2)
            
            maxL = np.max(theWave[transFrame3 : (transFrame3 + 20000)])
            maxR = np.max(otherChannel[transFrame3 : (transFrame3 + 20000)])
            theMax = np.max([maxL, maxR])
            
            noteComponents.extend([str(duration), str(theMax), str(transFrame3), str(silenceFrame2)])
            
            # Write File
            nameComponents = ["Piano", "SpacedOmni", "NoPedal", midiPitch, pitch, str(velocityLayers.index(velocity) + 1), velocity, repitition]
            filePath = outputPath + velocity + "_" + repitition + "/" + "_".join(nameComponents) + ".wav"
            print(" ".join(nameComponents))
            toWrite = stereo[transFrame3 : silenceFrame2, :]
            sf.write(filePath, toWrite, 48000)
        
       
            
            
#            print("Plotting")
#            print(transFrame)
#            print(transFrame2)
#            print(transFrame3)

#            print(silenceFrame2)

#            tf = int(transFrame)
#            tf2 = int(transFrame2)
#            plt.plot(range(startFrame, tf + 4000), theWave[startFrame : (tf + 4000)])
#            plt.ylim([-0.03, 0.03])
#            plt.axvline(x = tf, linestyle = "--", color = "red")
#            plt.axvline(x = tf2, linestyle = "--", color = "black")
#            plt.axvline(x = transFrame3, linestyle = "--", color = "purple")
#            plt.axvline(x = startFrame + baseLineEndFrame, linestyle = "--", color = "green")
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
   


main()
