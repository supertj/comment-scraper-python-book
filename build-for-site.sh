#!/usr/bin/env bash
# Build the book for https://comment-scraper.com/book and copy it into a checkout of the
# Comment Scraper repository. Usage: ./build-for-site.sh /path/to/comment-scraper
# Run it with this repository's virtual environment active: the build runs the notebooks with
# the "python" it finds on PATH.
set -euo pipefail

# Resolve to an absolute path before the cd below, so a relative argument can't point somewhere else
site_repo="$(cd -- "${1:?usage: $0 /path/to/comment-scraper}" >/dev/null && pwd)"
# Guard against wiping the wrong directory: the target must look like the website app
if [[ ! -f "$site_repo/apps/web/next.config.ts" || ! -d "$site_repo/apps/web/public" ]]; then
  echo "$site_repo does not look like the Comment Scraper repository" >&2
  exit 1
fi
target="$site_repo/apps/web/public/book"

cd "$(dirname "$0")"
# Start from a clean build: _build/site keeps files from earlier builds, and the execution cache is
# keyed on the notebook source, not on the data files the notebooks read. Execution takes seconds.
rm -rf _build/html _build/site _build/execute
# --strict fails the build when a notebook cell raises, including the checks on the numbers in the text
BASE_URL=/book jupyter book build --html --execute --strict

# MyST writes these for a site at the domain root and points them at localhost. The website's own
# robots.txt and sitemap.xml cover the book pages instead.
rm -f _build/html/robots.txt _build/html/sitemap.xml _build/html/sitemap_style.xsl

# The theme's "site not loading correctly?" fallback links to the MyST docs. The website keeps
# outbound links to a minimum and marks the ones it has to keep as nofollow.
find _build/html -name '*.html' -exec sed -i.bak \
  's|<a href="https://mystmd.org/guide/deployment#deploy-base-url">|<a href="https://mystmd.org/guide/deployment#deploy-base-url" rel="nofollow">|g' {} +
find _build/html -name '*.html.bak' -delete

rm -rf "$target"
mkdir -p "$target"
cp -R _build/html/. "$target/"
echo "Copied $(find "$target" -type f | wc -l | tr -d ' ') files to $target"
