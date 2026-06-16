# Timeline (React + TypeScript + Vite)

This app renders the timeline data stored in this repo and served from `timeline/public`.

## How to run

From the repo root:

```bash
cd timeline
npm install
npm run dev
```

Then open the local Vite URL that prints in the terminal.

## Data files

- AI timeline data: `timeline/public/data.json` (source of truth is also written to `timeline-data/data.json`)
- Marketing/brand intelligence data: `timeline/public/marketing-data.json` (source of truth is also written to `marketing-data/data.json`)

## Updating data (agents)

From the repo root:

```bash
python "timeline-agent/main.py"
python "marketing-agent/main.py"
```

Each agent merges new entries into its JSON targets without overwriting history and de-dupes by `(event, date, source)`.
