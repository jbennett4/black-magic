# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import re

# Cthulu inspired black magic from your nightmares!
def getVarsFromString(rawstring):
    start = re.compile("{{")
    finish = re.compile("}}")
    try:
        sVarValues = start.finditer(rawstring)
        fVarValues = finish.finditer(rawstring)
    except:
        return []
    startList = []
    finishList = []
    for sIter in sVarValues:
        startList.append(sIter.span())
    for fIter in fVarValues:
        finishList.append(fIter.span())
    varList = []
    for varPos in range(len(startList)):
        varList.append(rawstring[startList[varPos][0]:finishList[varPos][1]])
    return varList

def mergeVars(varList, dataSet):
    mergedDict = {}
    for var in varList:
        mergedDict[var] = dataSet[var[2:-2]]
    return mergedDict

def mangleString(rawstring, dataSet):
    for var in dataSet.keys():
        # FIXME: This shouldn't be necessary...
        if not '{{' in var:
            newVar = '{{' + var
            if not '}}' in var:
                newVar =  newVar + '}}'
        else:
            newVar = var
        rawstring = rawstring.replace(newVar, str(dataSet[var]))
    return rawstring

def buildString(rawstring, dataSet):
    varList = getVarsFromString(rawstring)
    varDict = mergeVars(varList, dataSet)
    newstring = mangleString(rawstring, dataSet)
    return newstring

def buildCollection(collection, dataSet):
    outList = []
    for rawstring in collection:
        outList.append(buildString(rawstring, dataSet))

    return outList

def buildFile(infile, outfile, dataSet):
    with open(infile, 'r') as f:
        fileData = f.read().split('\n')
    processedList = buildCollection(fileData, dataSet)

    with open(outfile, 'w') as f:
        for line in processedList:
            f.write(line + '\n')
