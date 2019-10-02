#!/usr/bin/env python3
""" Make all pins - needs Python 3.6 or better because it uses f-strings  

Run in the directory containing pins - uses 'empty.png' as the source pin.

"""

import sys

fillcolors = {
    'A': '#ffa500',
    'B': '#66ffff',
    'C': '#add8e6',
    'D': '#f08080',
    'E': '#cccc00',
    'F': '#a3d7a3',
    'G': '#bdb76b',
    'H': '#6cd9b5',
    'I': '#a38aff',
    'J': '#ffff00'
}

divisions = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
areas = ['1', '2', '3', '4', '5', '6', 'M']
font = 'ConsolasB'
loff = 2
roff = 1
toff = -2
try:
    font = sys.argv[1]
except IndexError:
    pass

def makecmd(leftdiv, rightdiv, leftstart, rightstart, leftitem, rightitem, outfile):
    return f"convert pin.png -fill '{fillcolors[leftdiv]}' -draw 'rectangle 1,1 9,10' -fill '{fillcolors[rightdiv]}' -draw 'rectangle 10,1 18,10' -draw 'image SrcOver {leftstart},1 0,0 {leftitem}.png' -draw 'image SrcOver {rightstart},1 0,0 {rightitem}.png' {outfile}.png"



for d in divisions:
    leftitem = d
    leftdiv = d
    rightdiv = d
    for rightitem in areas:
        if rightitem != 'M':
            leftstart = 2
            rightstart = 10
            outfile = leftitem+rightitem
            label = leftitem+rightitem
        else:
            leftstart = 1
            rightstart = 10 
            outfile = leftitem+rightitem
            label = leftitem
        cmd = f"convert pin.png -fill '{fillcolors[leftdiv]}' -draw 'rectangle 1,1 18,10' -fill black -font {font} -pointsize 11 -draw 'gravity Center text 0,-2 {label}' {outfile}.png"
        print(cmd)
    # Now, do the multi-division pins:
    leftstart = 0
    rightstart = 11
    for rightitem in divisions:
        if rightitem > d:
            rightdiv = rightitem
            outfile = leftitem+rightitem
            cmd = f"convert pin.png -fill '{fillcolors[leftdiv]}' -draw 'rectangle 1,1 9,10' -fill '{fillcolors[rightdiv]}' -draw 'rectangle 10,1 18,10' -fill black -font {font} -pointsize 11  -draw ' gravity West text {loff},{toff} {leftdiv}'  -draw 'gravity East text {roff},{toff} {rightdiv}' {outfile}.png"
            print(cmd)

