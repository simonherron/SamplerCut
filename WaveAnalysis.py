#!/usr/bin/env python3

import numpy as np
import soundfile as sf
from soundfile import SoundFile, SEEK_CUR

# scan through each file
# take max pressure
# append to PianoNoPedal.csv as an "amplitude" column

def main():
    noteLines = open("/Users/simonherron/Sampler/Piano/PianoNoPedal.csv").read().split("\n")
    outputPath = "/Users/simonherron/Sampler/Piano/SpacedOmni/"
    velocityLayers = ["pp", "mp", "f"]
    
    for noteIndex in range(1, len(noteLines)-1):
        noteComponents = noteLines[noteIndex].split(",")
        if noteComponents[7] != "d":
            fileNameComponents = ["Piano", "SpacedOmni", "NoPedal", noteComponents[4], noteComponents[5], str(velocityLayers.index(noteComponents[1]) + 1), noteComponents[1], noteComponents[2]]
            fileName = "_".join(fileNameComponents)
            
            theWave = SoundFile(outputPath + fileName + ".wav")
            theSize = theWave.frames
            theDuration = round(theSize / 48000, 2)
            
            firstSec = theWave.read(frames = 48000).T
            firstSec = abs(firstSec)
            
            maxL = max(firstSec[0])
            maxR = max(firstSec[1])
            theMax = max([maxL, maxR])
            
            maxLoc = np.argwhere(firstSec == theMax)[0][1]
            
            noteComponents.extend([str(theDuration), str(theMax), str(maxLoc)])
            newLine = ",".join(noteComponents)
            noteLines[noteIndex] = newLine
            
#            print(fileName + " Duration: " + str(theDuration) + " Max: " + str(theMax) + " at: " + str(maxLoc))
    
    output = open("/Users/simonherron/Sampler/Piano/PianoNoPedalData.csv", "wt")
    output.write("\n".join(noteLines))
    output.close()


main()
