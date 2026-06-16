# Agents

An agent is a program that can perceive its environment, make decisions, and take actions to achieve a goal — on its own, without you manually doing each step.

Tools are how an agent reaches out and does things in the real world. Without tools, an agent is just thinking — it can reason and generate text, but it's trapped inside its own knowledge. Tools give it hands.
When the agent calls a tool, it's essentially saying, "I need something I can't figure out on my own — let me go get it." The tool runs, returns data, and the agent uses that data to continue working toward its goal.

## News agent (AI timeline)

This repo includes a timeline news agent at `timeline-agent/main.py`. It follows this pattern:

1. **Trigger** — GitHub Actions (manual by default) runs `/.github/workflows/python-app.yml`.
2. **Collection** — Claude uses web search to find today’s AI news.
3. **Filtering** — Claude selects a single most notable event across categories like new terms, major releases, or shutdowns.
4. **Structured output** — It returns strict JSON with fields like `event`, `description`, `source`, and `date`.
5. **Deterministic delivery** — The script validates/merges/de-dupes and writes data to:
   - `timeline-data/data.json`
   - `timeline/public/data.json`

The clean insight here is that AI judgment is used only for collection + selection; everything else is deterministic automation.

## Marketing agent (Marketing Analyst / Brand Manager)

This repo also includes a marketing/brand intelligence agent at `marketing-agent/main.py`. It follows the same pattern as the timeline news agent:

1. **Trigger** — GitHub Actions (manual by default) runs `/.github/workflows/update-marketing-data.yml`.
2. **Role selection** — The agent can be run for a specific persona:
   - CLI: `python "marketing-agent/main.py" --role marketing_analyst|brand_manager|other`
   - Env var: `MARKETING_ROLE=marketing_analyst|brand_manager|other`
3. **Collection** — Claude uses web search to find several candidate developments (recent, reputable sources).
4. **Selection** — Claude picks the **single most actionable** development for the chosen role across:
   - `platform_change` (platform/privacy/measurement)
   - `competitor_campaign` (campaign/repositioning/partnership)
   - `consumer_trend` (culture/consumer behavior)
   - `regulation` (policy/regulatory)
5. **Structured output** — It returns strict JSON with fields designed for both:
   - **Marketing Analyst**: `analyst_take` (what to measure/watch; reporting/budget implications)
   - **Brand Manager**: `brand_take` (positioning/messaging/creative implications)
   - Plus optional “work product” fields when available: `kpis_to_watch`, `who_it_impacts`, `expected_directional_impact`, `next_7_days`, `next_30_days`, `assumptions_and_risks`, `confidence`, `role_primary`.
6. **Deterministic delivery** — The script validates/merges/de-dupes and writes data to:
   - `marketing-data/data.json`
   - `timeline/public/marketing-data.json`

As with the news agent, AI judgment is used only for collection + selection; everything else is deterministic automation.
