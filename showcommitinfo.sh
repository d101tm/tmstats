#!/bin/bash
function getit {  ts=$(git log -1 --format="%cd %<(80,trunc) %s" --date=format-local:"%Y-%m-%d %H:%M:%S" -- "$1"); echo "$ts $1" ; }

list=$(find . -iname '*.py' -o -iname '*.sh' -o -iname '*.sql' | sort)
for i in $list 
do
    getit "$i"
done
