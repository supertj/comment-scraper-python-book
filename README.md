# Reading Reddit and Hacker News threads in Python

Source of the Jupyter Book published at https://comment-scraper.com/book

A short book on working with an exported Reddit or Hacker News thread in pandas: check the reply
tree, filter by depth, score and OP, count the words people use, and check the quotes an LLM
pulls from numbered comments. The examples use synthetic threads written for the book, in the
export format of Comment Scraper (https://comment-scraper.com/).

The notebook chapters run when the book is built, so the tables, charts and printed output in
them come from the code. Notebooks are committed without outputs for that reason.

## Build it

Python 3.12 and Node.js 18 or newer:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                            # tests for threadtools.py
jupyter book start --execute                   # live preview
jupyter book build --html --execute --strict   # static site in _build/html
```

## Publish it on comment-scraper.com

The book is served as static files from the Comment Scraper repository, under
`apps/web/public/book/`. With that repository checked out on a feature branch:

```bash
./build-for-site.sh /path/to/comment-scraper
```

The script builds with `BASE_URL=/book`, drops the `robots.txt` and `sitemap.xml` that MyST
writes for a site at the domain root, and replaces `apps/web/public/book/` in the checkout. If you
add or rename a page, also update the page list in that repository's `apps/web/lib/book.ts`.

## Files

| File | What it is |
|---|---|
| `myst.yml` | Book configuration and table of contents |
| `index.md`, `run-it-yourself.md` | Text pages |
| `load-and-check.ipynb`, `filter-comments.ipynb`, `count-words.ipynb`, `check-llm-citations.ipynb` | Notebook chapters |
| `threadtools.py` | Loading, tree checks, numbered Markdown and quote checks, shared by the chapters |
| `charts.py` | The two charts |
| `data/` | Sample exports, price labels, and the prompt and answer of the model run |
| `scripts/make_sample_export.py` | Writes the sample exports |
| `scripts/ask_model.py` | Sent the prompt to the model once; the build doesn't run it |
| `tests/` | Tests for `threadtools.py` |
| `style.css`, `images/` | Site colours, logo and favicon |

## License

The code (`threadtools.py`, `charts.py`, `scripts/`, `tests/` and the code cells in the notebooks) is under the MIT License, see `LICENSE`. The book text and the sample data in `data/` are under CC BY 4.0, see `LICENSE-CC-BY-4.0.txt`. The Inter font in `fonts/` keeps its own license, `fonts/OFL.txt`. The Comment Scraper name and logo in `images/` aren't covered by either license.
