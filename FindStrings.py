#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import string
import sys
import enchant
import re
import multiprocessing
from itertools import repeat
from tqdm import tqdm
from nltk import ngrams

manager = multiprocessing.Manager()
finalLinks = manager.list()
finalLinksLine = manager.list()

d = enchant.Dict("en_US")
fileName = ""

#-----------------------------------------------
# Extracts all strings - Generator function to not overload the memory
#-----------------------------------------------
def strings(filename, min=4):
    with open(filename, errors="ignore") as f: 
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

#-----------------------------------------------
# 1. Links function
# Extracts links
#-----------------------------------------------
def checkForLinks(currentString, line):
    url = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", currentString) 
    if len(url) > 0:
        finalLinks.append(url[0])
        finalLinksLine.append(line)
        return True
    else:
        return False
        

#-----------------------------------------------
# 2. Find interesting strings
# Extracts links
#-----------------------------------------------       
def checkForWords(currentString, line, minimum):


    evalString1 = currentString.replace("\n", "")
    evalString2 = re.sub(' ', '', evalString1)
    evalString2 = re.sub('[^\w]', '', evalString2)
    evalString2 = re.sub('\d+', '', evalString2)

    if (len(evalString2) > minimum-2):
        
        for n in range(5, 8, 1):
            permutations = ngrams(list(evalString2), n) #Generate random words from the string
            for x in permutations:
                joined = "".join(x) #Each ngram is a tuple, join it into a string
                # If there is a valid english word in the string (based on pyenchant dict)
                if (d.check(joined) == True):
                    tqdm.write("Found interesting string: " + str(line) + ": " + evalString1 + " ---> " + joined)
                    return True




#-----------------------------------------------
# Key Operation Functions
#-----------------------------------------------     

line = 1
pbar = tqdm(None, "Analysing lines" , None, None, None, None, 1.5, 5.0, 0)
options = {"-L": False, "-S": False, "-h": False, "--help": False, "-M": 10 }

def handleSwitching(s):
    global line
    global pbar
    global options
    
    # <s> is the currentString and <line> is the current line no.
    if (options["-L"] == True):
        checkForLinks(s, line)
    if (options["-S"] == True):
        checkForWords(s, line, options["-M"])

    pbar.update()
    line += 1
    


def helpPrint():
    tqdm.write("Usage: FindStrings.py <options> fileName")
    tqdm.write("------------------------[Help Menu]------------------------")
    tqdm.write("Options: ")
    tqdm.write("    -M <Minimum_Characters> | Scan strings of given minimum characters. Default of 10 chars.")
    tqdm.write("    -S | Scan for interesting strings. Outputs as it scans (Warning, VERY spammy for large files!)")
    tqdm.write("    -L | Scan for links. Outputs at the end [Default]")
    tqdm.write("    -h --help | Show this menu")
    tqdm.write("")
    tqdm.write("Default command: FindStrings.py -M 10 -L fileName")



if __name__ == "__main__":

    if len(sys.argv) == 1:
        tqdm.write("Error: No file or options supplied. Please supply the filename!")
        helpPrint()
        sys.exit()
    else:
        if (len(sys.argv) > 2):
            # Arguments Parser
            counter = 1
            while counter < len(sys.argv)-1:
                if (sys.argv[counter] in options):
                    
                    #Handle help (-h) option
                    if (sys.argv[counter] == "-h" or sys.argv[counter] == "--help"):
                        helpPrint()
                        sys.exit()
                    
                    #Everything else
                    else:
                        options[sys.argv[counter]] = True

                        #Handle -M option
                        if (sys.argv[counter] == "-M"): #Get minimum character length per string
                            try:
                                options["-M"] = int(sys.argv[counter+1]) 
                                counter += 1 #Skip the next parameter since next option is a value
                            except:
                                #If no min. characters provided, leave to default which is 10
                                tqdm.write("-M option provided with no value, using default of 10")
                                
                else:
                    tqdm.write("Error: Unknown option " + str(sys.argv[counter]))
                    sys.exit()
                counter += 1

        else:
            if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
                helpPrint()
                sys.exit()

            #Default options
            tqdm.write("No options provided. Using default options")
            options["-L"] = True
        
        fileName = sys.argv[len(sys.argv)-1]

        tqdm.write("Begining analysis... this may take a while")
        tqdm.write("")
        tqdm.write("--------------------------[Results]--------------------------")
        tqdm.write("[Note:] The numbers are NOT line numbers, they are based on the order of strings")
        tqdm.write("")
        pool = multiprocessing.Pool()
        try:
            
            #Main looping through each line of string
            for i in strings(fileName):
                if (len(i) > options["-M"]):
                    pool.apply_async(handleSwitching, args=(i,))
                
        finally:
            pool.close()
            pool.join()

            tqdm.write("--------------------------[Links]--------------------------")
            for x in range(0, len(finalLinks), 1):
                tqdm.write("Line " + str(finalLinksLine[x]) + " | " + str(finalLinks[x]))
            
           