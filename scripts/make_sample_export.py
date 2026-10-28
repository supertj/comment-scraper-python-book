"""Build the two synthetic threads used in the book.

Every comment below was written by the author for this book. No real Reddit or
Hacker News content or usernames are involved. The output follows Comment
Scraper's export schema v1, so the book's code runs unchanged on a real export.

Run from the repository root:  python scripts/make_sample_export.py
Writes, in data/:
  sample_thread.json         Reddit thread, "JSON, one row per comment"
  sample_thread_nested.json  the same thread, "JSON, replies nested"
  sample_thread.csv          the same thread as CSV
  sample_hn_thread.json      a small Hacker News thread, one row per comment
  sample_hn_thread.csv       the same Hacker News thread as CSV
"""

import json
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(7)

SUBREDDIT = "ExampleMealKits"
THREAD_ID = "1nq7x2k"
THREAD_TITLE = "Cancelled our meal kit after 14 months. What finally made you quit yours?"
SLUG = "cancelled_our_meal_kit_after_14_months_what"
POST_BODY = (
    "Two adults, signed up with the intro deal, used it pretty consistently for about a year, "
    "then started skipping weeks and finally cancelled last month. Curious if people quit for "
    "the same reasons we did or different ones."
)
POSTED_AT = datetime(2026, 9, 14, 14, 5, tzinfo=timezone.utc)


def c(text, score, *replies, op=False, state="normal", hidden=False, edited=False):
    """One comment: text, score, replies. state is normal/deleted/removed like the export."""
    return {"text": text, "score": score, "replies": list(replies), "op": op,
            "state": state, "hidden": hidden, "edited": edited}


