# Quick Answers

The package includes **97 curated quick-answer rules** in:

`data/brain/quick_answers.json.gz`

The bundle is compressed only to keep distribution/GitHub transfer compact. The agent loads it transparently.

Local customization remains easy:

- `data/brain/quick_answers.json` — human-editable legacy/local override list.
- `data/brain/quick_answers/*.json` — optional modular override files.

If an override uses the same `id` as a bundled rule, the local override wins.

Matching supports normalized punctuation/case, common typo corrections, light plural normalization, filler words, word-order variation, priorities, and exclusions.

The normal agent chat path remains cloud-first. Quick answers are explicitly invoked from the GUI **Local Quick** button or `/quick` CLI command.
