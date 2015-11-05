#!/bin/sh
cd ~/Downloads
let spacing=32
let line1=100
let left=420
let shadow=2
let line2=line1+spacing
let line3=line2+spacing
let line4=line3+spacing+spacing
let sleft=left+shadow
let sline1=line1+shadow
let sline2=line2+shadow
let sline3=line3+shadow
let sline4=line4+shadow


while getopts "d:c:m:" flag
do
    case "$flag" in
        d) district=$OPTARG;;
        c) count=$OPTARG;;
        m) month=$OPTARG;;
        ?) exit 1;;
    esac
done

if [ -z $district -o -z $count -o -z $month ] ; then
    echo 'District, Count, and Month are all required'
    echo "district $district"
    echo "count $count"
    echo "month $month"
    exit 1
fi

convert ~/Downloads/ed-achieve-base.jpg  -quality 85 -font /Library/Fonts/Microsoft/Arial\ Bold.ttf   -pointsize 26 -fill  black -draw "text $sleft,$sline1 'Congratulations to the $count District $district'" -draw "text $sleft,$sline2 'members who achieved one or more'" -draw "text $sleft,$sline3 'of their educational goals in $month.'" -draw "text $sleft,$sline4 'Will you be recognized next?'" -fill white   -draw "text $left,$line1 'Congratulations to the $count District $district'" -draw "text $left,$line2 'members who achieved one or more'" -draw "text $left,$line3 'of their educational goals in $month.'" -draw "text $left,$line4 'Will you be recognized next?'" out.jpg && open out.jpg  && ls -la out.jpg