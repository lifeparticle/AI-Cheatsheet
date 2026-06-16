import os
import json
import re
import time
import random
import argparse
from datetime import datetime
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing ANTHROPIC_API_KEY. Set it in marketing-agent/.env and run again."
    )

client = anthropic.Anthropic(api_key=api_key)

current_date = datetime.now().strftime("%Y-%m-%d")
current_year = datetime.now().strftime("%Y")

# Opus 4.6 pricing (per million tokens)
INPUT_COST_PER_M = 5.00
OUTPUT_COST_PER_M = 25.00


def calc_cost(input_tokens, output_tokens):
    return (input_tokens / 1_000_000) * INPUT_COST_PER_M + \
           (output_tokens / 1_000_000) * OUTPUT_COST_PER_M


total_cost = 0.0


def _normalize_role(role: str) -> str:
    r = (role or "").strip().lower()
    if r in ("marketing-analyst", "marketing_analyst", "analyst", "ma"):
        return "marketing_analyst"
    if r in ("brand-manager", "brand_manager", "brand", "bm"):
        return "brand_manager"
    return "other"


ROLE_PROFILES: dict[str, dict[str, object]] = {
    "marketing_analyst": {
        "label": "Marketing Analyst",
        "decision_horizon": "daily/weekly optimization + monthly reporting + quarterly budget shifts",
        "primary_outputs": [
            "what changed (platform/policy/competitor/trend) + impact on measurement",
            "KPIs to watch + expected directional impact",
            "instrumentation / tracking checklist (server-side, consent, events, QA)",
            "recommended validation: attribution vs incrementality vs MMM",
            "7-day + 30-day actions",
        ],
        "focus_prompt": (
            "You are supporting a Marketing Analyst. Optimize for measurement quality, reporting clarity, "
            "budget allocation decisions, and practical next steps the analyst can implement."
        ),
    },
    "brand_manager": {
        "label": "Brand Manager",
        "decision_horizon": "campaign planning + messaging/positioning + brand risk management",
        "primary_outputs": [
            "what changed + why it matters to brand perception",
            "positioning/messaging implications + creative direction",
            "brand risks (adjacency, trust, policy) + guardrails",
            "7-day + 30-day actions (briefs, comms, experiments, monitoring)",
        ],
        "focus_prompt": (
            "You are supporting a Brand Manager. Optimize for positioning, messaging architecture, creative direction, "
            "brand risk/opportunity, and concrete briefing guidance."
        ),
    },
    "other": {
        "label": "Other",
        "decision_horizon": "pragmatic cross-functional marketing planning",
        "primary_outputs": [
            "what changed + executive-ready summary",
            "who it impacts + what to do next",
            "risks/assumptions + KPIs to watch",
        ],
        "focus_prompt": (
            "You are supporting a cross-functional marketing stakeholder. Optimize for clarity, plausibility, "
            "and actionability without over-specializing."
        ),
    },
}


def _safe_request_id(exc: Exception) -> str:
    # anthropic errors sometimes expose request_id, but shape can vary by version
    return str(getattr(exc, "request_id", "") or "")


def _is_retryable_error(exc: Exception) -> bool:
    # Different anthropic SDK versions expose different exception types.
    maybe_retryable_types = [
        getattr(anthropic, "InternalServerError", None),
        getattr(anthropic, "RateLimitError", None),
        getattr(anthropic, "APIConnectionError", None),
        getattr(anthropic, "APITimeoutError", None),
        getattr(anthropic, "OverloadedError", None),
    ]
    retryable_types = tuple(t for t in maybe_retryable_types if t is not None)

    if retryable_types and isinstance(exc, retryable_types):
        return True

    # Fallback: treat specific status codes as retryable even if the SDK
    # doesn't provide a dedicated exception class.
    status_code = getattr(exc, "status_code", None)
    return isinstance(status_code, int) and (
        status_code >= 500 or status_code in (429, 529)
    )


def _backoff_sleep_s(*, attempt_idx: int, base_sleep_s: float) -> float:
    # Exponential backoff with jitter (cap to keep CI reasonable)
    return min(60.0, base_sleep_s * (2**attempt_idx)) * (0.75 + random.random() * 0.5)


def _maybe_wait_for_rate_limit(*, input_tokens: int) -> None:
    """
    This script sometimes sends a large web-search prompt. Some Anthropic accounts
    can hit short-window token caps. Waiting is a cheap way to reduce flaky runs.
    """
    # Heuristic: only wait when we used a lot of input tokens.
    if isinstance(input_tokens, int) and input_tokens >= 18_000:
        print("    waiting 65s for rate limit window to reset...")
        time.sleep(65)


