# webreader

A Telegram web-reader bot: send a link, get clean readable text, the page's links, or a
PDF; search the web; summarize a page; pull named facts out of it.

## Commands (send to the bot in a private chat)

- **send any URL** -> clean readable text of the page (trafilatura), title first
- **`/pdf <url>`** -> the page's text rendered as a PDF you can download
- **`/links <url>`** -> the page's outgoing links, deduplicated, labels kept
- **`/search <query>`** -> keyless web search (DuckDuckGo HTML endpoint), top results
- **`/summarize <url> [n]`** -> n-bullet summary (default 5); uses NEAR AI Cloud
  inference when `NEAR_AI_KEY` is set, local extractive scorer otherwise
- **`/extract <url> field1 field2 ...`** -> verbatim values for named fields with
  confidence, via [Clocked](https://clocked.rezolve.ai) (exact-extraction model with
  source positions); enabled when `CLOCKED_API_KEY` is set

## Files

- `bot_webreader.py` - Telethon event loop wiring the features to chat commands
- `reader.py` - fetch a URL and return clean readable text, title, links (trafilatura)
- `pdf.py` - render plain text into a simple PDF (reportlab)
- `search.py` - DuckDuckGo HTML web search
- `summarize.py` - extractive summarizer; NEAR AI Cloud backend when keyed
- `clocked_backend.py` - Clocked exact-extraction backend (env-gated)

## Environment

Telegram API credentials are read from `TG_API_ID` / `TG_API_HASH` env vars.
Optional inference backends: `NEAR_AI_KEY` (NEAR AI Cloud), `CLOCKED_API_KEY` (Clocked).
Keep every key on the server; none belong in a repo or a client bundle.

## Credits

Clocked extraction credits on this bot come from the Clocked Build Challenge grant.

Built as the entry for the NEAR AI Agents hackathon, Nov 2026.
