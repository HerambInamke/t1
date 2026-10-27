"""Classify forum comments as acceptable / toxic / spam with Cloudflare Clef, then write an HTML report.

Usage:
    python classify.py                      # comments.json with clef -> output/comments.html
    python classify.py comments-v2.json     # another input file
    python classify.py --model clef-flash   # the faster, cheaper model
    python classify.py --fresh              # ignore cached answers and call the API again
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "templates" / "report.html"
OUTPUT = ROOT / "output"

LOW_CONFIDENCE = 0.5  # answers below this are flagged for a human look

QUESTION = {
    "type": "choice",
    "instructions": (
        "`comment` is a post by `author` in the `thread` thread of the discussion forum of a "
        "3rd-year B.Tech CSE college course on building things with AI coding "
        "assistants. Students, TAs and professors post here; Indian English and Hinglish are normal. "
        "Decide whether the post should stay up. Judge the post itself: rudeness aimed at a person "
        "is not excused by being a joke, and an apology, a complaint or blunt technical criticism "
        "is not toxic just because the topic is negative."
    ),
    "criteria": {
        "acceptable": (
            "A normal course post: questions, answers, doubts, tips, sharing one's own project or "
            "a link to it for feedback, honest criticism of someone's code or app, complaints or "
            "disagreement about grading, deadlines or the course stated without insults, "
            "admitting one is struggling, thanks, jokes, apologies for an earlier comment."
        ),
        "toxic": (
            "Attacks or demeans a person or group: insults, name-calling, mocking someone's work "
            "or ability to humiliate them, harassment, threats (including 'see you outside'), "
            "stereotypes or slurs about gender, region, caste, branch or community, or calling "
            "out a specific classmate with accusations meant to shame them."
        ),
        "spam": (
            "Posted to sell or promote something unrelated to helping with the course: ads, "
            "paid assignment/solution services, leaked papers, get-rich-quick or crypto schemes, "
            "job/registration-fee scams, giveaways asking for personal data, follower selling, "
            "referral codes, or self-promotion of channels/groups. Usually has contact numbers, "
            "links or prices and an account name that isn't a person's name."
        ),
    },
}


def load_creds(path=ROOT / "cloud-flare.local.sh"):
    try:
        creds = dict(re.findall(r'export (\w+)="([^"]*)"', Path(path).read_text()))
        return creds["CLOUDFLARE_ACCOUNT_ID"], creds["CLOUDFLARE_API_TOKEN"]
    except (FileNotFoundError, KeyError):
        sys.exit(f"Missing credentials: copy cloud-flare.sh to {path} and fill in your account ID and token.")


def ask_clef(comment, account, token, model, tries=5):
    payload = {
        "state": {k: comment[k] for k in ("author", "thread", "comment")},
        "questions": {"label": QUESTION},
    }
    request = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/cloudflare/{model}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
            if not data.get("success"):
                raise RuntimeError(f"Clef error: {data.get('errors')}")
            return data["result"]["answers"]["label"]
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f"HTTP {e.code}: bad account ID or token (needs Workers AI Read + Edit). {e.read().decode(errors='replace')}")
            if (e.code != 429 and e.code < 500) or attempt == tries - 1:
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt)  # 429 / 5xx / network blip: back off and retry


def classify_all(comments, cache_path, model, fresh):
    cache = {} if fresh or not cache_path.exists() else json.loads(cache_path.read_text(encoding="utf-8"))
    todo = [c for c in comments if str(c["id"]) not in cache]
    if todo:
        account, token = load_creds()
    for i, c in enumerate(todo, 1):
        answer = ask_clef(c, account, token, model)
        cache[str(c["id"])] = answer
        cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")  # save after each call so a crash loses nothing
        print(f"[{i}/{len(todo)}] #{c['id']}: {answer['choice']} ({answer['confidence']:.2f})")
    return cache


def render_html(meta, comments, answers, model):
    """Fill the report template with the comments and Clef's answers. The page itself renders them."""
    data = {
        "forum": meta.get("forum", "Comments"),
        "course": meta.get("course", ""),
        "model": model,
        "low": LOW_CONFIDENCE,
        "comments": [{**c, **answers[str(c["id"])]} for c in comments],
    }
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")  # a comment can't close the <script> tag
    return (TEMPLATE.read_text(encoding="utf-8")
            .replace("{{title}}", html.escape(f"Clef review: {data['forum']}"))
            .replace("{{data}}", blob))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", nargs="?", default="comments.json")
    parser.add_argument("--model", default="clef", choices=["clef", "clef-flash"])
    parser.add_argument("--fresh", action="store_true", help="ignore cached answers")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252

    src = Path(args.input)
    meta = json.loads(src.read_text(encoding="utf-8"))
    comments = meta["comments"]
    OUTPUT.mkdir(exist_ok=True)
    answers = classify_all(comments, OUTPUT / f"{src.stem}.{args.model}.results.json", args.model, args.fresh)
    out = OUTPUT / f"{src.stem}.html"
    out.write_text(render_html(meta, comments, answers, args.model), encoding="utf-8")
    print(f"Wrote {out} ({len(comments)} comments)")


if __name__ == "__main__":
    main()
