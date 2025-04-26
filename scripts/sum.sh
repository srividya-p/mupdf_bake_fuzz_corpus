#!/bin/bash

echo "Counting PDFs in $1..."

# Initialize counters
both_count=0
only_annots_count=0
only_widgets_count=0

# Loop through each PDF
for file in $1/*.pdf; do
    has_annots=$(grep -q "/Annots" "$file" && echo 1 || echo 0)
    has_widgets=$(grep -q "/Widget" "$file" && echo 1 || echo 0)

    if [[ "$has_annots" == "1" && "$has_widgets" == "1" ]]; then
        both_count=$((both_count + 1))
    elif [[ "$has_annots" == "1" ]]; then
        only_annots_count=$((only_annots_count + 1))
    elif [[ "$has_widgets" == "1" ]]; then
        only_widgets_count=$((only_widgets_count + 1))
    fi
done

echo
echo "Summary:"
echo "---------"
echo "Total PDFs                        : $(ls $1/*.pdf | wc -l)"
echo "PDFs with both /Annots and /Widget: $both_count"
echo "PDFs with only /Annots            : $only_annots_count"
echo "PDFs with only /Widget            : $only_widgets_count"
echo "Maximum PDF size                  : $(find $1 -type f -exec du -h {} + | \
    sort -hr | head -n 1 | awk '{print $1}')"
