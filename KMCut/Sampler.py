#!/usr/bin/env python3
import os

def main():
    path = "/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv"
    index = int(os.environ["KMVAR_samplerIndex"])
    standardStamp = [1, 27, 145, 198, 384, 386] #511
    
    csvTxt = open(path, "rt").read()
    lines = csvTxt.split("\n")
    theLine = lines[index].split(",") # it's effectively base 1 already becuase of the header row
    previousLine = lines[index - 1].split(",")
    twoPrevious = lines[index - 2].split(",")
    
    fileNameComponents = ["Piano", "SpacedOmni", "NoPedal", theLine[5], theLine[1], theLine[2]]
    
    delete = str(theLine[-1] == "d")
    if delete:
        fileNameComponents.append("d")
        
    if previousLine[-1] == "d" or twoPrevious[-1] == "d" or index == 1:
        method = "seek"
        moveBack = previousLine[-1] == "d" and (not (index in standardStamp))
        value = seek(theLine, lines[1].split(","), moveBack)
    else:
        method = "advance"
        value = advance(theLine, previousLine)

    
    
    fileName = "_".join(fileNameComponents)
    print("{\"method\": \"" + method + "\", \"value\": " + value + ", \"fileName\": \"" + fileName + "\", \"delete\": \"" + delete + "\"}")
    
    
    
def seek(theLine, firstLine, moveBack):
    firstPitch = 24 #int(os.environ["KMVAR_samplerFirstPitch"])
    offset = firstPitch - int(firstLine[-2])
    stamp = int(theLine[-2]) + offset
    if moveBack:
        return "\"" + str(stamp - 1) + " 3 4 1\""
    else:
        return "\"" + str(stamp) + " 0 0 0\""
    
    
def advance(theLine, previousLine):
#    if index == 1:
#        return str(int(os.environ["KMVAR_samplerFirstPitch"]) - 1)
#    else:
    previousTimeCode = int(previousLine[-2]) # time code is second to last column
    timeCode = int(theLine[-2])
    return str(timeCode - previousTimeCode) # how far to advance the cursor in Logic


def test(theIndex):
    testLine = lines[theIndex].split(",")
    return (testLine[-1] == "d" and not (theIndex in overrideIndeces))




#
#
#if test(index - 1): # should be seek to back thingy
#    delete = "True"
#    fileNameComponents.append("d")
##    method = "seek"
#    value = seek()
#elif test(index - 2): # should be normal seek for the purposes of resetting
#    delete = "False"
##    method = "seek"
#    value = seek()
#else:
#    delete = "False"
##    method = "advance"
#    value = advance()
#
#
#
#

main()
