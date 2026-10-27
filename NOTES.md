# Notes

## How to run

1. Copy `cloud-flare.sh` to `cloud-flare.local.sh` and fill in your Cloudflare account ID and a Workers AI API token.
2. Run `python classify.py` (Python 3, standard library only). It classifies `comments.json` with Clef and caches the answers in `output/`.
3. Open `output/comments.html` in a browser to see every comment with its label, confidence and probabilities.

Options: `python classify.py comments-v2.json` for another file, `--model clef-flash` for the faster model,
`--fresh` to ignore the cache. Offline tests: `python -m unittest`.

## Tools and models used

- **Cloudflare Workers AI, `clef` model**: classifies each comment as acceptable, toxic or spam. I wrote the
  instructions and the description of each label myself, with the forum context (an Indian college course,
  Hinglish is normal) and the tricky cases (blunt code feedback, grading complaints, apologies).
- **An AI coding assistant**: wrote the Python program, the HTML report and the tests, and checked the
  page in a browser.
- **Python standard library only**: no packages to install.
- **MISTAKES.md**: drafted with the AI coding assistant. <!-- add how you reviewed it yourself -->

## What I felt about doing this

<!-- Write this part yourself: a few honest lines about the task. -->
