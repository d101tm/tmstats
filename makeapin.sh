#!/bin/bash

# This makes one pin.  

convert empty.png -quality 100 -font Helvetica-Bold -pointsize 11   -fill '#a38aff' -draw 'rectangle 1,1 9,10' -fill '#B0E3F2' -draw 'rectangle 10,1 18,10' -fill black  -draw "gravity Center text 1,-2 '$1'"  $1.png 
