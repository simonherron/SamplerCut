#!/usr/bin/env python3

import soundfile as sf
from soundfile import SoundFile, SEEK_CUR
import sys
import numpy as np

theWave = SoundFile("/Users/simonherron/Documents/Sampler/Piano/08/Spaced Omni_08.wav")

output = ["Amp"]

theWave.seek(407706000)

for b in theWave.blocks(blocksize = 200, frames = 4000000):
    vals = b.T[0]
    m = np.mean(np.abs(vals))
    output.append(str(m))

outputStr = "\n".join(output)
outputFile = open("outputMistake200.csv", "wt")
outputFile.write(outputStr)
outputFile.close()

#theWave.seek(int(sys.argv[1]))

#b = theWave.read(frames = 10).round(6)
#bt = b.T

#print(bt[0])
#print(bt[0].dot(bt[0]))
#print(bt[0])
#
#print(b)
#print(np.abs(b))
#print(np.sum(np.abs(b)))
