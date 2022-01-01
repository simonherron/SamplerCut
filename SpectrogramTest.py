#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib
import scipy.signal as signal
from soundfile import SoundFile
import numpy as np


def logscale(x):
    return 10*np.log10(x)

def findPeaks(x):
    coolDown = int(0.5 * 48000 / 2**8) # half second of cool down
    print("cool down: " + str(coolDown))

    output = []
    for i in range(len(x-1)):
            if x[i] > 4e-10:
                if (len(output) == 0) or (i - coolDown > output[-1]):
                    if np.mean(x[(i+1) : (i+5)]) > np.max(x[(i-10) : i]) * 4:
                        if np.any(x[(i+1) : (i+10)] > 1e-11):
                                output.append(i-1)

    return output



waveFile = SoundFile("/Users/simonherron/Sampler/Piano/08/Spaced Omni_08.wav", mode = "rb")
#waveFile.seek(515675250) #end
waveFile.seek(179382000) #middle
data = waveFile.read(frames = int(0.15*10**7))[:,0]


output, ybins, xbins, im = plt.specgram(data, Fs = 48000, NFFT = 2**13, interpolation = "none", noverlap = 2**13 - 2**6) #NFFT: 2**7, overlap: 2**6
plt.close()

cutoff = np.searchsorted(ybins, 900) # finds index of first element great than 10000. Don't care about any frequency information higher than this
output = output[0:cutoff]
ybins = ybins[0:cutoff]

print(len(xbins))





freqIndex_1 = 14 #np.searchsorted(ybins, 200) # finds index of first element greater or equal to 1200, i.e. the highest fequency of the background noise
print(freqIndex_1)
freq_1 = ybins[freqIndex_1]
mags_1 = output[freqIndex_1]
mags_0 = output[1] # 4, 10, 15

print(mags_1[0:100])

peaks = findPeaks(mags_1)
print(peaks)

#transientIndex_1 = peaks[0]
#transient_1 = xbins[transientIndex_1]

print(ybins[0:100])



fig, ax = plt.subplots()
mesh = ax.pcolormesh(xbins, ybins, logscale(output))
fig.colorbar(mesh, ax=ax)
#plt.xlim([0, 50])
#plt.ylim([0, 100])

plt.axhline(y = freq_1, linestyle = "--", color = "red")



toTest = [14, 28]



for i in peaks:
    plt.axvline(x = xbins[i], linestyle = "--", color = "purple")
    
for k in toTest:
    plt.axhline(y = ybins[k], linestyle = "--", color = "orange")
        
plt.show()


fig, ax = plt.subplots(nrows=len(toTest)) #, figsize=(8, 8))

for j in range(len(toTest)):
    ax[j].plot((output[toTest[j]]), "o")
    for i in peaks:
        ax[j].axvline(x = i, linestyle = "--", color = "purple")

plt.show()



#    plt.plot(logscale(output[:,transientIndex_1]), "o")
#    plt.show()

#plt.plot(logscale(mags_1))
#plt.show()


#upwards = output[:,firstLoc]

#print(upwards)
#plt.plot(upwards)
#plt.show()





#
#divs = ybins[1:] / testFreq # excluding the first element of ybins, which is always 0
#remains = divs - np.floor(divs)
#theIndex = int(np.where(remains == remains.min())[0]) + 1 # because we removed the first element
#
#print(theIndex)
#print(ybins[theIndex])
#print(ybins[theIndex] / testFreq)
#print(6)
#print(ybins[6])
#print(ybins[6]/testFreq)






#ax1.set(title='Specgram')
#fig.colorbar(im, ax=ax1)
#
#


#mesh = plt.pcolormesh(output[:,])
#plt.xlim([25, 30])

#plt.colorbar(mesh)
#plt.show()











#plt.plot(output[0][0:10000])
#plt.ylim([0, 0.1])
#plt.show()

#plt.plot(output[1][0:10000])
#plt.show()

#
#t = [5, 25]
#for i in t:
#    plt.plot(output[i])
##    plt.ylim([-2e-6, 2e-5])
#    plt.show()



#peaks = signal.find_peaks(output[5], distance = 20*200, height = 0.0005)[0]
#peaks = signal.find_peaks(output[5], distance = 400, height = 3*10^-6)[0]
#
#print(len(peaks))
#print(peaks)
#
#plt.plot(output[5])
#
#for xc in peaks:
#    plt.axvline(x=xc, color = "red")
#plt.show()
