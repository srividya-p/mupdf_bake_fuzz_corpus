#!/usr/bin/env bash
dir="${1:-.}"

# Gather all sizes
mapfile -t sizes < <(find "$dir" -maxdepth 1 -type f -name '*.pdf' -printf '%s\n')

# If no files, exit
if [ ${#sizes[@]} -eq 0 ]; then
  echo "No PDFs in $dir"
  exit 0
fi

# Compute min/max
min=$(printf '%s\n' "${sizes[@]}" | sort -n | head -n1)
max=$(printf '%s\n' "${sizes[@]}" | sort -n | tail -n1)

echo "PDF count: ${#sizes[@]}"
echo "Min size : $((min/1024))K (${min} bytes)"
echo "Max size : $((max/1024/1024))M (${max} bytes)"
echo

# Bucket into ranges and count
printf '%s\n' "${sizes[@]}" | \
awk '
{
  if      ($1 <   100*1024) r="<100K";
  else if ($1 <  1024*1024) r="100K-1M";
  else if ($1 <  5*1024*1024) r="1M-5M";
  else if ($1 < 10*1024*1024) r="5M-10M";
  else                        r=">=10M";
  buckets[r]++;
}
END {
  print "Size distribution:";
  for (b in buckets) printf("  %8s : %d\n", b, buckets[b]);
}'
