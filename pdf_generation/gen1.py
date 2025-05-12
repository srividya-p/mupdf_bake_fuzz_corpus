#!/usr/bin/env python3
"""
This script generates 100 different PDF files whose structure is deliberately varied
in order to create a highly diverse seed corpus for a PDF library fuzzing harness.
The variations include:
  - A random number of pages (1 to 5) per PDF.
  - Randomized object order plus insertion of dummy objects.
  - Randomized annotation contents, coordinates, and sizes.
  - Additional dictionary keys in annotations (e.g., color and border).
  - Alternate PDF versions.
  - Variation in the cross-reference mechanism and trailer dictionaries.
  - Occasional small deviations (e.g. off-by-one values).
Each PDF is generated as a minimal document and is kept relatively small.
"""

import os
import random
import string

# --------------------------
# Helper functions
# --------------------------

def random_string(n=10):
    """Generate a random alphanumeric string of length n."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

def random_rect():
    """Generate a random rectangle [llx lly urx ury] ensuring llx < urx and lly < ury."""
    llx = round(random.uniform(0, 400), 2)
    lly = round(random.uniform(0, 600), 2)
    urx = round(random.uniform(llx + 1, 612), 2)
    ury = round(random.uniform(lly + 1, 792), 2)
    return f"[{llx} {lly} {urx} {ury}]"

def random_color():
    """Generate a random RGB array for PDF (each component between 0 and 1)."""
    r = round(random.uniform(0, 1), 2)
    g = round(random.uniform(0, 1), 2)
    b = round(random.uniform(0, 1), 2)
    return f"[{r} {g} {b}]"

def build_annotation(template):
    """
    Build an annotation by randomizing coordinates, text, and adding extra keys.
    The original template (which may include a placeholder rectangle) is modified.
    """
    rect = random_rect()
    contents = random_string(15)
    color = random_color()
    border = f"[{random.randint(0,3)} {random.randint(0,3)} {random.randint(1,10)}]"
    # If the template contains a placeholder rectangle, replace it; otherwise, inject one.
    if "[50 750 70 770]" in template:
        annot = template.replace("[50 750 70 770]", rect)
    else:
        annot = template.rstrip(" >>") + f" /Rect {rect}"
    # Append additional dictionary keys: /C for color, /Border, and override /Contents.
    annot = annot.rstrip(" >>") + f" /C {color} /Border {border} /Contents ({contents}) >>"
    return annot

# --------------------------
# Master annotation templates
# --------------------------
annotation_templates = [
    "<< /Type/Annot /Subtype /Text /Rect [50 750 70 770] /Contents (Text Annotation) >>",
    "<< /Type/Annot /Subtype /Link /Rect [50 750 70 770] /A << /S /URI /URI (http://example.com) >> /Contents (Link Annotation) >>",
    "<< /Type/Annot /Subtype /FreeText /Rect [50 750 70 770] /DA (/Helvetica 10 Tf 0 g) /Contents (FreeText Annotation) >>",
    "<< /Type/Annot /Subtype /Square /Rect [50 750 70 770] /Contents (Square Annotation) >>",
    # Additional widget annotation template added
    "<< /Type/Annot /Subtype /Widget /Rect [50 750 70 770] /Contents (Widget Annotation) >>",
]

# --------------------------
# Build PDF with all the introduced variations.
# --------------------------
def build_pdf():
    # Choose a random PDF version.
    pdf_version = random.choice(["1.4", "1.5", "1.7"])
    objects = []  # List of tuples: (object number, object content)
    
    # We'll assign fixed numbers to the Catalog and Pages objects.
    # Catalog (object 1) always points to Pages (object 2).
    catalog_obj = (1, "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(catalog_obj)

    pages_obj_num = 2  # reserved for the Pages object.
    current_obj = 3    # Next object number to assign.
    
    # Create a random number of pages (between 1 and 5).
    num_pages = random.randint(1, 5)
    page_obj_nums = []  # To remember which object numbers are pages.

    for p in range(num_pages):
        # --- Content Stream ---
        stream_text = random_string(20)
        stream_bytes = stream_text.encode("utf-8")
        stream_length = len(stream_bytes)
        # Possibly tweak the declared stream length by ±1.
        if random.random() < 0.2:
            deviation_val = random.choice([-1, 1])
            declared_length = stream_length + deviation_val
        else:
            declared_length = stream_length
        content_obj_num = current_obj
        content_obj = (current_obj,
                       f"{current_obj} 0 obj\n<< /Length {declared_length} >>\nstream\n{stream_text}\nendstream\nendobj\n")
        objects.append(content_obj)
        current_obj += 1

        # --- Annotations for this page ---
        n_annots = random.randint(1, 5)
        annot_obj_nums = []
        for i in range(n_annots):
            annot_template = random.choice(annotation_templates)
            annot = build_annotation(annot_template)
            annot_obj = (current_obj, f"{current_obj} 0 obj\n{annot}\nendobj\n")
            objects.append(annot_obj)
            annot_obj_nums.append(current_obj)
            current_obj += 1

        # --- Page Object ---
        annot_refs = " ".join(f"{num} 0 R" for num in annot_obj_nums)
        extra_key = ""
        if random.random() < 0.3:
            extra_key = f" /Modified ({random_string(8)})"
        page_obj = (current_obj,
                    f"{current_obj} 0 obj\n<< /Type /Page /Parent {pages_obj_num} 0 R "
                    f"/MediaBox [0 0 612 792] /Contents {content_obj_num} 0 R /Annots [{annot_refs}]{extra_key} >>\nendobj\n")
        objects.append(page_obj)
        page_obj_nums.append(current_obj)
        current_obj += 1

    # --- Pages Object ---
    kids_array = " ".join(f"{num} 0 R" for num in page_obj_nums)
    pages_obj = (pages_obj_num,
                 f"{pages_obj_num} 0 obj\n<< /Type /Pages /Count {num_pages} /Kids [{kids_array}] >>\nendobj\n")
    objects.append(pages_obj)

    # --- Dummy Objects ---
    dummy_count = random.randint(0, 5)
    for i in range(dummy_count):
        dummy_obj = (current_obj,
                     f"{current_obj} 0 obj\n<< /Type /Dummy /Data ({random_string(10)}) >>\nendobj\n")
        objects.append(dummy_obj)
        current_obj += 1

    total_objects = current_obj - 1  # Highest object number

    # --- Randomize object order ---
    # (Note: the cross-reference table does not care about file order, only object numbers and offsets.)
    random.shuffle(objects)

    # --- Build the PDF file ---
    header = f"%PDF-{pdf_version}\n%âãÏÓ\n"
    pdf_body = ""
    # We need to record the file offset of each object number.
    obj_offsets = {}
    current_offset = len(header.encode("utf-8"))
    for obj_num, content in objects:
        obj_offsets[obj_num] = current_offset
        pdf_body += content
        current_offset += len(content.encode("utf-8"))
    pdf_without_xref = header + pdf_body

    # --- Build cross-reference section ---
    # Create a xref table that lists objects sorted by their object number.
    xref_entries = []
    xref_entries.append("0000000000 65535 f \n")  # Object 0 entry
    for i in range(1, total_objects + 1):
        offset = obj_offsets.get(i, 0)
        xref_entries.append(f"{offset:010d} 00000 n \n")
    xref_table = "xref\n0 {}\n{}".format(total_objects + 1, "".join(xref_entries))

    # --- Build variable trailer dictionary ---
    trailer_dict = f"<< /Size {total_objects + 1} /Root 1 0 R"
    if random.random() < 0.5:
        trailer_dict += f" /Info ({random_string(12)})"
    if random.choice([True, False]):
        trailer_dict += f" /XRefStm {random.randint(100, 999)}"
    trailer_dict += " >>"
    trailer = f"trailer\n{trailer_dict}\n"

    # --- startxref and final EOF ---
    startxref_value = len(pdf_without_xref.encode("utf-8"))
    if random.random() < 0.3:
        startxref_value += random.choice([-1, 1])
    startxref = f"startxref\n{startxref_value}\n"
    eof = "%%EOF\n"

    pdf_complete = pdf_without_xref + xref_table + trailer + startxref + eof
    return pdf_complete.encode("utf-8")

# --------------------------
# Main: generate 100 PDFs
# --------------------------
def main():
    os.makedirs("pdf_outputs_1", exist_ok=True)
    for i in range(1, 51):
        pdf_data = build_pdf()
        filename = os.path.join("pdf_outputs_1", f"generated_1_{i}.pdf")
        with open(filename, "wb") as f:
            f.write(pdf_data)
        if len(pdf_data) >= 10 * 1024:
            print(f"Warning: {filename} size is {len(pdf_data)} bytes.")
    print("Generated 100 different PDF files in the 'pdf_outputs_1' directory.")

if __name__ == "__main__":
    main()
