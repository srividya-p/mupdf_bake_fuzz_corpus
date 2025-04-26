#!/bin/bash

# Only annotations but not widgets

mkdir -p final/annot

for file in $1/*.pdf; do
    grep -q "/Annots" "$file" && ! grep -q "/Widget" "$file" && echo "$(stat --format="%s" "$file") $file"
done | sort -n | head -n 1 | awk '{print $2}' | xargs -I{} mv "{}" annot/