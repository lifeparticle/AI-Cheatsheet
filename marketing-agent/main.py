import os
import json
import re
import time
import random
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


# --- Step 1: Search for latest marketing/brand intelligence ---
print(f"[1/2] Searching for marketing & brand intelligence on {current_date}...")

search_response = create_message_with_retries(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": f"""Search for the most impactful marketing/brand development today ({current_date}) that would matter to:
- a Marketing Analyst (measurement, channel/platform changes, budget allocation, reporting)
- a Brand Manager (positioning, messaging, creative direction, brand risk/opportunity)

Prioritize one of these categories (pick the single strongest):
1) Major ad platform / privacy / measurement change (Google/Meta/TikTok/Amazon/Apple, etc.)
2) Competitor or category-leading brand campaign / repositioning / partnership
3) Consumer/cultural trend with clear brand implications
4) Regulation or policy change affecting marketing (ads, data, disclosures)

Return a concise summary plus the most relevant source URLs."""
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

# Rate limit: 30k input tokens/minute. Call 1 may exceed that, so wait.
print("    waiting 65s for rate limit window to reset...")
time.sleep(65)

# --- Step 2: Filter and format into JSON schema ---
print("[2/2] Filtering and formatting into JSON schema...")

filter_response = create_message_with_retries(
    model="claude-opus-4-6",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": f"""Given the following marketing/brand intelligence summary, extract the single most actionable development that fits one of these categories:

1) Major ad platform / privacy / measurement change
2) Competitor or category-leading campaign / repositioning / partnership
3) Consumer/cultural trend with clear brand implications
4) Regulation or policy change affecting marketing

Intel summary:
{raw_intel}

Available source URLs (use the most relevant one exactly as written):
{sources_section}

If there is no clearly relevant development, return an empty JSON object: {{}}

Otherwise return ONLY a valid JSON object in exactly this format, with no extra text or markdown:
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
    parsed = json.loads(output)

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

