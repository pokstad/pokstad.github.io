#!/bin/bash
# --- Version history ---
#   0.4: added variable to store file path, and $2 for base file name
#        added variable to store desired reporting interval
#   0.3: added $1 to send in process ID at run time.
#   0.2: switched to $SECONDS for the loop. works.
#   0.1: didn't work well at all.
# --- Version history ---

# Usage: cputrack [PID] [filename]
#        replace [PID] with process ID #
#        replace [filename] with base file name to use (no extension)

filepath=`pwd`                      # modify as desired
interval=20                         # reports per minute
timelimit=6000                      # how long to run, in seconds

mydate=`date "+%H:%M:%S"`           # the timestamp
freq=$((60/$interval))              # for sleep function

while [ "$SECONDS" -le "$timelimit" ] ; do
  ps -p$1 -opid -opcpu -ocomm -c | grep $1 | sed "s/^/$mydate /" >> $filepath/$2.txt
  sleep 3
  mydate=`date "+%H:%M:%S"`
done