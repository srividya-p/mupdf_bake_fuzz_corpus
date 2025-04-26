# Mupdf bake fuzz corpus

A collection of PDFs with annotations and widgets to be used as a seed corpus for fuzzing the `pdf_bake_document` functionality in mupdf. 

The corpus is built from the following sources: 
1. https://corp.digitalcorpora.org/corpora/files/CC-MAIN-2021-31-PDF-UNTRUNCATED/zipfiles/0000-0999/ (0000 - 00055)
2. https://github.com/openpreserve/format-corpus
3. https://github.com/mozilla/pdf.js/tree/master/test
4. https://github.com/0xabu/pdfannots 

A simple filter (fast if not perfect) is used to distingush PDFs which have annotations and widgets:

```bash
grep -l -e "/Annots" -e "/Widget" .
```

And the size of individual PDFs is capped at 1MB:

```bash
find . -size -2M -type f -exec du -h {} + | sort -hr
```

It is very easy to find PDFs with annotations, but the ones with widgets occur in lower numbers in the sources. The final corpus has an equal distribution of both:

```bash
$ scripts/sum.sh bake_fuzzer_seed_corpus
Counting PDFs in bake_fuzzer_seed_corpus...

Summary:
---------
Total PDFs                        : 1008
PDFs with both /Annots and /Widget: 472
PDFs with only /Annots            : 500
PDFs with only /Widget            : 36
Maximum PDF size                  : 1,0M
```

Other than the final zip file to be used as a corpus, this repo contains some not fully automated, quick and dirty scripts used to build the seed corpus. 
