# webreader

Telegram web-reader feature for a study bot: send a link, get clean readable
text, the page's links, or a PDF; `/search <query>` runs keyless web search
via DuckDuckGo's HTML endpoint.

Files:
- `bot_webreader.py` - Telethon event loop wiring the features to chat commands
- `reader.py` - fetch a URL and return clean readable text, title, links (trafilatura)
- `pdf.py` - render plain text into a simple PDF (reportlab)
- `search.py` - DuckDuckGo HTML web search

Telegram API credentials are read from `TG_API_ID` / `TG_API_HASH` env vars.

Built as the entry for the NEAR AI Agents hackathon, Nov 2026.
