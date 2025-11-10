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
import re
from git import Repo,InvalidGitRepositoryError

VERBOSE = False

def vlog(*args, **kwargs):
    "Verbose print to stderr when VERBOSE is enabled."
    if VERBOSE:
        print(*args, file=sys.stderr, **kwargs)

def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat()

def gather_stats(root: Path, no_git:bool=False):
    root = root.resolve()
    # Following block caches git-repo data - runs once for each supplied module (.4gm)
    git_repo = None
    if not no_git:
        try:
            git_repo = Repo(root, search_parent_directories=True)
            vlog(f"Repo for this root path: {git_repo}")
        except(InvalidGitRepositoryError) as inv:
            vlog(f"No repo found in parent directories, continuing on")

    all_local_mod_files = None
    if(git_repo != None):
        all_local_mod_files = [git_repo.working_tree_dir + "/" + diff.a_path for diff in git_repo.index.diff(None)]
        all_local_mod_files.extend([git_repo.working_tree_dir + "/" + diff.b_path for diff in git_repo.index.diff(None)])
        all_local_mod_files = set(all_local_mod_files)
        vlog(f"Repo shows {len(all_local_mod_files)} locally-modified files")

    all_staged_files = None
    if(git_repo != None):
        all_staged_files = [git_repo.working_tree_dir + "/" + diff.a_path for diff in git_repo.index.diff("HEAD")]
        all_staged_files.extend([git_repo.working_tree_dir + "/" + diff.b_path for diff in git_repo.index.diff("HEAD")])
        all_staged_files = set(all_staged_files)
        vlog(f"Repo shows {len(all_staged_files)} staged files with changes")

    all_tracked_files = None
    if(git_repo != None):
        all_tracked_files = [entry.abspath for entry in git_repo.commit().tree.traverse()]
        # This would almost work, and may be faster
        # all_tracked_files = git_repo.git.ls_files().split()
        vlog(f"Repo shows {len(all_tracked_files)} total files tracked in repo")

    rows = []
    for p in root.rglob('*'):
        # Following block only involves info in filesystem metadata (FAT)
        try:
            if not p.is_file():
                continue
            st = p.stat()
        except (OSError, PermissionError) as e:
            # skip unreadable entries
            vlog(f"skipping unreadable entry: {p} ({e})")
            continue

        # Following block involves info against cached git-repo data
        b_tracked = False
        if(git_repo and p.name in all_tracked_files):
            b_tracked = True

        b_local_mod = False
        if(git_repo and p.name in all_local_mod_files ):
            b_local_mod = True

        b_staged = False
        if(git_repo and p.name in all_staged_files ):
            b_staged = True

        # Define "plaintext files" by suffix
        plaintext_suffixes = {'.4gl', '.ext', '.org', '.sql', '.set', '.RDS',
            '.txt', '.md', '.csv', '.json', '.yaml', '.yml', '.ini', '.cfg',
            '.py', '.pl', '.sh', '.bash', '.ksh', '.c', '.h', '.cpp', '.hpp',
            '.js', '.ts', '.html', '.css', '.xml', '.bat', '.cmd', '.php'}

        # Following block involves a full content-parse (intensive)
        n_lines = 0
        n_comment_lines = 0
        n_blank_lines = 0
        n_function_defines= 0
        n_prepare_defines= 0
        n_execute_statements= 0
        n_run_statements= 0
        n_mz_statements= 0
        if p.suffix.lower() in plaintext_suffixes or p.name == "Makefile":
            try:
                with p.open("r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        n_lines += 1
                        if re.search(r'^\s*#.*', line, re.IGNORECASE):
                            # Considering Copyright-related lines as "blank", not "comment"
                            if (re.search(r'Copyright', line, re.IGNORECASE) or
                                re.search(r'All rights reserved', line, re.IGNORECASE) or
                                re.search(r'Use, modification', line, re.IGNORECASE) or
                                re.search(r'software is limit', line, re.IGNORECASE)):
                                n_blank_lines += 1
                            # Considering lines with just # as "blank"
                            elif re.search(r'^\s*#+$', line, re.IGNORECASE):
                                n_blank_lines += 1 #101
                            # All else of this match are (useful) comments
                            # This includes code with comments appended per
                            # European Cooperation for Space Standardization
                            # (ECSS)
                            else:
                                n_comment_lines += 1
                        # Considering empty or lines with just whitespace as "blank"
                        if re.search(r'^\w*$', line, re.IGNORECASE):
                            n_blank_lines += 1
                        # Code lines that have a comment appended at the end
                        if re.search(r'^[^#]+#+\s*\W.*$', line, re.IGNORECASE):
                            n_comment_lines += 1
                        # XXX   Refactor to categorize the kinds of statements
                        #       (auth, time-consuming, risk, etc.), and allow
                        #       them to be configurable
                        if re.search(r'.*function\s+\w+\(.*\)', line, re.IGNORECASE):
                            n_function_defines += 1
                        if re.search(r'.*prepare\s+\w+\s+from', line, re.IGNORECASE):
                            n_prepare_defines += 1
                        if re.search(r'.*execute\s+\w+\s+using', line, re.IGNORECASE):
                            n_execute_statements += 1
                        if re.search(r'.*run\s+', line, re.IGNORECASE):
                            n_run_statements += 1
                        if re.search(r'.*mz\s+', line, re.IGNORECASE):
                            n_mz_statements += 1
            except Exception as e:
                vlog(f"could not count lines in {p}: {e}")

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
            "num_lines": n_lines,
            "num_comment_lines": n_comment_lines,
            "num_blank_lines": n_blank_lines,
            "num_function_defines": n_function_defines,
            "num_prepare_defines": n_prepare_defines,
            "num_execute_statements": n_execute_statements,
            "num_run_statements": n_run_statements,
            "num_mz_statements": n_mz_statements,
            "b_tracked_in_scm_repo": b_tracked,
            "b_locally_modified": b_local_mod,
            "b_staged_for_commit": b_staged,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["parent", "name"]).reset_index(drop=True)
    return df

def main(argv=None):
    p = argparse.ArgumentParser(description="Create a DataFrame of stats for one or more module directories.")
    p.add_argument("roots", nargs="*", help="Module directories to scan (default: audittest.4gm)")
    p.add_argument("-o", "--out", help="Optional output filename; use .parquet or .pq to write Parquet (falls back to CSV on error)")
    p.add_argument("-i", "--nogit", action="store_true", help="Skip analysis steps that look for an SCM repo   in a parent-directory and relate it to found files. (default: not set - analysis will be attempted)")
    p.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    args = p.parse_args(argv)

    global VERBOSE
    VERBOSE = bool(args.verbose)

    roots = args.roots or ["audittest.4gm"]
    all_dfs = []
    total_files = 0

    whole = len(roots)
    part = 0
    for root_str in roots:
        part += 1
        root = Path(root_str)
        if not root.exists() or not root.is_dir():
            print("ERROR: root directory not found or not a directory:", root, file=sys.stderr)
            continue

        df = gather_stats(root, args.nogit)
        count = len(df)
        total_files += count
        if count:
            df['module'] = root.name
        all_dfs.append(df)

        print(f"scanned: {root}, {part} of {whole}")
        print(f"files found: {count}")
        print(f"Printing <=8 example rows:")
        if count:
            pd.set_option("display.max_rows", 10)
            print(df.head(8).to_string(index=False))

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
