# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import re

# Cthulu inspired black magic from your nightmares!
def wordsToNumbers(string):
    numDict = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
               "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
    for word in string.split():
        if word.lower() in numDict:
            string = string.replace(word, numDict[word.lower()])
    return string

def processFilters(string, filters):
    outstring = ''
    if filters[0] == 'first_letter_of_words' or filters[0] == 'flow':
        for word in string.split():
            outstring = outstring + word[0]
    elif filters[0] == 'lower':
        outstring = string.lower()
    elif filters[0] == 'upper':
        outstring = string.upper()
    elif filters[0] == 'reverse_chars':
        outstring = string[::-1]
    elif filters[0] == 'reverse_words':
        outstring = " ".join(string.split()[::-1])
    elif filters[0] == 'words_to_numbers' or filters[0] == 'wtn':
        outstring = wordsToNumbers(string)
    elif '_padding' in filters[0]:
        formatString = filters[0].replace('_padding', '')
        outstring = formatString.format(string)
    elif '_character' in filters[0]:
        word_num = filters[0].replace('_character', '')
        if ':' in word_num:
            start = int(word_num.split(':')[0])
            end = int(word_num.split(':')[1])
            outstring = string[start:end]
        else:
            outstring = string[int(word_num)]
    elif '_word' in filters[0]:
        word_num = filters[0].replace('_word', '')
        if ':' in word_num:
            start = int(word_num.split(':')[0])
            end = int(word_num.split(':')[1])
            outstring = " ".join(string.split()[start:end])
        else:
            outstring = string.split()[int(word_num)]
    else:
        outstring = string
    if filters[1:]:
        outstring = processFilters(outstring, filters[1:])
    return outstring

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
    # FIXME: Account for variable not in dataset case.
    for var in varList:
        filters = []
        if '||' in var:
            rawVar = var.strip('{{').strip('}}')
            filters = rawVar.split('||')
            newVar = '{{' + filters[0] + '}}'
        else:
            newVar = var
        mergedDict[var] = dataSet[newVar[2:-2]]
        if filters:
            mergedDict[var] = processFilters(mergedDict[var], filters[1:])
    return mergedDict

def mangleString(rawstring, dataSet):
    for var in dataSet.keys():
        # Needed if mangleString is called directly, without processing through the other functions.
        # This is slightly more efficient, but unmatched template variables will be left in place,
        # and planned future functionality will not work.
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
    newstring = mangleString(rawstring, varDict)
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
