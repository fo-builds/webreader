"""Keyless web search via DuckDuckGo's HTML endpoint."""
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def search(query, n=8):
    r = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=UA, timeout=25)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    out = []
    for res in soup.select("div.result")[:n]:
        a = res.select_one("a.result__a")
        sn = res.select_one("a.result__snippet")
        if a and a.get("href"):
            out.append({"title": a.get_text(" ", strip=True), "url": a["href"], "snippet": sn.get_text(" ", strip=True) if sn else ""})
    return out
