#!/usr/bin/env python3
"""
Daily content generator for freebets.com.
Checks the day and prints the task for Claude to execute via MCP connectors.

Usage:
    python generate_content.py          # uses today's date
    python generate_content.py tuesday  # force a specific day (for testing)

No API keys or tokens required — Claude handles all external calls via MCP.
"""

import sys
from datetime import datetime

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

SLOT_CONTENT_TEMPLATE = """Each entry must follow this exact format:

<h3>[Game Name]: [Developer] (Released [Month Year])</h3>

[One sentence: volatility, developer, theme, and the two or three core mechanics.]

[Stat block: grid, ways/paylines, RTP options, volatility, max win, bet range.]

[Mechanic paragraphs — longest section. Explain each mechanic specifically with numbers.]

[Trigger paragraph: how bonus/free spins trigger, how many spins, retrigger rules.]

[Buy options paragraph: each option with its cost in x-stake.]

All features are subject to the full game rules and paytable.

Rules:
- UK English
- No em dashes (use commas, colons, or periods)
- No hollow intensifiers (significantly, incredibly, essentially)
- Active voice openers only
- Vary paragraph lengths
- Accurate numbers and mechanics only
- No guarantee-of-winning language"""


def get_day(override: str | None = None) -> str:
    if override:
        return override.lower()
    return datetime.now().strftime("%A").lower()


def main() -> None:
    day = get_day(sys.argv[1] if len(sys.argv) > 1 else None)

    if day not in CONTENT_SCHEDULE:
        print(f"No content scheduled for {day.capitalize()}. Nothing to do.")
        return

    task = CONTENT_SCHEDULE[day]

    if task["type"] == "slot_reviews":
        print(f"TASK: Tuesday slot reviews")
        print(f"DATE: {datetime.now().strftime('%d %B %Y')}")
        print(f"SLACK_CHANNEL: {SLACK_CHANNEL}")
        print(f"SLOT_COUNT: {SLOT_REVIEW_COUNT}")
        print()
        print("INSTRUCTIONS:")
        print(f"1. Use WebSearch (not WebFetch) to find the {SLOT_REVIEW_COUNT} most recently reviewed slot games on bigwinboard.com.")
        print("   Search query: 'site:bigwinboard.com new slot review 2026' — use the results to identify the latest titles.")
        print("2. For each game, run 1-2 targeted WebSearch queries to find accurate stats:")
        print("   '[Game name] [Developer] slot RTP volatility max win grid features 2026'")
        print("   '[Game name] [Developer] slot free spins buy options mechanics'")
        print("   Use only figures that appear consistently across multiple sources. Skip any stat you cannot verify.")
        print("3. Write a content block for each game using the template below.")
        print("4. Run The Humanizer on each block (scan for AI patterns, rewrite to remove them).")
        print(f"5. Post all {SLOT_REVIEW_COUNT} blocks to Slack channel {SLACK_CHANNEL} — first game as the parent message, remaining games as thread replies.")
        print("6. Parent message header: ':slot_machine: *Tuesday Slots Content — 7 New Games*\\nSection: *Where to Spend Your Slots Welcome Bonus?*'")
        print("NOTE: Do not use WebFetch — it is blocked in this environment. WebSearch only.")
        print()
        print("CONTENT TEMPLATE:")
        print(SLOT_CONTENT_TEMPLATE)


if __name__ == "__main__":
    main()
