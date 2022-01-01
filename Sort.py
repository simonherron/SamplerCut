#!/usr/bin/env python3

import shutil
import os

startDir = "/Users/simonherron/Sampler/Piano/SpacedOmni"

for aFile in os.listdir(startDir):
    if aFile != ".DS_Store":
        comps = aFile.split("_")
        newName = comps[6] + "_" + comps[7][0:-4]
        dest = startDir + "_Kontakt/" + newName + "/" + aFile
        print(dest)
        
        shutil.copyfile(startDir + "/" + aFile, dest)
