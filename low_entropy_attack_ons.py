#!/usr/bin/env python3
import argparse
import csv
import hashlib
import re
from typing import Any, Dict, Iterable, List, Tuple, Set, Optional
import pandas as pd

# -----------------------------
# Normalization & hashing
# -----------------------------
def normalize(s: Any) -> str:
    """Match the ONS pipeline you used earlier: lowercase, strip, remove non-alphanumerics."""
    return re.sub(r"\W+", "", str(s or "").strip().lower())

def hash_fields(fields: Iterable[Any]) -> str:
    combined = "".join(normalize(f) for f in fields if f is not None)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()  # hex string

# -----------------------------
# Simple Soundex (English-ish)
# (ONS examples use Soundex on last/first)
# -----------------------------
def soundex_simple(name: Any) -> str:
    n = normalize(name)
    if not n:
        return ""
    first = n[0].upper()
    mapping = {
        "bfpv": "1", "cgjkqsxz": "2", "dt": "3",
        "l": "4", "mn": "5", "r": "6"
    }
    code = first
    last_digit = ""
    for ch in n[1:]:
        digit = ""
        for k, v in mapping.items():
            if ch in k:
                digit = v
                break
        # skip vowels/h/w/y and duplicates
        if digit and digit != last_digit:
            code += digit
            last_digit = digit
        elif digit == "":
            last_digit = ""
    return (code + "000")[:4]

# -----------------------------
# Helpers to extract "top-k" empirical distributions
# -----------------------------
def top_values(series: pd.Series, k: int) -> List[str]:
    return series.dropna().astype(str).str.strip().str.lower().value_counts().head(k).index.tolist()

def first_initials_from(series: pd.Series, k: int) -> List[str]:
    vals = top_values(series, k)
    inits = [normalize(v)[:1] for v in vals if normalize(v)]
    # uniques in popularity order
    seen, out = set(), []
    for i in inits:
        if i and i not in seen:
            seen.add(i)
            out.append(i)
    return out

def first3_from(series: pd.Series, k: int) -> List[str]:
    vals = top_values(series, k)
    f3s = [normalize(v)[:3] for v in vals if normalize(v)]
    seen, out = set(), []
    for t in f3s:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

def initials_from_last(series: pd.Series, k: int) -> List[str]:
    vals = top_values(series, k)
    inits = [normalize(v)[:1] for v in vals if normalize(v)]
    seen, out = set(), []
    for t in inits:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

def zip3_list(series: pd.Series, k: int) -> List[str]:
    z = (series.dropna().astype(str)
         .str.replace(r"\D", "", regex=True)
         .str[:3]
         .replace("", pd.NA)
         .dropna())
    vals = z.value_counts().head(k).index.tolist()
    # keep only 3-digit items
    return [v for v in vals if len(v) == 3]

def dob_list(series: pd.Series, k: int) -> List[str]:
    # Expect YYYY-MM-DD or YYYYMMDD etc. We'll just keep digits and take 8 chars when possible.
    s = (series.dropna().astype(str)
         .str.replace(r"\D", "", regex=True)
         .str[:8]
         .replace("", pd.NA).dropna())
    # keep only plausible YYYYMMDD (8 digits)
    s = s[s.str.len() == 8]
    return s.value_counts().head(k).index.tolist()

def yob_list(series: pd.Series, k: int) -> List[str]:
    s = (series.dropna().astype(str)
         .str.replace(r"\D", "", regex=True)
         .str[:4]
         .replace("", pd.NA).dropna())
    s = s[s.str.len() == 4]
    return s.value_counts().head(k).index.tolist()

# -----------------------------
# Guesser per MK (returns dict: hash_hex -> tuple(plaintext parts))
# -----------------------------
def guesses_mk1(first_names, last_names, dobs):
    for fn in first_names:
        for ln in last_names:
            for dob in dobs:
                yield hash_fields([fn, ln, dob]), (fn, ln, dob)

def guesses_mk2(first_initials, last_names, dobs):
    for fi in first_initials:
        for ln in last_names:
            for dob in dobs:
                yield hash_fields([fi, ln, dob]), (fi, ln, dob)

