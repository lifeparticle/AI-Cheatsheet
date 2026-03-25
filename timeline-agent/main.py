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
        "Missing ANTHROPIC_API_KEY. Set it in timeline-agent/.env and run again."
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

            # Different anthropic SDK versions expose different exception types.
            maybe_retryable_types = [
                getattr(anthropic, "InternalServerError", None),
                getattr(anthropic, "RateLimitError", None),
                getattr(anthropic, "APIConnectionError", None),
                getattr(anthropic, "APITimeoutError", None),
                getattr(anthropic, "OverloadedError", None),
            ]
            retryable_types = tuple(t for t in maybe_retryable_types if t is not None)

            retryable = isinstance(exc, retryable_types)

            # Fallback: treat specific status codes as retryable even if the SDK
            # doesn't provide a dedicated exception class.
            if not retryable:
                status_code = getattr(exc, "status_code", None)
                if isinstance(status_code, int) and (
                    status_code >= 500 or status_code in (429, 529)
                ):
                    retryable = True

            if not retryable or i == attempts - 1:
                rid = _safe_request_id(exc)
                if rid:
                    print(f"    request_id: {rid}")
                raise

            # Exponential backoff with jitter (cap to keep CI reasonable)
            sleep_s = min(60.0, base_sleep_s * (2**i)) * (0.75 + random.random() * 0.5)
            rid = _safe_request_id(exc)
            msg = str(exc)
            if rid:
                msg = f"{msg} (request_id: {rid})"
            print(f"    transient error, retrying in {sleep_s:.1f}s: {msg}")
            time.sleep(sleep_s)

    # Should be unreachable, but keep mypy happy.
    raise last_exc if last_exc else RuntimeError("message create failed unexpectedly")


# --- Step 1: Search for latest AI news ---
print(f"[1/2] Searching for AI news on {current_date}...")

search_response = create_message_with_retries(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": f"Search for the latest AI news today ({current_date}). Look for: new AI terminology or concepts, new AI product/model releases, and AI products or services being shut down or discontinued.",
        }
    ],
    tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
)

s1_in = search_response.usage.input_tokens
s1_out = search_response.usage.output_tokens
s1_cost = calc_cost(s1_in, s1_out)
total_cost += s1_cost
print(f"    done. tokens: {s1_in} in / {s1_out} out  |  cost: ${s1_cost:.4f}")

raw_news = " ".join(
    block.text for block in search_response.content if block.type == "text"
)
print(f"    extracted {len(raw_news)} chars of news text")

# Extract URLs from web search result blocks
source_urls = []
for block in search_response.content:
    if block.type == "web_search_tool_result":
        for result in block.content:
            if hasattr(result, "url") and result.url:
                source_urls.append(f"- {result.title}: {result.url}")

print(f"    found {len(source_urls)} source URLs")
sources_section = "\n".join(source_urls) if source_urls else "(none found)"

# Rate limit: 30k input tokens/minute. Call 1 likely exceeded that, so wait.
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
            "content": f"""Given the following AI news summary, extract the single most notable event that fits one of these three categories:

1. A new AI term or concept entering mainstream use (e.g. "vibe coding")
2. A major AI product or model release (e.g. GPT-5 launch)
3. An AI product, service, or company ending / being shut down (e.g. Sora app discontinuation)

News summary:
{raw_news}

Available source URLs (use the most relevant one exactly as written):
{sources_section}

Return ONLY a valid JSON object in exactly this format, with no extra text or markdown:
{{
  "{current_year}": {{
    "event": "<short title of the event>",
    "description": "<2-3 sentence description of what happened and why it matters>",
    "source": "<URL of the most relevant source article>",
    "date": "{current_date}"
  }}
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
        repo_root / "timeline-data" / "data.json",
        repo_root / "timeline" / "public" / "data.json",
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

    if isinstance(parsed, dict):
        existing.update(parsed)

    formatted = json.dumps(existing, ensure_ascii=False, indent=2) + "\n"
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(formatted, encoding="utf-8")

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
except json.JSONDecodeError:
    print("(could not parse as JSON)")
    print(output)
