#!/usr/bin/env python3
"""
This script generates 100 different PDF files that use a varying subset
(and ordering) of annotation types. The master list of annotations includes:
Text, Link, FreeText, Line, Square, Circle, Polygon, PolyLine, Highlight, Underline,
Squiggly, StrikeOut, Stamp, Caret, Ink, Popup, FileAttachment, Sound, Movie, Widget,
Screen, PrinterMark, TrapNet, Watermark, 3D, and Redact. For each generated PDF,
a random subset (minimum 5 annotations) in a random order is chosen.
Each PDF file is generated as a minimal one‑page document and is less than 10 KB.
"""

import os
import random

# Master list of annotation definitions (each is a minimal PDF dictionary)
annotation_objects = [
    # 1. Text
    "<< /Type/Annot /Subtype /Text /Rect [50 750 70 770] /Contents (Text Annotation) >>",
    # 2. Link
    "<< /Type/Annot /Subtype /Link /Rect [80 750 100 770] /A << /S /URI /URI (http://example.com) >> /Contents (Link Annotation) >>",
    # 3. FreeText
    "<< /Type/Annot /Subtype /FreeText /Rect [110 750 150 770] /Contents (FreeText Annotation) /DA (/Helvetica 10 Tf 0 g) >>",
    # 4. Line
    "<< /Type/Annot /Subtype /Line /Rect [160 750 200 770] /L [160 760 200 760] /Contents (Line Annotation) >>",
    # 5. Square
    "<< /Type/Annot /Subtype /Square /Rect [210 750 250 770] /BS << /W 1 >> /Contents (Square Annotation) >>",
    # 6. Circle
    "<< /Type/Annot /Subtype /Circle /Rect [260 750 300 770] /BS << /W 1 >> /Contents (Circle Annotation) >>",
    # 7. Polygon
    "<< /Type/Annot /Subtype /Polygon /Rect [310 750 350 770] /Vertices [310 760 330 780 350 760] /Contents (Polygon Annotation) >>",
    # 8. PolyLine
    "<< /Type/Annot /Subtype /PolyLine /Rect [360 750 400 770] /Vertices [360 760 380 780 400 760] /Contents (PolyLine Annotation) >>",
    # 9. Highlight
    "<< /Type/Annot /Subtype /Highlight /Rect [50 700 100 720] /QuadPoints [50 720 100 720 50 700 100 700] /Contents (Highlight Annotation) >>",
    # 10. Underline
    "<< /Type/Annot /Subtype /Underline /Rect [110 700 160 720] /QuadPoints [110 720 160 720 110 700 160 700] /Contents (Underline Annotation) >>",
    # 11. Squiggly
    "<< /Type/Annot /Subtype /Squiggly /Rect [170 700 220 720] /QuadPoints [170 720 220 720 170 700 220 700] /Contents (Squiggly Annotation) >>",
    # 12. StrikeOut
    "<< /Type/Annot /Subtype /StrikeOut /Rect [230 700 280 720] /QuadPoints [230 720 280 720 230 700 280 700] /Contents (StrikeOut Annotation) >>",
    # 13. Stamp
    "<< /Type/Annot /Subtype /Stamp /Rect [290 700 330 720] /Contents (Stamp Annotation) >>",
    # 14. Caret
    "<< /Type/Annot /Subtype /Caret /Rect [340 700 360 720] /Contents (Caret Annotation) >>",
    # 15. Ink
    "<< /Type/Annot /Subtype /Ink /Rect [50 650 100 670] /InkList [[50 660 75 665 100 660]] /Contents (Ink Annotation) >>",
    # 16. Popup
    "<< /Type/Annot /Subtype /Popup /Rect [110 650 150 670] /Contents (Popup Annotation) >>",
    # 17. FileAttachment
    "<< /Type/Annot /Subtype /FileAttachment /Rect [160 650 200 670] /FS << /Type /Filespec /F (attached.txt) >> /Contents (FileAttachment Annotation) >>",
    # 18. Sound
    "<< /Type/Annot /Subtype /Sound /Rect [210 650 250 670] /Sound << /R 8000 /E (raw) /Channels 1 >> /Contents (Sound Annotation) >>",
    # 19. Movie
    "<< /Type/Annot /Subtype /Movie /Rect [260 650 300 670] /Movie << /F (movie.mpg) >> /Contents (Movie Annotation) >>",
    # 20. Widget
    "<< /Type/Annot /Subtype /Widget /Rect [310 650 350 670] /Contents (Widget Annotation) >>",
    # 21. Screen
    "<< /Type/Annot /Subtype /Screen /Rect [360 650 400 670] /Contents (Screen Annotation) >>",
    # 22. PrinterMark
    "<< /Type/Annot /Subtype /PrinterMark /Rect [50 600 100 620] /Contents (PrinterMark Annotation) >>",
    # 23. TrapNet
    "<< /Type/Annot /Subtype /TrapNet /Rect [110 600 150 620] /Contents (TrapNet Annotation) >>",
    # 24. Watermark
    "<< /Type/Annot /Subtype /Watermark /Rect [160 600 200 620] /Contents (Watermark Annotation) >>",
    # 25. 3D
    "<< /Type/Annot /Subtype /3D /Rect [210 600 250 620] /Contents (3D Annotation) >>",
    # 26. Redact
    "<< /Type/Annot /Subtype /Redact /Rect [260 600 300 620] /Contents (Redact Annotation) >>"
]

