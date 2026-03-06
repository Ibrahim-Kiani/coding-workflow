import os
from pathlib import Path
import argparse

# Define file extensions to include (set) and mapping to languages for fences
LANGS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css"
}

# Mapping of file extensions to Markdown fenced code block language hints
EXT_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".html": "html",
    ".css": "css"
}


def gather_files(folder, exclude_dirs=None):
    exclude_set = set(exclude_dirs) if exclude_dirs else set()
    exclude_set.add("venv")
    exclude_set.add(".venv")
    exclude_set.add(".github")

    matches = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in exclude_set]
        for file in files:
            if Path(file).suffix in LANGS:
                matches.append(os.path.join(root, file))

    return sorted(matches)


def write_concatenated(files, output_path):
    """Write a Markdown file with per-file headings and fenced code blocks.

    Each file is written as:
    ### filename.ext

    **Path:** `full/path/to/file.ext`

    ```<language>
    <file contents>
    ```
    
    ---
    """
    with open(output_path, "w", encoding="utf-8", errors="ignore") as out:
        for path in files:
            file_name = os.path.basename(path)
            ext = Path(path).suffix
            lang = EXT_LANG.get(ext, "")

            # Heading and path
            out.write(f"### {file_name}\n\n")
            out.write(f"**Path:** `{path}`\n\n")

            # Fenced code block with language hint when available
            fence = f"```{lang}" if lang else "```"
            out.write(f"{fence}\n")

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                out.write(content)
                if not content.endswith("\n"):
                    out.write("\n")

            out.write("```\n\n---\n\n")


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate source files into a single Markdown (.md) file with headings and fenced code blocks."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Folder path to scan (default: current folder)",
    )
    parser.add_argument(
        "--output",
        default="code.md",
        help="Output Markdown filename (written to the same directory as the .github folder)",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        default=[],
        help=(
            "Directories to exclude (can be given multiple times or comma-separated). "
            "'venv' is ignored by default."
        ),
    )
    args = parser.parse_args()

    exclude_set = set()
    for item in args.exclude:
        for part in item.split(","):
            part = part.strip()
            if part:
                exclude_set.add(part)

    files = gather_files(args.folder, exclude_dirs=exclude_set)
    if not files:
        print(
            f"No source files found in {args.folder!r} for extensions: {', '.join(sorted(LANGS))}"
        )
        return

    # Compute output path: same directory as .github folder (two levels up from script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    github_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(github_dir)
    output_path = os.path.join(root_dir, args.output)
    
    write_concatenated(files, output_path)
    print(f"Wrote {len(files)} files to {output_path}")


if __name__ == "__main__":
    main()
