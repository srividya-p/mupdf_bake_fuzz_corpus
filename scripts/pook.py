import os
import random
import shutil
import io
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfArray, PdfName
import logging

logging.getLogger("pdfrw").setLevel(logging.CRITICAL)

# === CONFIG ===
input_dir   = "bake_fuzzer_seed_corpus"
output_dir  = "test"
total_keep  = 400      # widgets + other annots
num_seeds   = 100
max_size_b  = 10 * 1024
NUM_OBJECTS = 5  # max number of objects in each seed

# Clean output
shutil.rmtree(output_dir, ignore_errors=True)
os.makedirs(output_dir, exist_ok=True)

# === PHASE 1: Build two balanced pools, storing the PdfDict itself ===

widget_pool = []  # (proxy, path, page_medabox, cropbox, PdfDict)
annot_pool  = []

for fn in os.listdir(input_dir):
    if not fn.lower().endswith(".pdf"):
        continue
    path = os.path.join(input_dir, fn)
    try:
        reader = PdfReader(path)
    except Exception:
        continue

    for page in reader.pages:
        annots = page.Annots or []
        for a in annots:
            proxy = len(repr(a))
            entry = (
                proxy,
                path,
                page.MediaBox,
                page.CropBox or page.MediaBox,
                a  # store the PdfDict for reuse
            )
            # classify
            if getattr(a, "Subtype", None) == PdfName.Widget:                
                widget_pool.append(entry)
            else:
                annot_pool.append(entry)

# sort by proxy size and trim to half each
widget_pool.sort(key=lambda e: e[0])
annot_pool .sort(key=lambda e: e[0])

for entry in widget_pool:
    pdfdict = entry[4]
    try:
        for key in ("/DA", "/MK", "/Border", "/AP", "/TU"):
            del pdfdict[key]
    except KeyError:
        pass

print(f"Pools: {len(widget_pool)} widgets, {len(annot_pool)} annots")

# for i in range(3000):
#     print(widget_pool[i])
#     print(f"{i} ##########################################################################")
#     print(annot_pool[i])
#     print()
    
# exit(1)

half = total_keep // 2
widget_pool = widget_pool[:half]
annot_pool  = annot_pool [:half]

print(f"Pools: {len(widget_pool)} widgets, {len(annot_pool)} annots")

# === PHASE 2: Generate seeds ===

def make_pdf_bytes(entries):
    """
    entries: list of tuples as in the pools,
    we ignore proxy and path here because we only need
    one MediaBox/CropBox (they should all be the same size
    before sampling mixed from different pages—this is simplest).
    """
    # Use the MediaBox/CropBox of the first entry
    _, _, media, crop, _ = entries[0]
    page = PdfDict(
        Type      = PdfName.Page,
        MediaBox  = media,
        CropBox   = crop,
        Resources = PdfDict(),
        Contents  = PdfArray(),
        Annots    = PdfArray([e[4] for e in entries])
    )
    pdf = PdfWriter()
    pdf.addpage(page)
    buf = io.BytesIO()
    pdf.write(buf)
    return buf.getvalue()

for i in range(1, num_seeds + 1):
    # pick 1–5 total
    n = random.randint(1, NUM_OBJECTS)
    w = n // 2
    a = n - w

    chosen = random.sample(widget_pool, w) + random.sample(annot_pool, a)
    random.shuffle(chosen)

    data = make_pdf_bytes(chosen)

    # if oversize, strip any stream data from each annot and retry
    if len(data) > max_size_b:
        for entry in chosen:
            annot = entry[4]
            if hasattr(annot, "stream"):
                annot.stream = b""
        data = make_pdf_bytes(chosen)

    out_name = f"seed_{i:03d}.pdf"
    with open(os.path.join(output_dir, out_name), "wb") as f:
        f.write(data)

print(f"✅ Generated {num_seeds} PDFs, each ≤10 KB, balanced widgets/annotations.")  
