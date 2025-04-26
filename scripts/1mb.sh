#!/bin/bash

# Filter out files > 1MB

mkdir -p big
find final/widget -type f -size +1M -exec mv "{}" big/ \;
find final/annot -type f -size +1M -exec mv "{}" big/ \;
