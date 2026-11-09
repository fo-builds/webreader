"""Fetch a URL and return clean readable text, title, and links."""
import requests, trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def fetch(url, timeout=25):
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if "pdf" in ctype:
        return {"title": url.rsplit("/", 1)[-1], "text": None, "links": [], "pdf_bytes": r.content, "url": r.url}
    html = r.text
    text = trafilatura.extract(html, include_links=False, favor_recall=True) or ""
    doc = trafilatura.extract_metadata(html)
    title = (doc.title if doc and doc.title else "")
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True)[:400]:
        absu = urljoin(r.url, a["href"].strip())
        if absu.startswith(("http://", "https://")) and absu not in seen:
            seen.add(absu)
            label = " ".join(a.get_text().split())[:120]
            links.append((label, absu))
    return {"title": title or r.url, "text": text, "links": links, "pdf_bytes": None, "url": r.url}
