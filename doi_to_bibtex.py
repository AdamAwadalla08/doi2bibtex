"""
doi_to_bibtex — Convert DOI(s) to BibTeX entries

Usage examples:
  doi2bib 10.1038/nature12373
  doi2bib 10.1038/nature12373 10.1145/1327452.1327492
  doi2bib -txt my_dois.txt
  doi2bib 10.1038/nature12373 -c
  doi2bib 10.1038/nature12373 -copy
  doi2bib 10.1038/nature12373 -s output.bib
  doi2bib 10.1038/nature12373 -save output.bib
  doi2bib -txt dois.txt -c -s refs.bib

Flags:
  -txt <file>         Read DOIs from a text file
  -c,  -copy          Copy output to clipboard
  -s,  -save <file>   Save output to a .bib or .txt file
  -h,  --help         Show this help message
"""

import sys
import re
import time
import requests


# ── Core ──────────────────────────────────────────────────────────────────────


def clean_doi(doi_input: str) -> str:
    """Strip URL wrapper and return a bare DOI."""
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", doi_input.strip().rstrip(","))


def fetch_bibtex(doi: str, retries: int = 2) -> str:
    """Fetch a single BibTeX entry from doi.org content negotiation."""
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex"}

    for attempt in range(retries + 1):
        try:
            response = requests.get(
                url, headers=headers, allow_redirects=True, timeout=10
            )
            if response.status_code == 200:
                return response.text.strip()
            elif response.status_code == 404:
                raise ValueError(f"DOI not found: {doi}")
            else:
                raise ValueError(f"HTTP {response.status_code} for DOI: {doi}")
        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(1)
            else:
                raise ValueError(f"Request timed out for DOI: {doi}")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Connection error — are you online?")


def process_dois(dois: list[str], delay: float = 0.5) -> tuple[list[str], list[str]]:
    """
    Fetch BibTeX for a list of DOIs.
    Returns (results, errors) where results are BibTeX strings and errors are messages.
    """
    results = []
    errors = []

    for i, raw in enumerate(dois):
        doi = clean_doi(raw)
        if not doi:
            continue
        try:
            print(f"  [{i+1}/{len(dois)}] Fetching: {doi}", file=sys.stderr)
            bibtex = fetch_bibtex(doi)
            results.append(bibtex)
        except ValueError as e:
            errors.append(str(e))
            print(f"  ✗ {e}", file=sys.stderr)

        # Be polite to doi.org — small delay between requests
        if i < len(dois) - 1:
            time.sleep(delay)

    return results, errors


# ── Input sources ─────────────────────────────────────────────────────────────


def load_dois_from_file(path: str) -> list[str]:
    """Read DOIs from a text file (one per line, blank lines and # comments ignored)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    dois = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            # A line may contain multiple DOIs separated by commas or spaces
            for token in re.split(r"[\s,]+", stripped):
                if token:
                    dois.append(token)
    return dois


# ── Output helpers ────────────────────────────────────────────────────────────


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except ImportError:
        print(
            "Warning: 'pyperclip' not installed. Run: pip install pyperclip",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"Warning: clipboard copy failed — {e}", file=sys.stderr)
        return False


def save_to_file(text: str, path: str) -> None:
    """Append or create a .bib / .txt file with the BibTeX content."""
    mode = "a" if path.endswith(".bib") else "w"
    try:
        with open(path, mode, encoding="utf-8") as f:
            f.write(text + "\n")
        action = "Appended to" if mode == "a" else "Saved to"
        print(f"  ✓ {action}: {path}", file=sys.stderr)
    except IOError as e:
        print(f"Error saving file: {e}", file=sys.stderr)
        sys.exit(1)


# ── CLI ───────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str]) -> dict:
    """
    Minimal hand-rolled argument parser (no argparse dependency).
    Supports:
      -txt <file>       read DOIs from a text file
      -copy             copy output to clipboard
      -save <file>      save output to a file
      Positional args   treated as DOIs
    """
    args = {
        "dois": [],
        "txt_file": None,
        "copy": False,
        "save_file": None,
    }
    COPY_FLAGS = {"-copy", "-c"}
    SAVE_FLAGS = {"-save", "-s"}

    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "-txt":
            i += 1
            if i >= len(argv):
                print("Error: -txt requires a file path argument.", file=sys.stderr)
                sys.exit(1)
            args["txt_file"] = argv[i]
        elif token in COPY_FLAGS:
            args["copy"] = True
        elif token in SAVE_FLAGS:
            i += 1
            if i >= len(argv):
                print("Error: -save requires a file path argument.", file=sys.stderr)
                sys.exit(1)
            args["save_file"] = argv[i]
        else:
            # Positional — could be comma-separated: "doi1,doi2"
            for part in token.split(","):
                if part.strip():
                    args["dois"].append(part.strip())
        i += 1

    return args


def print_usage():
    print(__doc__)


def main():
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print_usage()
        sys.exit(0)

    args = parse_args(argv)

    # Collect all DOIs
    all_dois = list(args["dois"])
    if args["txt_file"]:
        all_dois += load_dois_from_file(args["txt_file"])

    if not all_dois:
        print("Error: no DOIs provided. Use -h for help.", file=sys.stderr)
        sys.exit(1)

    print(f"\nFetching {len(all_dois)} DOI(s)...\n", file=sys.stderr)
    results, errors = process_dois(all_dois)

    if not results:
        print("\nNo BibTeX entries were retrieved.", file=sys.stderr)
        sys.exit(1)

    combined = "\n\n".join(results)

    # Always print to stdout
    print("\n" + combined + "\n")

    # Optional: copy to clipboard
    if args["copy"]:
        if copy_to_clipboard(combined):
            print("  ✓ Copied to clipboard.", file=sys.stderr)

    # Optional: save to file
    if args["save_file"]:
        save_to_file(combined, args["save_file"])

    # Summary
    print(f"\nDone. {len(results)} retrieved, {len(errors)} failed.\n", file=sys.stderr)


if __name__ == "__main__":
    main()