def build_pdf(annotations):
    """
    Build a minimal one-page PDF with the provided list of annotation strings.
    Returns the complete PDF as a bytes object.
    """
    objects = []

    # Object 1: Catalog
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Object 2: Pages
    objects.append("2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n")

    # Create references for the annotation objects.
    annot_count = len(annotations)
    annot_refs = " ".join(f"{i} 0 R" for i in range(5, 5 + annot_count))

    # Object 3: Page object with /Annots array
    objects.append(f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Annots [{annot_refs}] >>\nendobj\n")

    # Object 4: A simple content stream (here the text is fixed; you could also vary it)
    content = "BT /F1 12 Tf 100 700 Td (File variation) Tj ET"
    content_length = len(content.encode("utf-8"))
    objects.append(f"4 0 obj\n<< /Length {content_length} >>\nstream\n{content}\nendstream\nendobj\n")

    # Objects for annotations (objects 5 to 4+annot_count)
    obj_num = 5
    for annot in annotations:
        objects.append(f"{obj_num} 0 obj\n{annot}\nendobj\n")
        obj_num += 1

    # Assemble PDF header and body
    header = "%PDF-1.4\n%âãÏÓ\n"
    pdf_body = "".join(objects)
    pdf_without_xref = header + pdf_body

    # Compute xref offsets for each object after the header.
    offsets = []
    current_offset = len(header.encode("utf-8"))
    for obj in objects:
        offsets.append(current_offset)
        current_offset += len(obj.encode("utf-8"))

    # Build xref table.
    xref_entries = ["0000000000 65535 f \n"]
    for off in offsets:
        xref_entries.append(f"{off:010d} 00000 n \n")
    xref_section = "xref\n0 %d\n%s" % (len(xref_entries), "".join(xref_entries))

    # Build the trailer.
    trailer = f"trailer\n<< /Size {len(xref_entries)} /Root 1 0 R >>\n"
    startxref = f"startxref\n{len(pdf_without_xref.encode('utf-8'))}\n"
    eof = "%%EOF\n"

    pdf_complete = pdf_without_xref + xref_section + trailer + startxref + eof
    return pdf_complete.encode("utf-8")

def main():
    os.makedirs("pdf_outputs_2", exist_ok=True)
    for i in range(1, 51):
        # For every PDF file, start with a copy of all annotations and shuffle it.
        annot_list = annotation_objects.copy()
        random.shuffle(annot_list)
        # Choose a random subset—here we take between 5 and 26 annotations.
        n = random.randint(5, len(annot_list))
        annot_subset = annot_list[:n]

        # Build the PDF from the randomly selected subset.
        pdf_data = build_pdf(annot_subset)
        filename = os.path.join("pdf_outputs_2", f"generated_2_{i}.pdf")
        with open(filename, "wb") as f:
            f.write(pdf_data)
        # Optional: a warning if the PDF ends up larger than 10 KB (which is unlikely here).
        if len(pdf_data) >= 10 * 1024:
            print(f"Warning: {filename} size is {len(pdf_data)} bytes.")
    print("Generated 100 different PDF files in the 'pdf_outputs_2' directory.")

if __name__ == "__main__":
    main()
