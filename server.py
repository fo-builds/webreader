"""HTTP API for webreader: browser access without Telegram or any client.

Endpoints (all GET):
  /read?url=...        -> JSON {title, text, links, url}
  /search?q=...        -> JSON {query, results:[{title,url,snippet}]}
  /summarize?url=&n=5  -> JSON {title, bullets}
  /pdf?url=...         -> application/pdf of the readable text
Zero new dependencies; reuses reader/search/summarize/pdf.
"""
import json, os, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from reader import fetch
from search import search as web_search
from summarize import summarize
from pdf import make_pdf

class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # quiet
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"), "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif u.path == "/read":
                r = fetch(q["url"][0])
                text = r["text"] or ""
                self._json({"title": r["title"], "text": text, "links": r["links"][:80], "url": r["url"],
                            "word_count": len(text.split())})
            elif u.path == "/search":
                self._json({"query": q["q"][0], "results": web_search(q["q"][0], int(q.get("n", ["8"])[0]))})
            elif u.path == "/summarize":
                r = fetch(q["url"][0])
                text = r["text"] or ""
                if not text:
                    return self._json({"error": "no readable text on that page", "title": r["title"], "url": r["url"]}, 422)
                bullets = summarize(text, n=int(q.get("n", ["5"])[0]))
                self._json({"title": r["title"], "bullets": bullets, "url": r["url"]})
            elif u.path == "/pdf":
                r = fetch(q["url"][0])
                text = r["text"] or ""
                if not text:
                    return self._json({"error": "no readable text on that page"}, 422)
                fd, path = tempfile.mkstemp(suffix=".pdf"); os.close(fd)
                make_pdf(r["title"], text, path)
                with open(path, "rb") as f:
                    data = f.read()
                os.unlink(path)
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", f'attachment; filename="webreader.pdf"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif u.path == "/health":
                self._json({"ok": True, "service": "webreader"})
            else:
                self._json({"error": "unknown endpoint", "endpoints": ["/read?url=", "/search?q=", "/summarize?url=&n=", "/pdf?url="]}, 404)
        except KeyError:
            self._json({"error": "missing url= or q= parameter"}, 400)
        except Exception as e:
            self._json({"error": str(e)}, 502)

if __name__ == "__main__":
    port = int(os.environ.get("PORT") or os.environ.get("WEBREADER_PORT") or "8017")
    print(f"webreader api on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
