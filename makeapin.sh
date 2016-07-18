#!/bin/sh

# This makes one pin.  

convert empty.png -quality 100 -font Helvetica-Bold -pointsize 11   -fill '#a38aff' -draw 'rectangle 1,1 18,10' -fill black  -draw "gravity Center text 1,-2 '$1'"  $1.png 
