"""Web-reader feature for the study bot: send a link, get clean text / links / PDF; /search for web search."""
import asyncio, os, sys, time, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telethon import TelegramClient, events
from reader import fetch
from pdf import make_pdf
from search import search as web_search

API_ID, API_HASH = int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"]
SESSION = sys.argv[1] if len(sys.argv) > 1 else "/workspace/tgstate/bot_session"
OUT = "/workspace/near-webreader/out"
os.makedirs(OUT, exist_ok=True)
URL_RE = re.compile(r'https?://\S+')

def chunk(text, n=3900):
    return [text[i:i+n] for i in range(0, len(text), n)]

def fmt(res, query):
    lines = [f"Search: {query}", ""]
    for i, r in enumerate(res, 1):
        lines.append(f"{i}. {r['title']}")
        if r['snippet']:
            lines.append(f"   {r['snippet'][:180]}")
        lines.append(f"   {r['url']}")
        lines.append("")
    return "\n".join(lines)

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handler(event):
        msg = event.message
        text = (msg.raw_text or "").strip()
        if not text:
            return
        low = text.lower()
        try:
            if low.startswith("/search"):
                q = text[7:].strip() or ""
                if not q:
                    await event.reply("send: /search <query>")
                    return
                res = await asyncio.to_thread(web_search, q)
                await event.reply(fmt(res, q)[:4000] if res else "No results.")
                return
            if low.startswith("/pdf"):
                m = URL_RE.search(text[4:] or "")
                if not m:
                    await event.reply("send: /pdf <url>")
                    return
                r = await asyncio.to_thread(fetch, m.group(0))
                path = os.path.join(OUT, f"page_{int(time.time())}.pdf")
                await asyncio.to_thread(make_pdf, r["title"], r["text"] or "(PDF or non-HTML page; no extractable text)", path)
                if r.get("pdf_bytes"):
                    await event.reply(file=io.BytesIO(r["pdf_bytes"]), force_document=True, attributes=[types.DocumentAttributeFilename(os.path.basename(r["url"]))])
                else:
                    await event.reply(file=path, force_document=True)
                return
            if low.startswith("/links"):
                m = URL_RE.search(text[6:] or "")
                if not m:
                    await event.reply("send: /links <url>")
                    return
                r = await asyncio.to_thread(fetch, m.group(0))
                body = "\n".join(f"{i}. {l or u}\n   {u}" for i, (l, u) in enumerate(r["links"][:25], 1))
                await event.reply(f"Links on {r['url']}\n\n{body}"[:4000] if body else "No links found.")
                return
            if low.startswith("/read") or URL_RE.search(text):
                m = URL_RE.search(text[5:] if low.startswith("/read") else text)
                if not m:
                    await event.reply("Send a link, or /search <query>, /pdf <url>, /links <url>.")
                    return
                r = await asyncio.to_thread(fetch, m.group(0))
                body = r["text"] or "No readable text found on that page."
                await event.reply(f"{r['title']}\n\n{body}"[:4000])
                return
        except Exception as e:
            await event.reply(f"That link failed: {type(e).__name__}: {str(e)[:200]}")

    print("webreader live", flush=True)
    await client.run_until_disconnected()

if __name__ == "__main__":
    import io
    from telethon.tl.types import DocumentAttributeFilename as types
    asyncio.run(main())
