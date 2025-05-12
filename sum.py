import os
import sys
import fitz
import logging
import statistics

from pdfrw import PdfReader, PdfName

logging.getLogger("pdfrw").setLevel(logging.CRITICAL)


def human_readable_size(num, suffix="B"):
    """Convert a byte count into a human-readable string."""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"


def count_objects_mupdf(path):
    """Return (annotation_count, widget_count) across all pages of a PDF."""
    try:
        doc = fitz.open(path)
    except Exception:
        return 0, 0
    annots = 0
    widgets = 0
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        annots += len(list(page.annots() or []))
        widgets += len(list(page.widgets() or []))

    doc.close()
    return annots, widgets


def count_objects_pdfrw(path):
    """Return (annotation_count, widget_count) for the first page of a PDF."""
    try:
        reader = PdfReader(path)
    except Exception:
        return 0, 0
    page = reader.pages[0]  # assume one‐page PDFs
    annots = getattr(page, "Annots", []) or []
    widget_count = 0
    for a in annots:
        try:
            if a.Subtype == PdfName.Widget:
                widget_count += 1
        except Exception:
            continue
    annot_count = len(annots) - widget_count
    return annot_count, widget_count


# ════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════
if len(sys.argv) == 1:
    print("No input directory, exiting.")
    exit(0)

input_dir = sys.argv[1]
sizes = []

only_annots = []
only_widgets = []
both = []
neither = []

total_annots = 0
total_widgets = 0

bucket_counts = {
    "<10KB": 0,
    "10-50KB": 0,
    "50-200KB": 0,
    "200-500KB": 0,
    ">500KB": 0,
}

print("File statistics:\n")
for fname in sorted(os.listdir(input_dir)):
    if not fname.lower().endswith(".pdf"):
        continue
    path = os.path.join(input_dir, fname)

    a_count, w_count = count_objects_mupdf(path)
    size_bytes = os.path.getsize(path)
    sizes.append(size_bytes)
    size_hr = human_readable_size(size_bytes)

    total_annots += a_count
    total_widgets += w_count

    # classify
    if a_count > 0 and w_count == 0:
        only_annots.append(fname)
    elif w_count > 0 and a_count == 0:
        only_widgets.append(fname)
    elif w_count > 0 and a_count > 0:
        both.append(fname)
    else:
        neither.append(fname)

    # bucket
    if size_bytes < 10 * 1024:
        bucket_counts["<10KB"] += 1
    elif size_bytes < 50 * 1024:
        bucket_counts["10-50KB"] += 1
    elif size_bytes < 200 * 1024:
        bucket_counts["50-200KB"] += 1
    elif size_bytes < 500 * 1024:
        bucket_counts["200-500KB"] += 1
    else:
        bucket_counts[">500KB"] += 1

    # print(f"{fname}: {a_count:3d} annotations, {w_count:3d} widgets, {size_hr}")

# per‐file done
print("\n═══════════════════════════════════════════")
print("PDF classification summary:")
print("───────────────────────────────────────────")
print(f"PDF count                       : {len(sizes)}")
print(f"Only annotations                : {len(only_annots)}")
print(f"Only widgets                    : {len(only_widgets)}")
print(f"Both annots+widgets             : {len(both)}")
print(f"Neither annotations nor widgets : {len(neither)}")

# size summary
if sizes:
    print("\n═══════════════════════════════════════════")
    print("File size summary:")
    print("───────────────────────────────────────────")
    print(f"  Smallest file: {human_readable_size(min(sizes))}")
    print(f"  Largest  file: {human_readable_size(max(sizes))}")
    print(f"  Average size : {human_readable_size(sum(sizes) / len(sizes))}")

# bucket distribution
if sizes:
    # Compute quartiles (three cut-points dividing data into four equal groups)
    q1, q2, q3 = statistics.quantiles(sizes, n=4)
    # Build dynamic buckets
    dynamic_buckets = [
        (f"≤{human_readable_size(q1)}", lambda s: s <= q1),
        (
            f"{human_readable_size(q1)}–{human_readable_size(q2)}",
            lambda s: q1 < s <= q2,
        ),
        (
            f"{human_readable_size(q2)}–{human_readable_size(q3)}",
            lambda s: q2 < s <= q3,
        ),
        (f">{human_readable_size(q3)}", lambda s: s > q3),
    ]
    # Initialize counts
    bucket_counts = {label: 0 for label, _ in dynamic_buckets}

    # Tally
    for s in sizes:
        for label, test in dynamic_buckets:
            if test(s):
                bucket_counts[label] += 1
                break

    # Print dynamic distribution
    print("\n═══════════════════════════════════════════")
    print("Size distribution (dynamic quartiles):")
    print("───────────────────────────────────────────")
    for label, _ in dynamic_buckets:
        print(f"  {label:15s}: {bucket_counts[label]}")

# total counts
print("\n═══════════════════════════════════════════")
print("Total objects across all PDFs:")
print("───────────────────────────────────────────")
print(f"  Total annotations = {total_annots}")
print(f"  Total widgets     = {total_widgets}")

if neither:
    # Build full paths
    paths = [os.path.join(input_dir, f) for f in neither]
    # Print the rm command
    print("\nTo delete all PDFs without any annotations or widgets, run:")
    print("rm " + " ".join(f"'{p}'" for p in paths))
else:
    print("\nNo “neither” PDFs to remove.")