def create_message_with_retries(*, attempts: int = 6, base_sleep_s: float = 2.0, **kwargs):
    """
    Anthropic occasionally returns transient 5xx / overloaded errors.
    CI should retry those instead of failing the run.
    """
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            return client.messages.create(**kwargs)
        except Exception as exc:
            last_exc = exc

            retryable = _is_retryable_error(exc)
            is_last_attempt = i == attempts - 1

            if (not retryable) or is_last_attempt:
                rid = _safe_request_id(exc)
                if rid:
                    print(f"    request_id: {rid}")
                raise

            sleep_s = _backoff_sleep_s(attempt_idx=i, base_sleep_s=base_sleep_s)
            rid = _safe_request_id(exc)
            msg = str(exc)
            if rid:
                msg = f"{msg} (request_id: {rid})"
            print(f"    transient error, retrying in {sleep_s:.1f}s: {msg}")
            time.sleep(sleep_s)

    # Should be unreachable, but keep mypy happy.
    raise last_exc if last_exc else RuntimeError("message create failed unexpectedly")


parser = argparse.ArgumentParser(description="Fetch daily marketing/brand intelligence and append to data.json.")
parser.add_argument(
    "--role",
    default=os.getenv("MARKETING_ROLE", "marketing_analyst"),
    help="One of: marketing_analyst | brand_manager | other (can also set MARKETING_ROLE).",
)
args = parser.parse_args()

role_key = _normalize_role(args.role)
role_profile = ROLE_PROFILES[role_key]
role_label = str(role_profile["label"])
role_focus_prompt = str(role_profile["focus_prompt"])

print(f"Role: {role_label}")


# --- Step 1: Search for latest marketing/brand intelligence ---
print(f"[1/2] Searching for marketing & brand intelligence on {current_date}...")

search_response = create_message_with_retries(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": f"""Today is {current_date}.

{role_focus_prompt}

Task:
1) Find 3-6 candidate developments from reputable sources published recently (ideally today, otherwise within the last 7 days).
2) Each candidate must clearly fit ONE category:
   - platform_change (major ad platform / privacy / measurement change)
   - competitor_campaign (competitor or category-leading campaign / repositioning / partnership)
   - consumer_trend (consumer/cultural trend with clear brand implications)
   - regulation (regulation or policy change affecting marketing)
3) Then pick the single most actionable candidate for a {role_label}.

Output requirements:
- Provide a short list of candidates with: headline, category, 1-sentence why it matters for the role, and source URL.
- Then provide a final selected development with a 5-8 sentence intel summary.
- Include only claims that are supported by the sources.
""",
        }
    ],
    tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
)

s1_in = search_response.usage.input_tokens
s1_out = search_response.usage.output_tokens
s1_cost = calc_cost(s1_in, s1_out)
total_cost += s1_cost
print(f"    done. tokens: {s1_in} in / {s1_out} out  |  cost: ${s1_cost:.4f}")

raw_intel = " ".join(
    block.text for block in search_response.content if block.type == "text"
)
print(f"    extracted {len(raw_intel)} chars of intel text")

# Extract URLs from web search result blocks
source_urls = []
for block in search_response.content:
    if block.type == "web_search_tool_result":
        for result in block.content:
            if hasattr(result, "url") and result.url:
                source_urls.append(f"- {result.title}: {result.url}")

print(f"    found {len(source_urls)} source URLs")
sources_section = "\n".join(source_urls) if source_urls else "(none found)"

_maybe_wait_for_rate_limit(input_tokens=s1_in)

# --- Step 2: Filter and format into JSON schema ---
print("[2/2] Filtering and formatting into JSON schema...")

filter_response = create_message_with_retries(
    model="claude-opus-4-6",
    max_tokens=3072,
    messages=[
        {
            "role": "user",
            "content": f"""You are producing a real-world work product for a {role_label}.

Given the following marketing/brand intelligence summary, extract the single most actionable development that fits one of these categories:

1) platform_change (major ad platform / privacy / measurement change)
2) competitor_campaign (competitor or category-leading campaign / repositioning / partnership)
3) consumer_trend (consumer/cultural trend with clear brand implications)
4) regulation (regulation or policy change affecting marketing)

Intel summary:
{raw_intel}

Available source URLs (use the most relevant one exactly as written):
{sources_section}

Return only developments that are clearly supported by the intel summary and have a plausible matching source URL.

If there are no clearly relevant developments, return an empty JSON object: {{}}

Otherwise return ONLY a valid JSON object in exactly this format (no extra text, no markdown). Include EXACTLY 1 item in the array for "{current_year}".

Constraints:
- Keep every string factual and defensible based on the intel summary.
- Make recommended actions concrete (what, who, when).
- Use measurement triangulation language where relevant: attribution vs incrementality tests vs MMM (marketing mix modeling).