TREE = [
    c("Price. It started at $8 a serving with the intro discount and crept up to $12.49 by month six. "
      "At that point I was paying restaurant-adjacent prices to wash my own dishes.", 412,
      c("Same. The intro discount is doing a lot of work in their marketing.", 96,
        c("It's the gym membership model. They know half of us forget to cancel.", 41,
          c("We definitely paid for two months we didn't use before I noticed.", 18, op=True))),
      c("Did you ever compare it to just buying the same recipes at the grocery store? "
        "I did for a month and the gap wasn't as big as people think.", 37,
        c("How big was the gap for you?", 23,
          c("I priced 9 recipes against my local store. Kit was $11.90 a serving, groceries came to "
            "$7.40, but I ended up with half bottles of fish sauce and mirin I never used again. If you "
            "count the waste it was closer to $9. So yes, more expensive, but not double.", 187,
            c("This is the most useful comment in the thread. Nobody counts the leftover half bottles.", 64),
            c("Your $9 assumes you throw out the leftovers. I cook a lot so the fish sauce gets used. "
              "For me groceries win by a mile.", 29,
              c("Fair, it depends entirely on how stocked your pantry already is.", 22,
                c("Which is exactly the person these kits aren't for. Beginners have empty pantries.", 31)))))),
      c("Groceries are cheaper but the kit saved us from the 6pm 'what's for dinner' argument. "
        "That has value.", 52)),

    c("Packaging. Every box came with ice packs, insulated liners and about 14 tiny plastic bags. "
      "Our recycling bin was full by Tuesday.", 298,
      c("The liners are supposedly curbside recyclable now?", 19,
        c("Depends on your city. Ours takes the cardboard but not the liner, and the gel packs "
          "can't go down the drain.", 27,
          c("You can cut the gel packs open and put the gel in the trash, but at that point it's a chore.", 11)),
        c("I looked it up for mine and the answer was 'drop off at a store'. Nobody is doing that every week.", 24)),
      c("We started keeping the ice packs for lunch boxes. Now we have 60 ice packs.", 88,
        c("lol the freezer drawer of shame", 35)),
      c("", 3, state="deleted")),

    c("Honestly the recipes got repetitive. By month four it was the same six proteins in different sauces.", 241,
      c("The premium recipes were the only ones that felt new, and they cost extra.", 47,
        c("Surcharge recipes are such a trick. The menu shows them first.", 21)),
      c("Did you try switching plans? The bigger plan had a wider menu for us.", 6,
        c("We were on the biggest one. Still repetitive.", 9)),
      c("I'd argue that's a feature. I wanted boring and predictable on weeknights.", 15,
        c("Predictable is fine, but not the same chicken thigh four weeks in a row.", 26))),

    c("Missing ingredients. Three boxes in a row were missing something essential, once it was the protein. "
      "Support gave credits but credits don't make dinner on a Wednesday.", 176,
      c("Same thing happened to us with the sauce packet. The recipe without the sauce is just plain noodles.", 33),
      c("Credits are their way of keeping you subscribed. You can't cash them out.", 44,
        c("Exactly. I had $40 in credits when I cancelled and they just disappeared.", 20,
          c("Ours were honored for one last box after we paused. Might depend on whether you pause or cancel.", 12,
            c("Good tip. We cancelled outright, so ours are gone too.", 5, op=True)))),
      c("The delivery window was the bigger problem for us. The box sat on the porch for 5 hours in July.", 38,
        c("Did the food survive?", 7,
          c("Ice packs melted, meat was warm. Threw it all out and got a credit, see above.", 14)))),

    c("The skip-a-week flow. You had to skip by Wednesday midnight for the following week, and the app "
      "kept logging me out. Missed the deadline twice.", 133,
      c("The deadline being in a different time zone than me didn't help.", 17),
      c("I set a recurring phone reminder. Still missed it once when I was traveling.", 12),
      c("", 1, state="removed")),

    c("Counterpoint: it taught me to cook. I quit after a year, but I kept about 15 of the recipe cards "
      "and still make them.", 205,
      c("Same, the recipe cards are the real product.", 58,
        c("I photographed every card before recycling it. Best thing I got out of it.", 30)),
      c("This is the only reason I'd recommend it to someone. Use it for three months, keep the cards, quit.", 73,
        c("Three months is about right. That's when the repeats start.", 28,
          c("That matches us pretty much exactly. Month four is when we started skipping.", 16, op=True)))),

    c("Portions. Two servings were really 1.5 servings for my partner and me. We always ended up making "
      "toast on the side.", 119,
      c("Depends a lot on the recipe. The pasta ones were huge, the fish ones tiny.", 22,
        c("Yeah the fish portions were sad.", 13)),
      c("We added a side salad every night, which kind of defeats the point.", 18)),

    c("Nothing made us quit, we moved somewhere they don't deliver. Still miss it a bit.", 64,
      c("Short and wholesome.", 9)),

    c("The cancel flow. Four screens of 'are you sure', a discount offer, a survey, then a 'pause instead?' "
      "button styled like the main button.", 158,
      c("Dark patterns. Pause instead is designed so you click it by mistake.", 61,
        c("I clicked it by mistake. Got charged three weeks later.", 34,
          c("Did you get a refund?", 4,
            c("After two emails, yes. Took 9 days.", 15)))),
      c("Ha, ours had the same 'pause instead' button. I took a screenshot because I didn't trust it.", 27, op=True)),

    c("We quit because of food waste, weirdly. We'd skip cooking one night, then the fish would go off "
      "before we got to it.", 97,
      c("The fish-first rule saved us. Always cook the seafood recipe on day one.", 49,
        c("Should be printed on the box honestly.", 19))),

    c("My kid stopped eating anything with cilantro and half the recipes had it. You can't customize "
      "ingredients.", 46,
      c("You can sometimes swap the protein but never the garnishes. It's weird.", 10)),

    c("- Price went up\n- Delivery moved to Friday\n- Fewer vegetarian options\n\nThat's it, that's the list.", 88,
      c("Fewer vegetarian options is real. The vegetarian menu went from 8 to 4 options for us.", 25,
        c("And two of those were pasta with cheese.", 21))),

    c("Unpopular opinion, but the kits are fine. People just expect them to be cheaper than groceries "
      "and they never will be.", 57,
      c("Nobody expects cheaper than groceries. We expect the price at signup to be the price.", 93,
        c("This. It's the price creep, not the price.", 44,
          c("Price creep plus shrinking portions. Same price, less food.", 26,
            c("Is that documented anywhere or just vibes?", 8,
              c("Just my receipts. Two servings of the salmon recipe went from 2 fillets to what looked like 1.5.", 17,
                c("Fair enough, anecdote noted.", 6))))))),

    c("We kept ours. Two kids, both parents working, it's still worth it for us on the 3 busiest nights.", 81,
      c("That's the use case I think it's actually good for.", 23),
      c("Honestly this might be where we end up again once the baby arrives.", 12, op=True, edited=True)),

    c("Too much prep time. Recipes said 30 minutes but with chopping it was always 50+.", 74,
      c("The time estimate assumes you chop like a line cook.", 40,
        c("And that all your pans are already clean.", 18)),
      c("I timed a month of them. Our average was about 1.5x the printed time.", 21)),

    c("", 12,
      c("Nobody's saying meal kits are a scam, just that the pricing isn't honest.", 15,
        c("Agreed.", 3)),
      state="deleted"),

    c("Switched to a weekly meal plan and a grocery pickup order. Cheaper and less packaging, but more planning.", 69,
      c("What do you use for the meal plan?", 5,
        c("A spreadsheet with 20 dinners we like. I rotate through it.", 14,
          c("Simple. Love it.", 4)))),

    c("Delivery got moved from Tuesday to Friday without telling us. Friday is our takeout night, so the "
      "box just sat there.", 52,
      c("Same. They moved our delivery day twice in three months.", 11)),

    c("Packaging and price, in that order.", 33),

    c("The quality dropped. The produce started arriving bruised, and once the avocado was basically liquid.", 61,
      c("Avocados should never be shipped in a box, I'll die on this hill.", 29,
        c("Agreed, the avocado lottery.", 12))),

    c("Late to this, but customer support was great for us. Every issue got a credit within an hour.", None,
      c("Credits within an hour is fast. Ours took a day.", None, hidden=True),
      hidden=True),
]

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def new_id(used):
    while True:
        candidate = "n" + "".join(random.choice(ALPHABET) for _ in range(6))
        if candidate not in used:
            used.add(candidate)
            return candidate


