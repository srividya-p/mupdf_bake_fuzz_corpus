#!/bin/bash

# Must contain widgets (may also contain annotations)

DEST=final/widget
mkdir -p $DEST

for file in "$1"/*.pdf; do
    if [[ -f "$file" ]]; then
        if grep -q "/Widget" "$file"; then
            dest="$DEST/$(basename "$file")"
            if [[ -e "$dest" ]]; then
                echo "Skipping $(basename "$file"): already exists in $DEST/"
            else
                mv "$file" $DEST/
                echo "Moved $(basename "$file")"
            fi
        else
            echo "$(basename "$file"): no /Widget found"
        fi
    fi
done
