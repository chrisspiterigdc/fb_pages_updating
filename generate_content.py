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
from datetime import datetime
import anthropic
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_CHANNEL = "C0BATCW8K46"

# Map each weekday to a content task.
# Add new days/pages here as you expand.
CONTENT_SCHEDULE = {
    "tuesday": {
        "page": "Slots Bonuses",
        "url_slug": "/slots-bonuses/",
        "description": (
            "A page on freebets.com that lists and reviews the best slots bonuses "
            "available to UK players, including free spins, deposit match bonuses, "
            "and no-deposit slots offers from top UK-licensed casinos."
        ),
        "target_keywords": [
            "slots bonuses",
            "slots bonus UK",
            "free spins bonus",
            "best slots bonuses",
            "online slots offers",
        ],
    },
    # Example — uncomment and fill in to add more days:
    # "wednesday": {
    #     "page": "Casino Welcome Bonuses",
    #     "url_slug": "/casino-welcome-bonuses/",
    #     "description": "...",
    #     "target_keywords": [...],
    # },
}


def get_day(override: str | None = None) -> str:
    if override:
        return override.lower()
    return datetime.now().strftime("%A").lower()


def build_prompt(task: dict) -> str:
    keywords = ", ".join(task["target_keywords"])
    return f"""You are an expert SEO copywriter for freebets.com, a UK-focused comparison site for betting and casino bonuses.

Write SEO-optimised page copy for the following page:

Page title target: {task["page"]}
URL: https://www.freebets.com{task["url_slug"]}
Page purpose: {task["description"]}
Target keywords: {keywords}

Please produce:

1. **SEO Title** (50–60 characters, include primary keyword)
2. **Meta Description** (140–155 characters, compelling, include primary keyword)
3. **H1 Heading** (clear, keyword-rich)
4. **Intro paragraph** (2–3 sentences, hooks the reader, naturally includes primary keyword)
5. **Main body copy** (3–4 short paragraphs covering: what the bonus type is, what to look for, how freebets.com helps players find the best offers)
6. **CTA sentence** (one line encouraging users to browse the listings)

Tone: friendly, authoritative, UK English. Avoid overly promotional language. All gambling references should follow UK responsible gambling guidelines (no guarantees of winning, no targeting vulnerable groups).
"""


def generate_content(task: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": build_prompt(task)}],
    )
    return message.content[0].text


def post_to_slack(content: str, task: dict, day: str) -> None:
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    header = (
        f":pencil: *Daily SEO Content — {day.capitalize()}*\n"
        f"Page: *{task['page']}* (`{task['url_slug']}`)\n"
        f"{'─' * 40}\n"
    )
    try:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=header + content,
            mrkdwn=True,
        )
        print(f"Posted to Slack channel {SLACK_CHANNEL}")
    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
        raise


def main() -> None:
    day = get_day(sys.argv[1] if len(sys.argv) > 1 else None)

    if day not in CONTENT_SCHEDULE:
        print(f"No content scheduled for {day.capitalize()}. Nothing to do.")
        return

    task = CONTENT_SCHEDULE[day]
    print(f"Generating SEO copy for '{task['page']}' ({day.capitalize()})...")

    content = generate_content(task)
    print("Content generated. Posting to Slack...")
    post_to_slack(content, task, day)
    print("Done.")


if __name__ == "__main__":
    main()
