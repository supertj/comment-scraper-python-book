---
title: Run it yourself
description: The sample Reddit and Hacker News exports, the helper modules, the model answer and the commands to rebuild the book and run its tests.
---

Everything in the book can be rebuilt from the files below. The source, including the tests, is in the supertj/comment-scraper-python-book repository on GitHub.

## The files

Sample data, written for this book and in Comment Scraper's export format:

- {download}`data/sample_thread.json`: the Reddit thread, "JSON, one row per comment"
- {download}`data/sample_thread_nested.json`: the same thread, "JSON, replies nested"
- {download}`data/sample_thread.csv`: the same thread as CSV
- {download}`data/sample_hn_thread.json` and {download}`data/sample_hn_thread.csv`: the Hacker News thread
- {download}`data/price_labels.csv`: my reading of the 30 comments in the price section of [Count the words people use](count-words.ipynb)

Code:

- {download}`threadtools.py`: loading, tree checks, the numbered Markdown and the quote checks
- {download}`charts.py`: the two charts
- {download}`scripts/make_sample_export.py`: writes the sample data
- {download}`scripts/ask_model.py`: sent the prompt to the model once
- {download}`requirements.txt`

The model's input and output:

- {download}`data/llm/prompt.md`: the prompt, built by the last chapter's code
- {download}`data/llm/answer.md`: the answer, exactly as it came back
- {download}`data/llm/answer.json`: which model answered, when, and how many tokens it used

Each notebook chapter can also be downloaded as a Jupyter notebook from the download menu at the top of its page.

## Build the book

With Python 3.12, from the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                    # tests for threadtools.py
jupyter book build --html --execute    # runs every notebook, writes _build/html
```

The build executes each notebook from the top, so the tables, charts and printed output come from the code above them. Some cells that are hidden in the book check the numbers the text relies on, and the build fails if the data changes under them.

## The sample data

`python scripts/make_sample_export.py` writes the files in `data/`. Every comment is in the script, written by hand, and the IDs and timestamps come from a fixed random seed, so it writes the same files every time.

## The model's answer

`scripts/ask_model.py` sends `data/llm/prompt.md` to the Anthropic API once and saves the reply:

```{literalinclude} scripts/ask_model.py
:start-at: MODEL =
```

The saved answer came from Claude Haiku 5.5 (`claude-haiku-5-5`) with extended thinking off, on 28 October 2026 (UTC). To try it with your own key, put the key in the `ANTHROPIC_API_KEY` environment variable, install the `anthropic` package and run the script. Your answer will differ from the saved one, and the last chapter's text describes the saved one, so its hidden checks will fail until you update them. The test `test_saved_prompt_matches_the_sample_thread` fails if the sample data changes without a new answer.