def guesses_mk3(first_names, zips, dobs):
    for fn in first_names:
        for zp in zips:
            for dob in dobs:
                yield hash_fields([fn, zp, dob]), (fn, zp, dob)

def guesses_mk4(last_names, dobs):
    for ln in last_names:
        sdx = soundex_simple(ln)
        if not sdx:
            continue
        for dob in dobs:
            yield hash_fields([sdx, dob]), (ln, dob)  # store original ln for reporting

def guesses_mk5(first3s, last_names, yobs):
    for f3 in first3s:
        for ln in last_names:
            for yob in yobs:
                yield hash_fields([f3, ln, yob]), (f3, ln, yob)

def guesses_mk6(first_names, last_names, dobs):
    for fn in first_names:
        for ln in last_names:
            sdx = soundex_simple(ln)
            if not sdx:
                continue
            for dob in dobs:
                yield hash_fields([fn, sdx, dob]), (fn, ln, dob)

def guesses_mk7(first_initials, last_names, dobs):
    for fi in first_initials:
        for ln in last_names:
            sdx = soundex_simple(ln)
            if not sdx:
                continue
            for dob in dobs:
                yield hash_fields([fi, sdx, dob]), (fi, ln, dob)

def guesses_mk8(first_names, last_names, dobs):
    for fn in first_names:
        for ln in last_names:
            for dob in dobs:
                yield hash_fields([fn, ln, dob[:7]]), (fn, ln, dob[:7])

def guesses_mk9(first_initials, last_initials, yobs):
    for fi in first_initials:
        for li in last_initials:
            for yob in yobs:
                yield hash_fields([fi, li, yob]), (fi, li, yob)

def guesses_mk10(last_names, zips, yobs):
    for ln in last_names:
        for zp in zips:
            for yob in yobs:
                yield hash_fields([ln, zp, yob]), (ln, zp, yob)

def guesses_mk11(first_names, yobs, zip3s):
    for fn in first_names:
        for yob in yobs:
            for zp3 in zip3s:
                yield hash_fields([fn, yob, zp3]), (fn, yob, zp3)

def guesses_mk12(first_names, last_names, dobs):
    for fn in first_names:
        sdx_fn = soundex_simple(fn)
        if not sdx_fn:
            continue
        for ln in last_names:
            for dob in dobs:
                yield hash_fields([sdx_fn, ln, dob]), (fn, ln, dob)

def guesses_mk13(last_names, yobs, zip3s):
    for ln in last_names:
        for yob in yobs:
            for zp3 in zip3s:
                yield hash_fields([ln, yob, zp3]), (ln, yob, zp3)

# Map mk name -> generator builder
GENS = {
    "mk1": guesses_mk1,
    "mk2": guesses_mk2,
    "mk3": guesses_mk3,
    "mk4": guesses_mk4,
    "mk5": guesses_mk5,
    "mk6": guesses_mk6,
    "mk7": guesses_mk7,
    "mk8": guesses_mk8,
    "mk9": guesses_mk9,
    "mk10": guesses_mk10,
    "mk11": guesses_mk11,
    "mk12": guesses_mk12,
    "mk13": guesses_mk13,
    # allow ONS_MKx aliases
    "ons_mk1": guesses_mk1,
    "ons_mk2": guesses_mk2,
    "ons_mk3": guesses_mk3,
    "ons_mk4": guesses_mk4,
    "ons_mk5": guesses_mk5,
    "ons_mk6": guesses_mk6,
    "ons_mk7": guesses_mk7,
    "ons_mk8": guesses_mk8,
    "ons_mk9": guesses_mk9,
    "ons_mk10": guesses_mk10,
    "ons_mk11": guesses_mk11,
    "ons_mk12": guesses_mk12,
    "ons_mk13": guesses_mk13,
}

