# doi2bibtex

Convert DOI numbers or URLs to BibTeX entries — from the command line.
> [!IMPORTANT]
> For Windows users, your Python scripts must be on PATH for this to work from command line anywhere.

## Install

```bash
pip install .
```

Or for development (editable install — changes to the script take effect immediately):

```bash
pip install -e .
```

After installing, the `doi2bib` command is available globally.

## Usage

```bash
# Single DOI
doi2bib 10.1016/S0021-9258(19)52451-6

# Full DOI URL works too
doi2bib https://doi.org/10.1016/S0021-9258(19)52451-6

# Multiple DOIs (space or comma separated)
doi2bib 10.1038/nature12373 10.1145/1327452.1327492
doi2bib 10.1038/nature12373,10.1145/1327452.1327492

# Read DOIs from a text file
doi2bib -txt my_dois.txt

# Copy result to clipboard
doi2bib 10.1038/nature12373 -c
doi2bib 10.1038/nature12373 -copy

# Save to a .bib file (appends) or .txt file (overwrites)
doi2bib 10.1038/nature12373 -s refs.bib
doi2bib 10.1038/nature12373 -save refs.bib

# Mix and match
doi2bib -txt dois.txt 10.1038/extra -c -s refs.bib
```

## Text file format

```
# My references (lines starting with # are ignored)
10.1038/nature12373
10.1145/1327452.1327492
https://doi.org/10.1109/5.771073

# Comma-separated also works
10.1016/j.cell.2020.01.001, 10.1126/science.abc1234
```

## Notes

- Results always print to **stdout**, so you can also pipe: `doi2bib 10.xxx/yyy >> refs.bib`
- Status messages go to **stderr** and won't pollute piped output
- Saving to a `.bib` file **appends**; saving to `.txt` **overwrites**
- A small delay is added between requests to be polite to doi.org

## Dependencies

- [`requests`](https://pypi.org/project/requests/)
- [`pyperclip`](https://pypi.org/project/pyperclip/) — for clipboard support
