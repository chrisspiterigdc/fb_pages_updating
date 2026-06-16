#!/usr/bin/env python3
"""
Daily content generator for freebets.com.
Checks the day and prints the task for Claude to execute via MCP connectors.

Usage:
    python generate_content.py          # uses today's date
    python generate_content.py tuesday  # force a specific day (for testing)
    python generate_content.py monday   # force any day

No API keys or tokens required — Claude handles all external calls via MCP.
"""

import sys
from datetime import datetime

SLACK_CHANNEL = "C0BATCW8K46"
SLOT_REVIEW_COUNT = 7

# Tasks run every day unless overridden by a day-specific entry.
# Day-specific tasks run IN ADDITION to the daily task.
DAILY_TASK = {"type": "daily_offer"}

DAY_SCHEDULE = {
    "tuesday": {"type": "slot_reviews"},
    # Add more day-specific tasks here, e.g.:
    # "wednesday": {
    #     "type": "seo_page",
    #     "page": "Casino Welcome Bonuses",
    #     "url_slug": "/casino-welcome-bonuses/",
    # },
}

OFFER_PARAGRAPH_EXAMPLE = """
Today's Best Free Bet Offer
The Tote has been at the heart of British racing for over 90 years, and today new customers can take advantage of a cracking welcome deal: Bet £10 and Get £40 in Free Bets.

To qualify, register a new account, deposit and place a £10 qualifying bet at minimum odds of 1/1 (2.0). Use code B10G40 on registration. £20 in Tote Credit, a £10 Free Sports Bet and two £5 Football Acca tokens will be credited within 48 hours of your qualifying bet settling.

The free bets can be used across racing, football and other sport and with the tote's unique pool betting markets, there's always the chance of a bigger return when the pools are running hot.

Today is a brilliant day to get involved. York hosts one of the jewels in the June flat racing calendar, the Mid-Summer Raceday, a quality card and the perfect warm-up before Royal Ascot thunders into view next week.

Come evening, it's all about the World Cup. Canada take on Bosnia-Herzegovina in the Group Stage (around 8pm BST), with USA facing Paraguay for a high-profile night fixture. Goals, drama and plenty of betting angles to explore.

The tote is the natural home for racing fans thanks to its exclusive pool markets, including the legendary Placepot but with World Cup football stacked on top, this offer works for everyone.
"""

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


def print_daily_offer_task(date_str: str) -> None:
    print("=" * 60)
    print("TASK: Daily best offer paragraph")
    print(f"DATE: {date_str}")
    print(f"SLACK_CHANNEL: {SLACK_CHANNEL}")
    print()
    print("INSTRUCTIONS:")
    print("1. Use WebSearch to find the current #1 offer on freebets.com.")
    print("   Search query: 'site:freebets.com best free bet offer today 2026'")
    print("   Also try: 'freebets.com homepage number 1 offer [current month] 2026'")
    print("   Identify: bookmaker name, offer headline, key terms (min bet, odds, code, credit breakdown).")
    print()
    print("2. Use WebSearch to find today's major sports events (UK focus).")
    print("   Search query: 'UK sport today [date] football racing cricket tennis'")
    print("   Pick 1-2 events most relevant to the bookmaker's offer.")
    print()
    print("3. Write the offer paragraph following the STYLE GUIDE below.")
    print("   Do NOT invent offer terms — only use what you verified in step 1.")
    print()
    print("4. Run The Humanizer on the paragraph before posting.")
    print()
    print(f"5. Post to Slack channel {SLACK_CHANNEL} with header:")
    print("   ':moneybag: *Today's Best Free Bet Offer*'")
    print()
    print("NOTE: WebFetch is blocked — use WebSearch only.")
    print()
    print("STYLE GUIDE:")
    print("- Open with the bookmaker name and a brief brand/context line (one sentence).")
    print("- State the offer headline clearly in the first paragraph.")
    print("- Second paragraph: qualifying terms — min bet, min odds, promo code if any, how/when credit lands.")
    print("- Third paragraph: what the free bets cover and any standout product feature.")
    print("- Fourth/fifth paragraph: today's sports context — 1-2 specific events, times, why they're relevant to the offer.")
    print("- Close with one sentence tying the offer back to today's action.")
    print("- Tone: warm, knowledgeable, UK English. Not salesy. Like a racing tipster recommending something to a mate.")
    print("- Length: 5-6 short paragraphs, similar to the example below.")
    print("- No guarantee-of-winning language. No superlatives like 'best ever' or 'incredible'.")
    print()
    print("EXAMPLE OUTPUT (style reference only — do not copy the offer details):")
    print(OFFER_PARAGRAPH_EXAMPLE)


def print_slot_reviews_task(date_str: str) -> None:
    print("=" * 60)
    print("TASK: Tuesday slot reviews")
    print(f"DATE: {date_str}")
    print(f"SLACK_CHANNEL: {SLACK_CHANNEL}")
    print(f"SLOT_COUNT: {SLOT_REVIEW_COUNT}")
    print()
    print("INSTRUCTIONS:")
    print(f"1. Use WebSearch (not WebFetch) to find the {SLOT_REVIEW_COUNT} most recently reviewed slot games on bigwinboard.com.")
    print("   Search query: 'site:bigwinboard.com new slot review 2026'")
    print("2. For each game, run 1-2 targeted WebSearch queries:")
    print("   '[Game name] [Developer] slot RTP volatility max win grid features 2026'")
    print("   '[Game name] [Developer] slot free spins buy options mechanics'")
    print("   Use only figures that appear consistently across multiple sources.")
    print("3. Write a content block for each game using the template below.")
    print("4. Run The Humanizer on each block.")
    print(f"5. Post all {SLOT_REVIEW_COUNT} blocks to Slack channel {SLACK_CHANNEL}.")
    print("   First game as parent message, remaining 6 as thread replies.")
    print("   Parent message header: ':slot_machine: *Tuesday Slots Content — 7 New Games*\\nSection: *Where to Spend Your Slots Welcome Bonus?*'")
    print("NOTE: WebFetch is blocked — use WebSearch only.")
    print()
    print("CONTENT TEMPLATE:")
    print(SLOT_CONTENT_TEMPLATE)


def main() -> None:
    day = get_day(sys.argv[1] if len(sys.argv) > 1 else None)
    date_str = datetime.now().strftime("%d %B %Y")

    # Daily offer task runs every day
    print_daily_offer_task(date_str)

    # Day-specific task runs on top if scheduled
    if day in DAY_SCHEDULE:
        print()
        task = DAY_SCHEDULE[day]
        if task["type"] == "slot_reviews":
            print_slot_reviews_task(date_str)


if __name__ == "__main__":
    main()
