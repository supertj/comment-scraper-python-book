---
title: Reading Reddit and Hacker News threads in Python
short_title: Introduction
description: A short book on working with an exported Reddit or Hacker News thread in pandas. Check the reply tree, filter by depth, score and OP, count the words people use, and check the quotes an LLM pulls from numbered comments.
---

A thread export is a table of comments with a few extra columns that make it more than a list: who each comment replies to, how deep it sits, its score, and whether the person who started the thread wrote it. This book is about using those columns in Python.

It works through one thread from start to finish:

1. [Load an export and check it](load-and-check.ipynb). Read the JSON into pandas, confirm every reply has a parent, and deal with hidden scores, deleted comments, the CSV version of the same file and Hacker News threads.
2. [Filter by depth, score and OP](filter-comments.ipynb). Find the replies that outscored the comment they answer, see where the original poster (OP) joined in, and read a comment together with the comments above it.
3. [Count the words people use](count-words.ipynb). Count words and two-word phrases by the number of comments that use them, see which ones live in replies, and test a keyword rule against a careful reading.
4. [Check what a model quotes](check-llm-citations.ipynb). Number the comments the way Comment Scraper's Markdown export does, give them to an LLM, and check every quote it returns against the comment it cites.

The last page, [Run it yourself](run-it-yourself.md), lists the files and the commands to rebuild everything.

## The data

The main example is a Reddit thread in which people explain why they cancelled a meal-kit subscription. It's made up. I wrote all 95 comments for this book, in an invented subreddit, with no real users. I gave it the things that make real threads awkward: deleted and removed comments, hidden scores, a reply chain six levels deep and an OP who answers inside other people's branches. A second, smaller thread shows how Hacker News exports differ.

Both files follow the export format of [Comment Scraper](https://comment-scraper.com/), the browser extension I build. It exports a Reddit or Hacker News thread from your own browser to CSV, JSON, Markdown or Org, with the reply structure kept. The fields are listed in the [help pages](https://comment-scraper.com/docs#formats-and-fields). You don't need the extension to follow along: the sample files can be downloaded from [Run it yourself](run-it-yourself.md), and if your data comes from somewhere else, adapt the loader in the first chapter so it produces the same columns.

## What you need

Python 3.12 with pandas, matplotlib and scikit-learn. The notebook chapters run when the book is built, so every table, chart and printed line in them is real output from the code above it.

If you work on real threads, check the platform's terms before you publish anything built on them. Our page on [whether scraping Reddit is legal](https://comment-scraper.com/is-it-legal-to-scrape-reddit) covers what that means for reading and exporting threads.

Written by Super Lede.