def iso(moment):
    # Matches JavaScript's Date.toISOString(), which the extension uses.
    return moment.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def build_records():
    used = {THREAD_ID}
    post = {
        "schema_version": 1, "source": "reddit", "record_type": "post",
        "thread_id": THREAD_ID, "thread_title": THREAD_TITLE, "subreddit": SUBREDDIT,
        "comment_id": None, "parent_id": None, "depth": None,
        "score": 1840, "score_hidden": False,
        "created_utc": iso(POSTED_AT), "edited_utc": iso(POSTED_AT + timedelta(minutes=42)),
        "is_op": True, "body": POST_BODY,
        "permalink": f"https://www.reddit.com/r/{SUBREDDIT}/comments/{THREAD_ID}/{SLUG}/",
        "comment_state": "normal",
    }
    records = [post]
    # Late top-level comments arrive while the thread is still hiding scores.
    late_start = POSTED_AT + timedelta(hours=30)

    def walk(node, parent_id, depth, parent_time, position):
        comment_id = new_id(used)
        if node["hidden"]:
            created = late_start + timedelta(minutes=random.randint(1, 40) + 45 * depth)
        elif depth == 0:
            created = POSTED_AT + timedelta(minutes=6 + position * 37 + random.randint(0, 20))
        else:
            created = parent_time + timedelta(minutes=random.randint(4, 95))
        normal = node["state"] == "normal"
        records.append({
            "schema_version": 1, "source": "reddit", "record_type": "comment",
            "thread_id": THREAD_ID, "thread_title": THREAD_TITLE, "subreddit": SUBREDDIT,
            "comment_id": comment_id, "parent_id": parent_id, "depth": depth,
            "score": None if node["hidden"] else node["score"],
            "score_hidden": node["hidden"],
            "created_utc": iso(created),
            "edited_utc": iso(created + timedelta(minutes=12)) if node["edited"] else None,
            "is_op": node["op"],
            "body": node["text"] if normal else "",
            "permalink": f"https://www.reddit.com/r/{SUBREDDIT}/comments/{THREAD_ID}/{SLUG}/{comment_id}/",
            "comment_state": node["state"],
        })
        for index, reply in enumerate(node["replies"]):
            walk(reply, comment_id, depth + 1, created, index)

    for position, node in enumerate(TREE):
        walk(node, THREAD_ID, 0, POSTED_AT, position)
    return records


