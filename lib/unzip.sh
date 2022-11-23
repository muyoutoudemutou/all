#!/bin/bash

cd bountyFile

if ls | grep ".zip" &> /dev/null; then
 unzip '*.zip' &> /dev/null
 cat *.txt >> alltargets.txt
 rm -f *.zip