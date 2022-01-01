#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy.fft import rfft, fftfreq
from scipy.signal import flattop, hamming
from soundfile import SoundFile
import numpy as np


def dft(x, freq, sampleRate):
    N = len(x)
    output = []
    
    for k in range(N//2): # only care about the first half of frequencies
        val = 0
        for n in range(N): #i.e. 0 through N-1
            val += x[n] * np.exp(-2j*np.pi*k*n/N)
        
        output.append(val)
    
    return np.abs(output)

def isolateFreq(signal, freq, sampleRate):
    N = len(signal)
    allFreqs = 5
    k = round(freq * (N * 1/sampleRate))
    
    return np.abs(np.sum(signal * np.exp(-2j * np.pi * k * np.arange(N) / N)))


waveFile = SoundFile("/Users/simonherron/Sampler/Piano/08/Spaced Omni_08.wav", mode = "rb")
#waveFile.seek(515675250) #end
#waveFile.seek(179382000) #middle
waveFile.seek(176000000) #E2 transient


nfft = 2**11
T = 1/48000


data = waveFile.read(frames = nfft)[:,0]

window = hamming(nfft, sym = False)
signal = data * window




yf = np.abs(rfft(data))
xf = fftfreq(nfft, T)[:nfft//2]

print(len(xf))
print(xf[0:50])
print(len(yf))
print(yf[0:50])

#yf2 = dft(data)
#print(len(yf2))
#print(yf2[0:50])

f = isolateFreq(data, 85, 48000)
print(f)


freqcutoff = np.searchsorted(xf, 2000)

#print(freqcutoff)


plt.plot(xf[0:freqcutoff], yf[0:freqcutoff], "o")
#plt.plot(xf[0:freqcutoff], yf2[0:freqcutoff], "o", color = "red")



#plt.show()

