# Marketing Agent

Generates a single most-actionable **marketing/brand intelligence** development for **today** and writes/merges it into:

- `marketing-data/data.json`
- `timeline/public/marketing-data.json`

The output is structured to be useful for **Marketing Analysts**, **Brand Managers**, and adjacent roles.

## Prerequisites

- Python **3.12+**
- An Anthropic API key

## Setup

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r "marketing-agent/requirements.txt" anthropic
```

## Configure environment

Option A (recommended): export an env var:

```bash
export ANTHROPIC_API_KEY="YOUR_KEY"
```

Option B: create `marketing-agent/.env`:

```bash
ANTHROPIC_API_KEY=YOUR_KEY
```

## Run

From the repo root:

```bash
python "marketing-agent/main.py"
```

If a new development is found, the agent merges it into the JSON files (without overwriting historical entries) and de-dupes by `(event, date, source)`.

## GitHub Actions

The workflow `/.github/workflows/update-marketing-data.yml` runs this script and opens a PR if the JSON files changed.

