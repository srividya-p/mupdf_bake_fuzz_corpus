from pdfrw import PdfReader, PdfName
import os

def human_readable_size(num, suffix='B'):
    """Convert a byte count into a human-readable string."""
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

def count_objects_pdfrw(path):
    reader = PdfReader(path)
    page = reader.pages[0]  # assume one-page PDFs
    annots = getattr(page, "Annots", []) or []
    widget_count = sum(1 for a in annots if a.Subtype == PdfName.Widget)
    annot_count  = len(annots) - widget_count
    return annot_count, widget_count

# Example batch run
input_dir = "test"
sizes = []

print("File statistics:")
for fname in sorted(os.listdir(input_dir)):
    if not fname.lower().endswith(".pdf"):
        continue
    full_path = os.path.join(input_dir, fname)

    # 1) Get annotation/widget counts
    a_count, w_count = count_objects_pdfrw(full_path)
    # 2) Get file size
    size_bytes = os.path.getsize(full_path)
    sizes.append(size_bytes)
    size_hr = human_readable_size(size_bytes)

    print(f"{fname}: {a_count} annotations, {w_count} widgets, {size_hr}")

# Compute summary stats
if sizes:
    min_size = min(sizes)
    max_size = max(sizes)
    avg_size = sum(sizes) / len(sizes)

    print("\nSummary of file sizes:")
    print(f"  Smallest file: {human_readable_size(min_size)}")
    print(f"  Largest file : {human_readable_size(max_size)}")
    print(f"  Average size : {human_readable_size(avg_size)}")
else:
    print("No PDF files found in the directory.")