# Pretty labels for console
LABELS = {
    "mk1":  "first + last + dob",
    "mk2":  "first_initial + last + dob",
    "mk3":  "first + zip + dob",
    "mk4":  "soundex(last) + dob",
    "mk5":  "first3 + last + yob",
    "mk6":  "first + soundex(last) + dob",
    "mk7":  "first_initial + soundex(last) + dob",
    "mk8":  "first + last + dob[:7]",
    "mk9":  "first_initial + last_initial + yob",
    "mk10": "last + zip + yob",
    "mk11": "first + yob + zip[:3]",
    "mk12": "soundex(first) + last + dob",
    "mk13": "last + yob + zip[:3]",
}

def find_mk_columns(df: pd.DataFrame) -> List[str]:
    cols = []
    for c in df.columns:
        cl = c.lower()
        if cl.startswith("mk") or cl.startswith("ons_mk"):
            cols.append(c)
    return cols

def normalize_colnames(cols: List[str]) -> Dict[str, str]:
    """Return mapping original->normalized key (mk1..mk13) if possible; else keep original."""
    out = {}
    for c in cols:
        lc = c.lower()
        if lc.startswith("ons_mk"):
            out[c] = lc  # e.g., ons_mk1
        elif lc.startswith("mk"):
            out[c] = lc  # e.g., mk1
        else:
            out[c] = lc
    return out

