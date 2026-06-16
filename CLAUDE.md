# freebets.com Content Project

## Writing Standard — MANDATORY

Every time Claude writes any content in this project, it MUST automatically run The Humanizer on it before presenting it to the user or sending it anywhere. No exceptions.

This is not optional and does not require the user to ask. The flow is always:
1. Generate draft
2. Run The Humanizer (full pipeline: AI pattern scan, originality check, score, rewrite)
3. Present only the humanized version

This applies to: SEO copy, blog content, Slack messages, emails, meta descriptions, headings, CTAs — any written output.

The Humanizer skill is at `.claude/commands/humanize.md`.
