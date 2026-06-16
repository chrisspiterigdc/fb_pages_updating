#!/usr/bin/env python3
"""
Daily content generator for freebets.com.
Generates SEO page copy based on the day of the week and posts it to Slack.

Usage:
    python generate_content.py          # uses today's date
    python generate_content.py tuesday  # force a specific day (for testing)

Required env vars:
    ANTHROPIC_API_KEY   - Claude API key
    SLACK_BOT_TOKEN     - Slack bot OAuth token (xoxb-...)
"""

import os
import sys
import json
import time
from datetime import datetime
import anthropic
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_CHANNEL = "C0BATCW8K46"

SLOT_REVIEW_COUNT = 7

CONTENT_SCHEDULE = {
    "tuesday": {"type": "slot_reviews"},
    # Add more days here, e.g.:
    # "wednesday": {
    #     "type": "seo_page",
    #     "page": "Casino Welcome Bonuses",
    #     "url_slug": "/casino-welcome-bonuses/",
    #     "description": "...",
    #     "target_keywords": [...],
    # },
}

SLOT_CONTENT_TEMPLATE = """You are writing technical slot game descriptions for the page freebets.com/slots-bonuses/, in a section called "Where to Spend Your Slots Welcome Bonus?"

Each entry follows this exact format — match it precisely:

<h3>[Game Name]: [Developer] (Released [Month Year])</h3>

[One sentence: volatility, developer, theme, and the two or three core mechanics that define the game.]

[Stat block sentence: grid, ways/paylines, RTP, volatility label, max win, bet range.]

[Mechanic paragraph(s): explain each core mechanic in plain language. Be specific about how they interact. Use numbers wherever possible.]

[Trigger paragraph: how the bonus/free spins are triggered, how many spins, any retrigger rules.]

[Buy options paragraph: list each buy option with its cost in x-stake.]

All features are subject to the full game rules and paytable.

Rules:
- UK English throughout
- No em dashes (use commas, colons, or periods instead)
- No hollow intensifiers (significantly, incredibly, essentially)
- No passive openers ("X options are available" → "The game carries X options")
- No AI filler phrases
- Vary paragraph lengths — the mechanic paragraph should be the longest
- All numbers and mechanics must be accurate
- Responsible gambling: no guarantee of winning language
"""

HUMANIZER_SYSTEM = """You are a content editor specialised in removing AI-generated texture from slot game technical descriptions.

Review the content and rewrite any passages that contain:
- Passive voice openers (fix to active)
- Hollow intensifiers: significantly, incredibly, essentially, various, typically
- Contrast negations ("Rather than X, it does Y" — rewrite as direct positive statement)
- Redundant adjective pairs (premium enhanced, fully comprehensive)
- Uniform paragraph lengths (vary them)
- Any em dashes (replace with comma, colon, or period)

Do not change any facts, numbers, or game mechanics.
Do not add ideas not in the original.
Return only the corrected content with no commentary."""


def get_day(override: str | None = None) -> str:
    if override:
        return override.lower()
    return datetime.now().strftime("%A").lower()


def find_latest_slots() -> list[dict]:
    """Use Claude with web_search to find the 7 most recent slots on BigWinBoard."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"  Searching BigWinBoard for latest {SLOT_REVIEW_COUNT} slots...")

    messages = [
        {
            "role": "user",
            "content": (
                f"Go to bigwinboard.com and find the {SLOT_REVIEW_COUNT} most recently reviewed slot games. "
                "For each game return a JSON array with objects containing: "
                '"name" (game title), "developer" (studio name), "url" (bigwinboard review URL). '
                "Return only the JSON array, no other text."
            ),
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
        messages=messages,
    )

    # Extract the final text response
    for block in reversed(response.content):
        if block.type == "text":
            text = block.text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            try:
                return json.loads(text.strip())
            except json.JSONDecodeError:
                pass

    raise RuntimeError("Could not parse slot list from search response")


def research_and_write_slot(game: dict) -> str:
    """Research a single slot game and write its content block."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"  Writing: {game['name']} ({game['developer']})...")

    messages = [
        {
            "role": "user",
            "content": (
                f"Research the slot game '{game['name']}' by {game['developer']} using web search. "
                f"Find its grid, ways/paylines, RTP options, volatility, max win, bet range, "
                f"all mechanics, free spins triggers, and feature buy options with costs. "
                f"Then write a content block for it following the template in your system prompt exactly. "
                f"Use the release month and year from your research."
            ),
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SLOT_CONTENT_TEMPLATE,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 6}],
        messages=messages,
    )

    for block in reversed(response.content):
        if block.type == "text":
            return block.text.strip()

    raise RuntimeError(f"No text response for {game['name']}")


def humanize(content: str) -> str:
    """Run a humanizer pass to strip AI texture."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=HUMANIZER_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text.strip()


def generate_slot_reviews() -> str:
    """Find 7 latest slots, write and humanize each, return combined content."""
    games = find_latest_slots()
    games = games[:SLOT_REVIEW_COUNT]

    blocks = []
    for i, game in enumerate(games, 1):
        print(f"  [{i}/{len(games)}] {game['name']}")
        raw = research_and_write_slot(game)
        clean = humanize(raw)
        blocks.append(clean)
        time.sleep(1)  # avoid rate limits

    return "\n\n" + "\n\n".join(blocks)


def post_to_slack(content: str, day: str, label: str) -> None:
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    header = (
        f":slot_machine: *Tuesday Slots Content — {SLOT_REVIEW_COUNT} New Games*\n"
        f"Section: *Where to Spend Your Slots Welcome Bonus?*\n"
        f"{'─' * 40}\n"
    )
    # Slack has a 40,000 char limit per message; split if needed
    full = header + content
    if len(full) > 39000:
        chunks = [full[i : i + 39000] for i in range(0, len(full), 39000)]
    else:
        chunks = [full]

    slack = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    thread_ts = None
    for chunk in chunks:
        try:
            resp = slack.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=chunk,
                mrkdwn=True,
                thread_ts=thread_ts,
            )
            if thread_ts is None:
                thread_ts = resp["ts"]
        except SlackApiError as e:
            print(f"Slack error: {e.response['error']}")
            raise

    print(f"Posted to Slack channel {SLACK_CHANNEL}")


def main() -> None:
    day = get_day(sys.argv[1] if len(sys.argv) > 1 else None)

    if day not in CONTENT_SCHEDULE:
        print(f"No content scheduled for {day.capitalize()}. Nothing to do.")
        return

    task = CONTENT_SCHEDULE[day]

    if task["type"] == "slot_reviews":
        print(f"Tuesday: generating {SLOT_REVIEW_COUNT} slot reviews from BigWinBoard...")
        content = generate_slot_reviews()
        print("All reviews written. Posting to Slack...")
        post_to_slack(content, day, "slot_reviews")

    print("Done.")


if __name__ == "__main__":
    main()
