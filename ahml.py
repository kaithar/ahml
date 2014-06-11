from __future__ import print_function
import sys
import re

mdsection = re.compile("^=+\n$")
mdsubsec = re.compile("^-+\n$")

input = sys.stdin.readlines()
lineno = 0
lenin = len(input)
for lineno in range(0,len(input)):
    lineno += 1
    if (lineno == lenin):
        break
    line = input[lineno]
    if (line[0] == '#'):
        if (line[1] == '!'):
            continue
        elif(line[1] == '#'):
            # This will be the control instructions
            pass
        else:
            # This will be comments
            pass
        continue
    if ((lineno+1 < len(input)) and (len(line) == len(input[lineno+1]))):
        if (mdsection.match(input[lineno+1])):
            print("section header!")
        elif(mdsubsec.match(input[lineno+1])):
            print("subsec header!")
        print(line)
        print(input[lineno+1])


