#!/usr/bin/env python3
import os

path = "/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv"

firstPitch = int(os.environ["KMVAR_samplerFirstPitch"])
index = int(os.environ["KMVAR_samplerIndex"])

csvTxt = open(path, "rt").read()
lines = csvTxt.split("\n")

theLine = lines[index].split(",") # it's effectively base 1 already becuase of the header row

if index == 1:
    timeCode = firstPitch
else:
    firstLine = lines[1].split(",")
    offset = firstPitch - int(firstLine[-2])
    timeCode = int(theLine[-2]) + offset
    
#    previousLine = lines[index - 1].split(",")
#    previousTimeCode = int(previousLine[-2]) # time code is second to last column
#    previousTimeCode = 0
#advance = timeCode - previousTimeCode # how far to advance the cursor in Logic

fileNameComponents = ["Piano", "SpacedOmni", "NoPedal", theLine[4], theLine[0], theLine[1]]
if theLine[-1] == "d":
    fileNameComponents.append("d")

fileName ="_".join(fileNameComponents)

print("{\"timeCode\": " + str(timeCode) + ", \"fileName\": \"" + fileName + "\"}")
