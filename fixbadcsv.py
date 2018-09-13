#!/usr/bin/env python3
import sys, os
for fn in sys.argv[1:]:
    with open(fn, 'r') as infile:
        input = infile.readlines()
        if len(input) == 1:
            input = input[0].replace('Leadership 101,', 'Leadership 101!')
            input = ['101,' + s for s in input.split('101,')]
            input[0] = input[0][4:]

        print(fn, len(input))
        if len(input) >= 148:
            with open(fn, 'w') as outfile:
                out = '\n'.join(input)
                out = out.replace('Leadership 101!','Leadership 101,')
                outfile.write(out)
                outfile.write('\n')
