"""
This script is used to generate a call graph with regex upto 2 level for 
the pdf_bake_document function. It is run from the root of the mupdf repo.
"""

#!/usr/bin/env python3
import os
import re 
import sys

SRC_ROOT = "source"
HDR_ROOT = "include/mupdf"
OUT_FILE = "bake_funky.txt"

IGNORE_TOKENS = {
    "if",
    "for",
    "while",
    "switch",
    "return",
    "sizeof",
    "fz_always",
    "fz_catch",
    "fz_var",
    "assert",
    "fz_rethrow",
    "fz_throw",
    "fz_try",
}
MACRO_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

def get_signature(func_name, code):
    """
    From the file contents `code`, find the *definition* of `func_name`
    (i.e. the line ending in ') {'), capture only its argument list,
    and return a string like 'func_name(arg1, arg2, …)'.
    """
    sig_re = re.compile(
        rf'\b{re.escape(func_name)}\s*\(\s*([^)]*?)\s*\)\s*\{{',
        re.DOTALL
    )
    m = sig_re.search(code or "")
    if m:
        args = m.group(1).strip()
        return f"{func_name}({args})"
    return f"{func_name}("

def load_file_codes():
    """Return a dict mapping each .c/.h path under SRC_ROOT to its file contents."""
    files = {}
    for root, _, names in os.walk(SRC_ROOT):
        for fn in names:
            if fn.endswith((".c", ".h")):
                path = os.path.join(root, fn)
                try:
                    files[path] = open(path, "r", errors="ignore").read()
                except IOError:
                    pass
    for root, _, names in os.walk(HDR_ROOT):
        for fn in names:
            if fn.endswith(".h"):
                path = os.path.join(root, fn)
                try:
                    files[path] = open(path, "r", errors="ignore").read()
                except IOError:
                    pass
    return files


def extract_body(code, func_name):
    """Extract the entire definition of func_name, including its braces."""
    pat = re.compile(
        r"\b[\w\s\*]+\b" + re.escape(func_name) + r"\s*\([^)]*\)\s*\{", re.M
    )
    m = pat.search(code)
    if not m:
        return ""
    i = m.end()
    depth = 1
    while i < len(code) and depth:
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        i += 1
    return code[m.start() : i]


def find_calls(txt):
    """
    Return a set of all function names called in the given text,
    ignoring comments, string literals, keywords, macros, the entry point,
    methods (->), and so on.
    """
    txt = re.sub(r'/\*.*?\*/', '', txt, flags=re.DOTALL)
    txt = re.sub(r'//.*?$', '', txt, flags=re.MULTILINE)
    txt = re.sub(r'"([^"\\]|\\.)*"', '', txt)

    calls = set()
    for m in re.finditer(r'\b([a-zA-Z_]\w*)\s*\(', txt):
        name = m.group(1)
        if m.start() >= 2 and txt[m.start()-2:m.start()] == '->':
            continue
        if name in IGNORE_TOKENS or MACRO_RE.match(name):
            continue
        calls.add(name)

    return calls


def find_definition(func, file_codes):
    """
    Scan each file in file_codes for a definition of func.
    Return the first path where extract_body is non-empty.
    """
    for path, code in file_codes.items():
        if extract_body(code, func):
            return path
    return None


def main():
    file_codes = load_file_codes()
    all_code = "\n".join(file_codes.values())

    # Level 1
    body = extract_body(all_code, "pdf_bake_document")
    level1 = find_calls(body)
    level1.discard("pdf_bake_document")
    if not level1:
        print("Couldn't find pdf_bake_document or it has no calls.", file=sys.stderr)
        sys.exit(1)
        
    funcs = set()  # set of "source_path,function"

    print("=== Level 1 calls from pdf_bake_document ===")
    for fn in sorted(level1):
        path = find_definition(fn, file_codes) or "<unknown>"
        print(f"  [L1] {fn:<30s} (defined in {path})")
        sig = get_signature(fn, file_codes.get(path))
        funcs.add(f"{path},{sig}")

    # Level 2
    print("\n=== Level 2 calls (functions called by each Level 1) ===")
    for fn in sorted(level1):
        print(f"\n-- {fn} (Level 1) calls:")
        def_path = find_definition(fn, file_codes)
        src = file_codes.get(def_path, all_code)
        calls = find_calls(extract_body(src, fn))
        calls.discard(fn)
        if calls:
            for c in sorted(calls):
                cpath = find_definition(c, file_codes) or "<unknown>"
                print(f"    [L2] {c:<28s} (defined in {cpath})")
                sig = get_signature(c, file_codes.get(cpath))
                funcs.add(f"{cpath},{sig}")
        else:
            print("    (no calls found or not in this codebase)")
    
    with open(OUT_FILE, "w") as out:
        for fn in funcs:
            out.write(f"{fn}\n")
    print(f"\n→ Wrote {len(funcs)} unique entries to {OUT_FILE}")

if __name__ == "__main__":
    main()
