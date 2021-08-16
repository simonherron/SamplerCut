#!/usr/bin/env python3

import numpy as np
#sys.path.append("/usr/local/lib/python3.9/site-packages")

import soundfile as sf
from soundfile import SoundFile, SEEK_CUR

theWave = SoundFile("/Users/simonherron/Documents/Sampler/Piano/08/SpacedPop_08.wav")

#theWave.seek(294000)
    

notes = [0]

prevSection = np.max(np.abs(theWave.read(frames = 1)))
theWave.seek(0)

for b in theWave.blocks(blocksize = 1000, frames = 20000000):
    thisSection = np.sum(np.abs(b))
    
    if (thisSection > prevSection * 6): # and (prevSection < 0.002) and (thisSection > 0.001):
        transient = theWave.tell() - 1000
        
        print("transient at: " + str(transient) + " with amplitude: " + str(round(thisSection, 6)) + " prev: " + str(round(prevSection, 6)))
        
        notes.append(transient)
        
        
        
#        theWave.seek(-1, whence = SEEK_CUR)

    prevSection = thisSection



theWave.seek(0)
for i in range(1, len(notes)):
    toWrite = theWave.read(frames = notes[i] - notes[i-1])
    sf.write(str(i) + ".wav", toWrite, 48000)
