#!/usr/bin/env python3

import numpy as np
import soundfile as sf
from soundfile import SoundFile, SEEK_CUR



def main():
    theWave = SoundFile("/Users/simonherron/Documents/Sampler/Piano/08/Spaced Omni_08.wav")
    print("Splitting Wave")
    waveSegs = splitWave(theWave)
    
    print("Cutting")
    noteLines = open("/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv").read().split("\n")
    outputPath = "/Users/simonherron/Documents/Sampler/Piano/SpacedOmni/"
    firstPitch = 23.5
    offSet = firstPitch - float(noteLines[1].split(",")[6])
    velocityLayers = ["pp", "mp", "f"]

    for noteIndex in range(1, len(noteLines)-1):
        noteComponents = noteLines[noteIndex].split(",")
        if noteComponents[7] != "d":
            startIndex = (float(noteComponents[6]) + offSet - 1) * 240 # 48000 / 200 = 240
            startIndex = int(startIndex)
            
            coolDown = 0
            noteStart = -1
            for i in range(startIndex, startIndex + 144000):
                m = waveSegs[i]
                if coolDown > 0:
                    coolDown -= 1
                else:
                    if m > 0.0005:
                        if (waveSegs[i - 5] * 4) < m:
                            if (waveSegs[i - 5] * 2) < min(waveSegs[i:(i + 15)]):
                                if (min(waveSegs[(i - 5):i]) * 4) < min(waveSegs[i:(i + 5)]):
                                    coolDown = 20
                                    if noteStart == -1: # this is the beginning of the note
#                                       print("found")
                                        noteStart = i
                                    else: # this is the second event we've found; it must be the end of the note
                                        break
                
            fileNameComponents = ["Piano", "SpacedOmni", "NoPedal", noteComponents[4], noteComponents[5], str(velocityLayers.index(noteComponents[1]) + 1), noteComponents[1], noteComponents[2]]
            fileName = "_".join(fileNameComponents)
            
            print(str(noteStart * 200) + " " + fileName)
            
            noteDuration = (i - noteStart) * 200
            theWave.seek(noteStart * 200)
            toWrite = theWave.read(frames = noteDuration)
            sf.write(outputPath + fileName + ".wav", toWrite, 48000)
                




def splitWave(theWave):
    output = []
    theWave.seek(0)
    for b in theWave.blocks(blocksize = 200): # frames = 18000000
        vals = b.T[0]
        m = np.mean(np.abs(vals))
        output.append(m)
    
    return output



main()


#theWave.seek(294000)
    

#notes = [0]
#
#prevSection = np.max(np.abs(theWave.read(frames = 1)))
#theWave.seek(0)
#
#for b in theWave.blocks(blocksize = 1000, frames = 20000000):
#    thisSection = np.sum(np.abs(b))
#
#    if (thisSection > prevSection * 6): # and (prevSection < 0.002) and (thisSection > 0.001):
#        transient = theWave.tell() - 1000
#
#        print("transient at: " + str(transient) + " with amplitude: " + str(round(thisSection, 6)) + " prev: " + str(round(prevSection, 6)))
#
#        notes.append(transient)
#
#
#
##        theWave.seek(-1, whence = SEEK_CUR)
#
#    prevSection = thisSection
#
#
#
#theWave.seek(0)
#for i in range(1, len(notes)):
#    toWrite = theWave.read(frames = notes[i] - notes[i-1])
#    sf.write(str(i) + ".wav", toWrite, 48000)