Schema (keep existing fields for backwards compatibility; additional fields are allowed and encouraged):
{{
  "{current_year}": [
    {{
      "event": "<short headline (max ~10 words)>",
      "category": "<one of: platform_change | competitor_campaign | consumer_trend | regulation>",
      "description": "<2-3 sentences describing what happened and why it matters>",
      "analyst_take": "<1-2 sentences: what to measure, what to watch, how it affects reporting/budget>",
      "brand_take": "<1-2 sentences: implications for positioning/messaging/creative or brand risk>",
      "recommended_actions": [
        "<bullet-like action 1>",
        "<bullet-like action 2>",
        "<bullet-like action 3>"
      ],
      "who_it_impacts": [
        "<e.g. Performance Marketing>",
        "<e.g. Brand/Comms>",
        "<e.g. Analytics/BI>",
        "<e.g. Legal/Compliance>"
      ],
      "kpis_to_watch": [
        "<KPI 1>",
        "<KPI 2>",
        "<KPI 3>"
      ],
      "expected_directional_impact": {{
        "awareness": "<up/down/unclear + 5-12 words why>",
        "conversion": "<up/down/unclear + 5-12 words why>",
        "cac_or_cpa": "<up/down/unclear + 5-12 words why>",
        "measurement_confidence": "<up/down/unclear + 5-12 words why>"
      }},
      "next_7_days": [
        "<smallest next steps that can start this week>"
      ],
      "next_30_days": [
        "<steps that require planning/coordination>"
      ],
      "assumptions_and_risks": [
        "<assumption/risk + mitigation>"
      ],
      "confidence": "<low|medium|high>",
      "role_primary": "{role_label}",
      "source": "<URL of the most relevant source article>",
      "date": "{current_date}"
    }}
  ]
}}""",
        }
    ],
)

s2_in = filter_response.usage.input_tokens
s2_out = filter_response.usage.output_tokens
s2_cost = calc_cost(s2_in, s2_out)
total_cost += s2_cost
print(f"    done. tokens: {s2_in} in / {s2_out} out  |  cost: ${s2_cost:.4f}")

print(f"\n    total cost this run: ${total_cost:.4f}")

output = " ".join(
    block.text for block in filter_response.content if block.type == "text"
).strip()

# Strip markdown code fences if model wraps output in ```json ... ```
output = re.sub(r"^```[a-z]*\n?", "", output).rstrip("`").strip()

# Validate and pretty-print JSON
print("\n--- Result ---")
try:
    def _try_parse_json(s: str) -> dict:
        return json.loads(s)

    try:
        parsed = _try_parse_json(output)
    except json.JSONDecodeError:
        # Recovery: if the model output was cut off, trim to the last complete JSON object.
        start = output.find("{")
        end = output.rfind("}")
        if start != -1 and end != -1 and end > start:
            trimmed = output[start : end + 1].strip()
            parsed = _try_parse_json(trimmed)
        else:
            raise

    # Write output JSON into the repo data files so CI doesn't need to scrape stdout.
    repo_root = Path(__file__).resolve().parents[1]
    targets = [
        repo_root / "marketing-data" / "data.json",
        repo_root / "timeline" / "public" / "marketing-data.json",
    ]

    # Merge new year entry into existing JSON (so we don't wipe historical data).
    primary = targets[0]
    existing = {}
    if primary.exists():
        try:
            loaded = json.loads(primary.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except json.JSONDecodeError:
            existing = {}

    def _event_key(e: dict) -> tuple[str, str, str]:
        # De-dupe within a year by (event, date, source). Keep it simple + stable.
        return (
            str(e.get("event", "")).strip(),
            str(e.get("date", "")).strip(),
            str(e.get("source", "")).strip(),
        )

    if isinstance(parsed, dict):
        for year, new_value in parsed.items():
            if year not in existing:
                existing[year] = []

            # Normalize existing[year] -> list[dict]
            if isinstance(existing.get(year), dict):
                existing[year] = [existing[year]]
            elif not isinstance(existing.get(year), list):
                existing[year] = []

            # Normalize new_value -> list[dict]
            if isinstance(new_value, dict):
                new_events = [new_value]
            elif isinstance(new_value, list):
                new_events = [e for e in new_value if isinstance(e, dict)]
            else:
                new_events = []

            existing_keys = {_event_key(e) for e in existing[year] if isinstance(e, dict)}
            for e in new_events:
                if _event_key(e) not in existing_keys:
                    existing[year].append(e)
                    existing_keys.add(_event_key(e))

    formatted = json.dumps(existing, ensure_ascii=False, indent=2) + "\n"
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(formatted, encoding="utf-8")

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
except json.JSONDecodeError:
    print("(could not parse as JSON)")
    print(output)

