#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import string
import sys
import enchant
import re
from tqdm import tqdm
from nltk import everygrams

d = enchant.Dict("en_US")
fileName = ""

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please supply the filename!")
        print("Usage: FindStrings.py <filename>")
        sys.exit();
    else:
        fileName = sys.argv[1]
        print("Begining analysis... this may take a while")
        
def strings(filename, min=4):
    with open(filename, errors="ignore") as f:  # Python 3.x
        result = ""
        for c in f.read():
            if c in string.printable:
                result += c
                continue
            if len(result) >= min:
                yield result
            result = ""
        if len(result) >= min:  # catch result at EOF
            yield result
links = []
linksLine = []
linksCounter = 0

def checkForLinks(currentString, line):
    #Check for links
    url = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", currentString) 
    if len(url) > 0:
        links.extend(url)
        global linksCounter
        linksCounter += len(url)
        linksLine.append(line)
        return True
    else:
        return False
        
        
interestingStrings = []
interestingStringsLine = []
interestingStringsString = []
interestingStringsCounter = 0
def checkForWords(currentString, line):
    if (len(currentString) > 8):
        evalString1 = currentString.replace("\n", "")
        evalString2 = evalString1.replace(" ", "")
        evalString2 = re.sub('[^\w]', '', evalString2)
        evalString2 = re.sub('\d+', '', evalString2)
    
        if (len(evalString2) > 8):
            #Generate random words from the string
            permutations = [''.join(_ngram) for _ngram in everygrams(evalString2)]
            for x in permutations:
                # If there is a valid english word in the string (based on pyenchant dict), add to interesting strings
                if (len(x) > 2):
                    if (d.check(x) == True):
                        interestingStrings.append(evalString1) #Add original string for human analysis
                        interestingStringsLine.append(line)
                        interestingStringsString.append(x)
                        global interestingStringsCounter
                        interestingStringsCounter += 1
                        break
    else:
        return None
        

#Main looping through each line of string
line = 1
for s in tqdm(strings(fileName)):
    if (len(s) > 6):
        if (checkForLinks(s, line) == False):
            checkForWords(s, line)
    line += 1

#Finished running program
print("--------------------------[Results]--------------------------")
print("[Note:] The numbers are NOT line numbers, they are the string no. from the <strings> command")
print("")
print("-------------[Links]-------------")
print("Found " + str(linksCounter) + " link(s)")
for x in range(0, len(links), 1):
    print(str(linksLine[x]) + ": " + links[x])
print("")
print("-------------[Interesting Strings (With valid english words) ]-------------")
print("Found " + str(interestingStringsCounter) + " interesting strings(s)")
for x in range(0, len(interestingStrings), 1):
    print(str(interestingStringsLine[x]) + ": " + interestingStrings[x] + " --> " + interestingStringsString[x])

