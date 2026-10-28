"""Edge cases the sample threads don't cover. Run from the repository root: python -m pytest -q"""

import json
from pathlib import Path

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")  # no display needed for the chart test

import charts  # noqa: E402
import threadtools as t  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def record(comment_id, parent_id, depth, score=None, body="text", state="normal", **extra):
    return {
        "schema_version": 1, "source": "reddit", "record_type": "post" if comment_id is None else "comment",
        "thread_id": "abc1234", "thread_title": "test  thread", "subreddit": "test",
        "comment_id": comment_id, "parent_id": parent_id, "depth": depth,
        "score": score, "score_hidden": False, "created_utc": "2026-09-14T14:05:00.000Z",
        "edited_utc": None, "is_op": comment_id is None, "body": body if state == "normal" else "",
        "permalink": f"https://example.com/{comment_id}", "comment_state": state, **extra,
    }


def write_export(tmp_path, records, status="all_known_fetched"):
    meta = {"source": "reddit", "thread_id": "abc1234", "thread_title": "test thread", "permalink": "",
            "fetch_path": "json", "task_state": status, "stop_reason": "rate_limited" if status == "partial" else None,
            "fetched": len(records) - 1, "known_unfetched_at_least": 2, "reported_by_source": None,
            "fetched_at": "2026-09-16T09:12:44.318Z"}
    path = tmp_path / "export.json"
    path.write_text(json.dumps({"schema_version": 1, "threads": [{"meta": meta, "records": records}]}))
    return path


def test_nested_export_loads_to_the_same_rows():
    flat, _ = t.load_export(DATA / "sample_thread.json")
    nested, _ = t.load_export(DATA / "sample_thread_nested.json")
    assert nested.equals(flat)


def test_hidden_scores_stay_missing_and_hacker_news_ids_stay_text():
    reddit, _ = t.load_export(DATA / "sample_thread.json")
    hidden = reddit[reddit.score_hidden]
    assert len(hidden) == 2 and hidden.score.isna().all()
    hn, _ = t.load_export(DATA / "sample_hn_thread.json")
    comments = hn[hn.record_type == "comment"]
    assert comments.score.isna().all()
    assert all(isinstance(cid, str) for cid in comments.comment_id)


def test_partial_export_with_a_missing_parent(tmp_path, capsys):
    records = [record(None, None, None, 10, "post"),
               record("c1", "abc1234", 0, -4, "Downvoted top comment"),
               record("c3", "gone99", 2, 3, "Reply whose parent was never fetched", parent_missing=True),
               record("c4", "c3", 3, 1, "# not a heading\n```")]
    rows, meta = t.load_export(write_export(tmp_path, records, status="partial"))
    post, comments = t.check_tree(rows)
    assert "orphans: 1, depth mismatches: 0" in capsys.readouterr().out
    # Walking up stops at the comment whose parent isn't in the file
    assert t.chain_to_top("c4", comments.set_index("comment_id")) == ["c3", "c4"]
    markdown = t.thread_markdown(rows, meta.iloc[0])
    assert "status: partial (rate_limited)" in markdown
    assert "unknown reported by the source" in markdown
    assert "[c2] reply to a comment not fetched (score 3" in markdown
    assert "[c3] reply to [c2] (score 1" in markdown
    assert "\\# not a heading\n\\```" in markdown


def test_deleted_comments_keep_their_number(tmp_path):
    records = [record(None, None, None, 10, "post"),
               record("c1", "abc1234", 0, 5, state="deleted"),
               record("c2", "c1", 1, 2, "Still here")]
    rows, meta = t.load_export(write_export(tmp_path, records))
    assert t.number_comments(rows) == {"c1": 1, "c2": 2}
    markdown = t.thread_markdown(rows, meta.iloc[0])
    assert "[c1] (score 5, 1d ago)\n(deleted)" in markdown
    assert "# test thread" in markdown


def test_quote_checks():
    comments = pd.DataFrame({
        "comment_id": ["a", "b", "c"],
        "body": ["The box sat on the porch.", "Credits don't help on a Wednesday.", ""],
        "comment_state": ["normal", "normal", "deleted"],
    })
    numbers = {"a": 1, "b": 2, "c": 3}
    answer = "\n".join([
        '- "The box sat on the porch." [c1]',
        '- "credits don’t help" [c2]',
        '- "sat on the porch" [c2]',
        '- "a quote nobody wrote" [c1, c9]',
        '- "anything" [c3]',
        "- A point with no citation",
    ])
    checked = t.check_quotes(answer, comments, numbers)
    assert checked.verdict.tolist() == [
        "exact",
        "same words, different case or punctuation",
        "found in [c1] instead",
        "not in this comment",
        "no such comment",
        "cites a deleted comment",
    ]
    assert t.uncited_lines(answer) == ["- A point with no citation"]


def test_quote_checks_do_not_pass_shortened_or_empty_quotes():
    comments = pd.DataFrame({"comment_id": ["a"], "body": ["The price is $12.49 now."],
                             "comment_state": ["normal"]})
    answer = '- "The price is $12." [c1]\n- "..." [c1]\n- "the price is $12.49" [c1]'
    checked = t.check_quotes(answer, comments, {"a": 1})
    assert checked.verdict.tolist() == [
        "not in this comment", "no words to check", "same words, different case or punctuation"]


def test_citations_in_parentheses_and_unpaired_quotes():
    comments = pd.DataFrame({"comment_id": ["a"], "body": ["Nothing like it."],
                             "comment_state": ["normal"]})
    answer = '- "invented claim" ([c1])\n- "Nothing like it." [c1] (they also said "more")'
    checked = t.check_quotes(answer, comments, {"a": 1})
    assert checked.verdict.tolist() == ["not in this comment", "exact"]
    assert t.quotes_not_checked(answer) == ['- "Nothing like it." [c1] (they also said "more")']


def test_batch_exports_must_be_split_by_thread(tmp_path):
    first = [record(None, None, None, 10, "post"), record("c1", "abc1234", 0, 5)]
    second = [{**row, "thread_id": "xyz9876"} for row in first]
    rows, _ = t.load_export(write_export(tmp_path, first + second))
    with pytest.raises(ValueError, match="2 threads"):
        t.check_tree(rows)
    _, comments = t.check_tree(rows[rows.thread_id == "abc1234"])
    assert len(comments) == 1


def test_score_chart_refuses_a_thread_without_scores():
    hn, _ = t.load_export(DATA / "sample_hn_thread.json")
    comments = hn[hn.record_type == "comment"]
    scored = comments[comments.score.notna()]
    with pytest.raises(ValueError, match="no visible scores"):
        charts.score_by_depth(scored, scored.iloc[0:0])


def test_saved_prompt_matches_the_sample_thread():
    # The saved model answer was made from this exact prompt; if the data changes, ask again.
    rows, meta = t.load_export(DATA / "sample_thread.json")
    prompt = t.with_prompt(t.QUOTES_PROMPT, t.thread_markdown(rows, meta.iloc[0]))
    assert prompt == (DATA / "llm" / "prompt.md").read_text(encoding="utf-8")
