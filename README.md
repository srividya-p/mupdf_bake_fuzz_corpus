# Mupdf bake fuzz corpus

A collection of PDFs with annotations and widgets to be used as a seed corpus for fuzzing the `pdf_bake_document` functionality in mupdf. 

The corpus is built from the following sources: 
1. https://corp.digitalcorpora.org/corpora/files/CC-MAIN-2021-31-PDF-UNTRUNCATED/zipfiles/0000-0999/ (0000 - 00055)
2. https://github.com/openpreserve/format-corpus
3. https://github.com/mozilla/pdf.js/tree/master/test
4. https://github.com/0xabu/pdfannots 

PyMuPDF's `page.annots()` and `page.widgets()` functions are used to distingush PDFs which have annotations and widgets.

The full (old) corpus has the following distribution:

```bash
$ python3 sum.py seed_corpus_old
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
Size distribution (dynamic quartiles):
───────────────────────────────────────────
  ≤79.0KB        : 146
  79.0KB–160.7KB : 147
  160.7KB–314.8KB: 147
  >314.8KB       : 146

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
Each of these yield around ~100-200 execs/s. 

# Psyche! Generated PDFs >> corpora

The generated PDFs (present in the final `bake_fuzzer_seed_corpus` folder) are much smaller in size and therefore yield upto 600 execs/s.  Half of them are generated using `gen1.py` and the other half with `gen2.py`.

**Generator 1**
1. Multi-page (1–5) documents
2. Randomized object graph: content streams, annotation dictionaries, dummy objects, object ordering
3. Variable PDF version, trailer fields, and cross-reference tweaks
4. Varied structure beyond just annotations

**Generator 2**
1. Single-page PDFs
2. Chooses a random subset (5–26) of 26 distinct annotation subtypes, shuffles their order
3. Simpler object model: no dummy objects or version variations
4. Focused variation in annotation kinds and ordering

The final corpus has the following distribution:

```bash
$ python3 sum.py bake_fuzzer_seed_corpus
═══════════════════════════════════════════  ═══════════════════════════════════════════
 PDF classification summary:                  File size summary:
───────────────────────────────────────────  ───────────────────────────────────────────
PDF count                       : 200        Smallest file                : 715.0B      
Only annotations                : 55         Largest  file                : 6.1KB
Only widgets                    : 6          Average size                 : 2.9KB
Both annots+widgets             : 138
Neither annotations nor widgets : 1
═══════════════════════════════════════════  ═══════════════════════════════════════════
 Size distribution (dynamic quartiles):       Total objects across all PDFs:
───────────────────────────────────────────  ───────────────────────────────────────────
  ≤2.0KB                        : 50         Total annotations            : 1946       
  2.0KB–3.0KB                   : 50         Total widgets                : 260      
  3.0KB–3.9KB                   : 50
  >3.9KB                        : 50
═══════════════════════════════════════════  ═══════════════════════════════════════════
```

For a 10 minute run, this corpus also provides a coverage of 67.4% (LOC 783/1161) which is still reasonably high.
