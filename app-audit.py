#!/usr/bin/env python3
"""Scan one or more module directories (default: audittest.4gm) and produce pandas
DataFrames containing filesystem statistics for all files under those directories.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys

VERBOSE = False

def vlog(*args, **kwargs):
    "Verbose print to stderr when VERBOSE is enabled."
    if VERBOSE:
        print(*args, file=sys.stderr, **kwargs)

def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat()

def gather_stats(root: Path):
    root = root.resolve()
    rows = []
    for p in root.rglob('*'):
        try:
            if not p.is_file():
                continue
            st = p.stat()
        except (OSError, PermissionError) as e:
            # skip unreadable entries
            vlog(f"skipping unreadable entry: {p} ({e})")
            continue
        rows.append({
            "abs_path": str(p),
            "rel_path": str(p.relative_to(root)),
            "parent": str(p.parent.relative_to(root)),
            "name": p.name,
            "suffix": p.suffix,
            "size_bytes": st.st_size,
            "mtime": iso(st.st_mtime),
            "ctime": iso(st.st_ctime),
            "atime": iso(st.st_atime),
            "mode_octal": oct(st.st_mode & 0o777),
            "uid": st.st_uid,
            "gid": st.st_gid,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["parent", "name"]).reset_index(drop=True)
    return df

def main(argv=None):
    p = argparse.ArgumentParser(description="Create a DataFrame of filesystem stats for one or more module directories.")
    p.add_argument("roots", nargs="*", help="module directories to scan (default: audittest.4gm)")
    p.add_argument("-o", "--out", help="optional output filename; use .parquet or .pq to write Parquet (falls back to CSV on error)")
    p.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    args = p.parse_args(argv)

    global VERBOSE
    VERBOSE = bool(args.verbose)

    roots = args.roots or ["audittest.4gm"]
    all_dfs = []
    total_files = 0

    for root_str in roots:
        root = Path(root_str)
        if not root.exists() or not root.is_dir():
            print("ERROR: root directory not found or not a directory:", root, file=sys.stderr)
            continue

        df = gather_stats(root)
        count = len(df)
        total_files += count
        if count:
            df['module'] = root.name
        all_dfs.append(df)

        print(f"scanned: {root}")
        print(f"files found: {count}")
        if count:
            pd.set_option("display.max_rows", 10)
            print(df.head(20).to_string(index=False))

    if not all_dfs:
        print("No valid modules scanned.", file=sys.stderr)
        sys.exit(2)

    if args.out:
        out_path = Path(args.out)
        combined = pd.concat(all_dfs, ignore_index=True)
        suffix = out_path.suffix.lower()
        if suffix in ('.parquet', '.pq'):
            # attempt parquet write; if engine missing, fall back to CSV
            try:
                combined.to_parquet(str(out_path), index=False)
                print("wrote:", out_path)
            except Exception as e:
                print("ERROR writing Parquet:", e, file=sys.stderr)
                print("Parquet engine not available or write failed; falling back to CSV.", file=sys.stderr)
                csv_path = out_path.with_suffix('.csv')
                combined.to_csv(str(csv_path), index=False)
                print("wrote:", csv_path)
        else:
            combined.to_csv(str(out_path), index=False)
            print("wrote:", out_path)

    print("total files across modules:", total_files)

if __name__ == "__main__":
    main()
