# Timeline Agent

Generates a single notable AI timeline event for **today** and writes/merges it into:

- `timeline-data/data.json`
- `timeline/public/data.json`

It’s designed to run locally or via GitHub Actions.

## Prerequisites

- Python **3.12+**
- An Anthropic API key

## Setup

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r "timeline-agent/requirements.txt" anthropic
```

## Configure environment

Option A (recommended): export an env var:

```bash
export ANTHROPIC_API_KEY="YOUR_KEY"
```

Option B: create `timeline-agent/.env`:

```bash
ANTHROPIC_API_KEY=YOUR_KEY
```

## Run

From the repo root:

```bash
python "timeline-agent/main.py"
```

If a new event is found, the agent merges it into the JSON files (without overwriting historical entries) and de-dupes by `(event, date, source)`.

## GitHub Actions

The workflow `/.github/workflows/python-app.yml` runs this script and opens a PR if the JSON files changed.