# --- CSV writer: same rules as the extension's CSV export ---------------------------------
CSV_COLUMNS = [
    "schema_version", "source", "record_type", "thread_id", "thread_title", "subreddit",
    "comment_id", "parent_id", "parent_missing", "depth", "score", "score_hidden",
    "created_utc", "edited_utc", "is_op", "comment_state", "body", "permalink",
    "task_state", "fetch_path", "fetched_at",
]
# Text cells that a spreadsheet could read as a formula get a leading apostrophe.
FORMULA_START = re.compile("^[=+\\-@\t\r\n＝＋－＠]")


def csv_cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if FORMULA_START.match(text):
        text = "'" + text
    if re.search(r'[",\r\n]', text):
        text = '"' + text.replace('"', '""') + '"'
    return text


def nest_comments(records):
    """Port of the extension's nestComments: records are in tree order, so one pass nests them."""
    roots, by_id = [], {}
    for record in records:
        if record["record_type"] != "comment":
            continue
        node = {**record, "replies": []}
        by_id[record["comment_id"]] = node
        parent = by_id.get(record["parent_id"])
        (parent["replies"] if parent else roots).append(node)
    return roots


# --- Hacker News sample ---------------------------------------------------------------------
# HN has no comment scores (the export leaves them null), numeric IDs, and no subreddit.
HN_THREAD_ID = "45120388"
HN_TITLE = "Ask HN: How do you keep a side project's hosting bill under $20 a month?"
HN_POST = ("I run three small sites for fun and the bill keeps creeping up. Curious what other people "
           "do before it turns into a real expense.")
HN_POSTED_AT = datetime(2026, 9, 21, 16, 40, tzinfo=timezone.utc)
HN_TREE = [
    c("One VPS, everything on it, nightly backups to object storage. Boring, but the bill hasn't "
      "changed in three years.", None,
      c("What happens when the VPS dies?", None,
        c("I restore from the backup onto a new one. Did it once, took about an hour.", None,
          c("That hour is what people are paying the platforms to avoid.", None))),
      c("Same setup here. The trick is not running a database server you don't need. SQLite covers "
        "all three of my sites.", None)),
    c("Free tiers until they stop being free, then move. I've moved twice this year.", None,
      c("Moving twice a year sounds like more work than paying $20.", None, op=True)),
    c("", None,
      c("The bandwidth line item is the one that surprises people, not compute.", None),
      state="deleted"),
    c("Turn off what nobody visits. I had a demo app from 2023 still costing $7 a month.", None,
      c("Good point. One of my three is probably that.", None, op=True)),
]


