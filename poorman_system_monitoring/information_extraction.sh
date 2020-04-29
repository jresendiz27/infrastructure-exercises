#!/usr/bin/env bash
rm -rf information.txt
head -n 1 /proc/meminfo | awk '{print $2}' >> information.txt
ps -o pid,user,%mem,command ax >> information.txt
cat information.txt
