#!/bin/bash
source ./setup_env.sh

# find the last arguemnt
for OUTPUT; do true; done

MAX_JOBS=$(nproc --ignore=1)
CURRENT_JOBS=0

for inp in "$@"; do
  if ! [ "$inp" = "$OUTPUT" ] ; then 
    for f in $(find $inp -type f -name "*.ogg"); do
      NAME=$(basename "$f")
      python ./src/generate.py -i "$f" "$OUTPUT/$NAME" &
      CURRENT_JOBS=$(($CURRENT_JOBS + 1))
      if [ $CURRENT_JOBS -eq $MAX_JOBS ] ; then
        # wait for all currently queued processes
        wait
        CURRENT_JOBS=0
      fi
    done
  fi
done

# wait for the remaining processes
wait