def build_hn_records():
    clock = random.Random(11)
    next_id = int(HN_THREAD_ID) + 5
    post = {
        "schema_version": 1, "source": "hn", "record_type": "post",
        "thread_id": HN_THREAD_ID, "thread_title": HN_TITLE, "subreddit": None,
        "comment_id": None, "parent_id": None, "depth": None,
        "score": 64, "score_hidden": False,
        "created_utc": iso(HN_POSTED_AT), "edited_utc": None,
        "is_op": True, "body": HN_POST,
        "permalink": f"https://news.ycombinator.com/item?id={HN_THREAD_ID}",
        "comment_state": "normal",
    }
    records = [post]

    def walk(node, parent_id, depth, parent_time):
        nonlocal next_id
        next_id += clock.randint(3, 40)
        comment_id = str(next_id)
        created = parent_time + timedelta(minutes=clock.randint(3, 80))
        normal = node["state"] == "normal"
        records.append({
            **post, "record_type": "comment", "comment_id": comment_id, "parent_id": parent_id,
            "depth": depth, "score": None, "created_utc": iso(created), "is_op": node["op"],
            "body": node["text"] if normal else "",
            "permalink": f"https://news.ycombinator.com/item?id={comment_id}",
            "comment_state": node["state"],
        })
        for reply in node["replies"]:
            walk(reply, comment_id, depth + 1, created)

    for node in HN_TREE:
        walk(node, HN_THREAD_ID, 0, HN_POSTED_AT)
    return records


def write_csv(path, records, meta):
    """UTF-8 with a byte order mark and CRLF line ends, one row per record, like the extension."""
    lines = [",".join(CSV_COLUMNS)]
    for record in records:
        row = {**record, "parent_missing": False, "task_state": meta["task_state"],
               "fetch_path": meta["fetch_path"], "fetched_at": meta["fetched_at"]}
        lines.append(",".join(csv_cell(row[column]) for column in CSV_COLUMNS))
    path.write_text("\ufeff" + "\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")


def write_json(path, threads, exported_at):
    export = {"schema_version": 1, "exported_at": exported_at, "generator": "Comment Scraper", "threads": threads}
    path.write_text(json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    records = build_records()
    comments = [r for r in records if r["record_type"] == "comment"]
    fetched_at = "2026-09-16T09:12:44.318Z"
    meta = {
        "source": "reddit", "thread_id": THREAD_ID, "thread_title": THREAD_TITLE,
        "permalink": records[0]["permalink"], "fetch_path": "json",
        "task_state": "all_known_fetched", "stop_reason": None,
        "fetched": len(comments), "known_unfetched_at_least": 0,
        # Reddit's own count usually differs a little from what it actually returns.
        "reported_by_source": len(comments) + 3,
        "fetched_at": fetched_at,
    }
    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    exported_at = "2026-09-16T09:12:51.902Z"
    write_json(out_dir / "sample_thread.json", [{"meta": meta, "records": records}], exported_at)
    write_json(out_dir / "sample_thread_nested.json",
               [{"meta": meta, "post": records[0], "comments": nest_comments(records)}], exported_at)

    write_csv(out_dir / "sample_thread.csv", records, meta)
    print(f"{len(comments)} Reddit comments written to {out_dir}")

    hn_records = build_hn_records()
    hn_comments = [r for r in hn_records if r["record_type"] == "comment"]
    hn_meta = {
        "source": "hn", "thread_id": HN_THREAD_ID, "thread_title": HN_TITLE,
        "permalink": hn_records[0]["permalink"], "fetch_path": "api",
        "task_state": "all_known_fetched", "stop_reason": None,
        "fetched": len(hn_comments), "known_unfetched_at_least": 0,
        # The extension leaves this null for Hacker News.
        "reported_by_source": None,
        "fetched_at": "2026-09-22T08:03:17.554Z",
    }
    write_json(out_dir / "sample_hn_thread.json", [{"meta": hn_meta, "records": hn_records}],
               "2026-09-22T08:03:18.120Z")
    write_csv(out_dir / "sample_hn_thread.csv", hn_records, hn_meta)
    print(f"{len(hn_comments)} Hacker News comments written to {out_dir}")


if __name__ == "__main__":
    main()
