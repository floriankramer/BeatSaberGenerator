#!/bin/bash
source ./setup_env.sh

for f in $(find $1 -type f -name "*.ogg"); do
  NAME=$(basename "$f")
  python ./src/generate.py -i "$f" "$2/$NAME"
done
