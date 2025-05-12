# Mupdf bake fuzz corpus

A collection of PDFs with annotations and widgets to be used as a seed corpus for fuzzing the `pdf_bake_document` functionality in mupdf. 

The corpus is built from the following sources: 
1. https://corp.digitalcorpora.org/corpora/files/CC-MAIN-2021-31-PDF-UNTRUNCATED/zipfiles/0000-0999/ (0000 - 00055)
2. https://github.com/openpreserve/format-corpus
3. https://github.com/mozilla/pdf.js/tree/master/test
4. https://github.com/0xabu/pdfannots 

PyMuPDF's `page.annots()` and `page.widgets()` functions are used to distingush PDFs which have annotations and widgets.

The full corpus has the following distribution:

```bash
$ python3 sum.py
═══════════════════════════════════════════
PDF classification summary:
───────────────────────────────────────────
PDF count                       : 586
Only annotations                : 68
Only widgets                    : 491
Both annots+widgets             : 27
Neither annotations nor widgets : 0

═══════════════════════════════════════════
File size summary:
───────────────────────────────────────────
  Smallest file: 969.0B
  Largest  file: 1013.2KB
  Average size : 236.4KB

═══════════════════════════════════════════
Size distribution:
───────────────────────────────────────────
  <10KB     : 56
  10-50KB   : 67
  50-200KB  : 219
  200-500KB : 162
  >500KB    : 82

═══════════════════════════════════════════
Total objects across all PDFs:
───────────────────────────────────────────
  Total annotations = 315
  Total widgets     = 7328
```

For the actual fuzzing a pruned version of the corpus is used since the large file sizes slow down the execs/s by a lot. The upper limit on the file sizes are decided by looking at the coverage achieved by the seed for a 10 minute run of the fuzzer. 

```bash
mkdir -p bake_fuzzer_seed_corpus
find seed_corpus_full -maxdepth 1 -type f -name '*.pdf' -size -200k -exec cp -t bake_fuzzer_seed_corpus {} +
```

In addition to the final seeds folder, this repo contains some 
1. quick and dirty scripts used to build the seed corpus
2. scripts for generating PDFs with annotations and widgets (from scratch and from existing PDFs)
3. scripts for coverage extraction from an oss-fuzz coverage report for two levels of functions called by `pdf_bake_document` 

## Coverage extraction results

For a 10 minute run of the bake_fuzzer the different size limits set on the full corpus yielded the following results:
- <500KB = 69.9% (811/1161 LOC)
- <200KB = 70.2% (815/1161 LOC)
- <150KB = 67.5% (784/1161 LOC)
- <100KB = 67.1% (783/1161 LOC)
