import os
from pathlib import Path
import argparse

try:
    import tiktoken
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None

ENCODER = tiktoken.get_encoding("o200k_base") if tiktoken else None

# Define file extensions and their comment styles
LANGS = {
    ".py": {"single": "#", "multi_start": '"""', "multi_end": '"""'},
    ".js": {"single": "//", "multi_start": "/*", "multi_end": "*/"},
    ".ts": {"single": "//", "multi_start": "/*", "multi_end": "*/"},
    ".jsx": {"single": "//", "multi_start": "/*", "multi_end": "*/"},
    ".tsx": {"single": "//", "multi_start": "/*", "multi_end": "*/"},
    ".html": {"single": None, "multi_start": "<!--", "multi_end": "-->"},
    ".css": {"single": None, "multi_start": "/*", "multi_end": "*/"},
}

def count_lines(file_path, lang, encoder):
    code = comment = blank = 0
    multi_comment = False
    comment_start = lang.get("multi_start")
    comment_end = lang.get("multi_end")
    single_comment = lang.get("single")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        tokens = len(encoder.encode(content))
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                blank += 1
                continue

            if multi_comment:
                comment += 1
                if comment_end and comment_end in stripped:
                    multi_comment = False
                continue

            if comment_start and stripped.startswith(comment_start):
                comment += 1
                if comment_end and not stripped.endswith(comment_end):
                    multi_comment = True
                continue

            if single_comment and stripped.startswith(single_comment):
                comment += 1
                continue

            # Otherwise it's code
            code += 1

    return code, comment, blank, tokens


def scan_folder(folder, absolute=False, max_path_width=60, exclude_dirs=None):
    """Scan a folder and print a neatly formatted table.

    - Shows relative paths by default (use --absolute to show absolute paths).
    - Truncates long paths with a leading ellipsis to keep columns aligned.
    - Skips directories listed in exclude_dirs (default: 'venv').
    """
    total_code = total_comment = total_blank = total_tokens = 0
    results = []
    lang_totals = {ext: [0, 0, 0, 0] for ext in LANGS}
    exclude_set = set(exclude_dirs) if exclude_dirs else set()
    # Always ignore virtual environment folders by default
    exclude_set.add("venv")
    exclude_set.add(".github")
    for root, dirs, files in os.walk(folder):
        # Filter out excluded directories so we don't descend into them
        dirs[:] = [d for d in dirs if d not in exclude_set]
        for file in files:
            ext = Path(file).suffix
            if ext in LANGS:
                path = os.path.join(root, file)
                code, comment, blank, tokens = count_lines(path, LANGS[ext], ENCODER)
                results.append((path, code, comment, blank, tokens))
                lang_totals[ext][0] += code
                lang_totals[ext][1] += comment
                lang_totals[ext][2] += blank
                lang_totals[ext][3] += tokens
                total_code += code
                total_comment += comment
                total_blank += blank
                total_tokens += tokens

    if not results:
        print(f"No source files found in {folder!r} for extensions: {', '.join(LANGS.keys())}")
        return

    # Prepare display paths (relative by default) and truncate if too long
    def display_path(p):
        dp = p if absolute else os.path.relpath(p, folder)
        if len(dp) > max_path_width:
            return "..." + dp[-(max_path_width - 3):]
        return dp

    displayed = [display_path(p) for p, *_ in results]
    path_col_width = max(len("File"), max(len(p) for p in displayed))
    num_col_width = max(6, len(f"{max(total_code, total_comment, total_blank, total_tokens, 1):,}"))

    header = f"{ 'File':<{path_col_width}} { 'Code':>{num_col_width}} { 'Comment':>{num_col_width}} { 'Blank':>{num_col_width}} { 'Tokens':>{num_col_width}}"
    sep = "=" * len(header)

    print(header)
    print(sep)

    for (path, code, comment, blank, tokens), disp in zip(results, displayed):
        print(f"{disp:<{path_col_width}} {code:>{num_col_width},} {comment:>{num_col_width},} {blank:>{num_col_width},} {tokens:>{num_col_width},}")

    print(sep)
    print(f"{ 'TOTAL':<{path_col_width}} {total_code:>{num_col_width},} {total_comment:>{num_col_width},} {total_blank:>{num_col_width},} {total_tokens:>{num_col_width},}")

    # Per-language totals
    lang_header = f"{ 'Language':<10} { 'Code':>{num_col_width}} { 'Comment':>{num_col_width}} { 'Blank':>{num_col_width}} { 'Tokens':>{num_col_width}}"
    lang_sep = "-" * len(lang_header)
    print()
    print(lang_header)
    print(lang_sep)
    for ext, (code, comment, blank, tokens) in lang_totals.items():
        if code == 0 and comment == 0 and blank == 0 and tokens == 0:
            continue
        print(f"{ext:<10} {code:>{num_col_width},} {comment:>{num_col_width},} {blank:>{num_col_width},} {tokens:>{num_col_width},}")


if __name__ == "__main__":
    if ENCODER is None:
        print("tiktoken is not installed. Install it with: pip install tiktoken")
        raise SystemExit(1)
    
    # Compute default folder: two levels up from script (same directory as .github folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    github_dir = os.path.dirname(script_dir)
    default_folder = os.path.dirname(github_dir)
    
    parser = argparse.ArgumentParser(description="Count lines of code, comments, and blanks in multiple languages.")
    parser.add_argument("folder", nargs="?", default=default_folder, help="Folder path to scan (default: same directory as .github folder)")
    parser.add_argument("--absolute", action="store_true", help="Show absolute file paths instead of relative paths")
    parser.add_argument("--max-width", type=int, default=60, help="Maximum width for the file column (default: 60)")
    parser.add_argument("--exclude", "-e", action="append", default=[], help="Directories to exclude (can be given multiple times or comma-separated). 'venv' is ignored by default.")
    args = parser.parse_args()

    # Build exclude set from multiple --exclude args (and comma-separated values)
    exclude_set = set()
    for item in args.exclude:
        for part in item.split(","):
            part = part.strip()
            if part:
                exclude_set.add(part)

    scan_folder(args.folder, absolute=args.absolute, max_path_width=args.max_width, exclude_dirs=exclude_set)