def main():
    ap = argparse.ArgumentParser(description="Low-entropy dictionary attack on ONS match-keys (MK1–MK13).")
    ap.add_argument("--encoded", required=True, help="CSV with hashed ONS matchkeys (columns mk1..mk13 or ONS_MK1..13)")
    ap.add_argument("--plain", default="", help="(Optional) CSV with plaintext-like data to derive top-k distributions")
    ap.add_argument("--out", required=True, help="Output text file for matches")
    ap.add_argument("--topk", type=int, default=25, help="Top-k values to consider per attribute (default: 25)")
    ap.add_argument("--print-matches", action="store_true", help="Print hash←values for each hit")
    args = ap.parse_args()

    # Load encoded (hashed) ONS keys
    df_enc = pd.read_csv(args.encoded)
    mk_cols = find_mk_columns(df_enc)
    if not mk_cols:
        raise SystemExit("No match-key columns (mk1..mk13 or ONS_MK*) found in encoded CSV.")

    colmap = normalize_colnames(mk_cols)

    # Load plaintext distribution if provided
    # Fallback: very small dummy lists if not provided (but strongly recommend providing --plain)
    if args.plain:
        df_plain = pd.read_csv(args.plain)
        # Extract distributions
        top_first = top_values(df_plain.get("first_name", pd.Series(dtype=str)), args.topk)
        top_last = top_values(df_plain.get("last_name", pd.Series(dtype=str)), args.topk)
        top_dobs = dob_list(df_plain.get("dob", pd.Series(dtype=str)), args.topk)
        top_yobs = yob_list(df_plain.get("year_of_birth", pd.Series(dtype=str)), args.topk)
        top_zips = top_values(df_plain.get("zip", pd.Series(dtype=str)), args.topk)
    else:
        print("Warning: No --plain CSV provided; using minimal hardcoded lists for guessing (not recommended).")
        # Minimal fallback if no --plain is provided: tiny lists (adjust as needed)
        """top_first = ["anna", "maria", "peter", "thomas", "michael"]
        top_last  = ["mueller", "meier", "schmidt", "schneider", "fischer"]
        top_dobs  = ["19700101", "19800101", "19900101", "19750715", "19851230"]
        top_yobs  = ["1970", "1980", "1990", "1975", "1985"]
        top_zips  = ["10115", "20095", "50667", "80331", "01067"]"""

    # Derived helpers
    top_first_initials = sorted({normalize(n)[:1] for n in top_first if normalize(n)})
    top_last_initials  = sorted({normalize(n)[:1] for n in top_last if normalize(n)})
    top_first3         = sorted({normalize(n)[:3] for n in top_first if normalize(n)})
    top_zip3           = sorted({re.sub(r"\D", "", z)[:3] for z in top_zips if re.sub(r"\D", "", z)})
    top_dob7           = sorted({d[:7] for d in top_dobs if len(d) >= 7})

    # Build a small attribute bag to pass into generators
    attrs = dict(
        first_names = top_first,
        last_names  = top_last,
        dobs        = top_dobs,
        yobs        = top_yobs,
        zips        = top_zips,
        first_initials = top_first_initials,
        last_initials  = top_last_initials,
        first3s        = top_first3,
        zip3s          = top_zip3,
        dob7s          = top_dob7,  # used internally by mk8 construction
    )

    # Collect matches
    results: Dict[str, List[Tuple[str, Tuple[Any, ...]]]] = {}

    # Helper to run one MK
    def run_one_mk(mk_original: str, mk_norm: str):
        enc_col = df_enc[mk_original].dropna().astype(str).str.lower().tolist()
        target_set: Set[str] = set(enc_col)

        gen = None
        key = mk_norm
        if key in ("mk1", "ons_mk1"):
            gen = guesses_mk1(attrs["first_names"], attrs["last_names"], attrs["dobs"])
        elif key in ("mk2", "ons_mk2"):
            gen = guesses_mk2(attrs["first_initials"], attrs["last_names"], attrs["dobs"])
        elif key in ("mk3", "ons_mk3"):
            gen = guesses_mk3(attrs["first_names"], attrs["zips"], attrs["dobs"])
        elif key in ("mk4", "ons_mk4"):
            gen = guesses_mk4(attrs["last_names"], attrs["dobs"])
        elif key in ("mk5", "ons_mk5"):
            gen = guesses_mk5(attrs["first3s"], attrs["last_names"], attrs["yobs"])
        elif key in ("mk6", "ons_mk6"):
            gen = guesses_mk6(attrs["first_names"], attrs["last_names"], attrs["dobs"])
        elif key in ("mk7", "ons_mk7"):
            gen = guesses_mk7(attrs["first_initials"], attrs["last_names"], attrs["dobs"])
        elif key in ("mk8", "ons_mk8"):
            # Construct mk8 via mk8 generator (we reuse dob[:7] inside the generator)
            gen = guesses_mk8(attrs["first_names"], attrs["last_names"], attrs["dobs"])
        elif key in ("mk9", "ons_mk9"):
            gen = guesses_mk9(attrs["first_initials"], attrs["last_initials"], attrs["yobs"])
        elif key in ("mk10", "ons_mk10"):
            gen = guesses_mk10(attrs["last_names"], attrs["zips"], attrs["yobs"])
        elif key in ("mk11", "ons_mk11"):
            gen = guesses_mk11(attrs["first_names"], attrs["yobs"], attrs["zip3s"])
        elif key in ("mk12", "ons_mk12"):
            gen = guesses_mk12(attrs["first_names"], attrs["last_names"], attrs["dobs"])
        elif key in ("mk13", "ons_mk13"):
            gen = guesses_mk13(attrs["last_names"], attrs["yobs"], attrs["zip3s"])

        if gen is None:
            return

        hits: List[Tuple[str, Tuple[Any, ...]]] = []
        for h, vals in gen:
            if h in target_set:
                hits.append((h, vals))

        results[mk_original] = hits

        # Console summary
        label_key = mk_norm if mk_norm in LABELS else mk_norm.replace("ons_", "")
        print(f"[{mk_original}] hits = {len(hits)}  • {LABELS.get(label_key, '')}")

        # Optional verbose print
        if args.print_matches and hits:
            print(f"Matched values for {mk_original} ({LABELS.get(label_key, mk_original)}):")
            for hash_val, values in hits:
                print(f"Hash: {hash_val}  \u2190  Values: {values}")

    # Run all present MK columns
    for c in mk_cols:
        run_one_mk(c, colmap[c])

    # Write results to file
    with open(args.out, "w", encoding="utf-8") as f:
        total = sum(len(v) for v in results.values())
        f.write(f"TOTAL MATCHES: {total}\n\n")
        for mk, hits in results.items():
            label_key = colmap[mk] if mk in colmap else mk
            label_key = label_key if label_key in LABELS else label_key.replace("ons_", "")
            f.write(f"[{mk}] {LABELS.get(label_key, mk)} — {len(hits)} hits\n")
            for h, vals in hits:
                f.write(f"Hash: {h}  <-  Values: {vals}\n")
            f.write("\n")

if __name__ == "__main__":
    main()
