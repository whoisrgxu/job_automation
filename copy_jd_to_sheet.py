#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
import sys
from pathlib import Path
import math
import pandas as pd

ILLEGAL_CHARS = r'[\/\\\:\*\?\"\<\>\|]'  # Windows/Unix unsafe

def sanitize(name: str) -> str:
    if name is None or (isinstance(name, float) and math.isnan(name)):
        return ""
    s = str(name).strip()
    s = re.sub(ILLEGAL_CHARS, " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def first_newline_tail(text: str) -> str:
    if text is None:
        return ""
    parts = str(text).split("\n", 1)
    return parts[1] if len(parts) == 2 else ""

def read_text_file(fp: Path) -> str:
    return fp.read_text(encoding="utf-8", errors="ignore")

def case_insensitive_child(parent: Path, target: str) -> Path | None:
    if not target:
        return None
    if not parent.exists() or not parent.is_dir():
        return None
    tgt = target.lower()
    for child in parent.iterdir():
        if child.name.lower() == tgt:
            return child
    return None

def find_job_desc(base: Path, company: str, title: str) -> Path | None:
    comp = sanitize(company)
    titl = sanitize(title)
    if not comp or not titl:
        return None

    p_company = base / comp
    p_title = p_company / titl
    jd = p_title / "job_description.txt"
    if jd.exists():
        return jd

    p_company_ci = case_insensitive_child(base, comp)
    if not p_company_ci:
        return None
    p_title_ci = case_insensitive_child(p_company_ci, titl)
    if not p_title_ci:
        return None
    jd_ci = p_title_ci / "job_description.txt"
    return jd_ci if jd_ci.exists() else None

def main():
    ap = argparse.ArgumentParser(description="Populate Excel column with JD tails.")
    ap.add_argument("--excel", required=True)
    ap.add_argument("--sheet", default=0)
    ap.add_argument("--base", default="FullTime-Resume")
    ap.add_argument("--company-col", default="Company")
    ap.add_argument("--title-col", default="Title")
    ap.add_argument("--jd-col", default="Job Description")
    ap.add_argument("--status-col", default="JD Status")
    ap.add_argument("--out")
    args = ap.parse_args()

    excel_path = Path(args.excel)
    base_dir = Path(args.base)
    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet

    df = pd.read_excel(excel_path, sheet_name=sheet)

    # Validate source columns
    for col in [args.company_col, args.title_col]:
        if col not in df.columns:
            sys.exit(f"ERROR: Column '{col}' not found in sheet.")

    # Ensure output columns exist and are text-friendly
    if args.jd_col not in df.columns:
        df[args.jd_col] = ""
    if args.status_col and args.status_col not in df.columns:
        df[args.status_col] = ""

    # Force object dtype to accept long strings without warnings
    df[args.jd_col] = df[args.jd_col].astype("object")
    if args.status_col:
        df[args.status_col] = df[args.status_col].astype("object")

    # Process rows, skipping errors
    for idx, row in df.iterrows():
        try:
            company = row[args.company_col]
            title = row[args.title_col]

            jd_path = find_job_desc(base_dir, company, title)
            if jd_path:
                raw = read_text_file(jd_path)
                tail = first_newline_tail(raw)
                df.at[idx, args.jd_col] = str(tail)
                if args.status_col:
                    df.at[idx, args.status_col] = "OK"
            else:
                if args.status_col:
                    df.at[idx, args.status_col] = "MISSING_PATH"
        except Exception as e:
            # Log to status and continue
            if args.status_col:
                df.at[idx, args.status_col] = f"ERROR: {e}"

    out_path = Path(args.out) if args.out else excel_path.with_name(excel_path.stem + "_with_jd.xlsx")
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=str(sheet))
    print(f"Done. Wrote: {out_path}")

if __name__ == "__main__":
    main()
