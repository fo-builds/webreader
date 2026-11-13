"""Summarize fetched page text. Extractive baseline (no deps); optional NEAR AI Cloud
inference when NEAR_AI_KEY is set, with local fallback on any API failure."""
import os, re, json, urllib.request

def _sentences(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text.strip())

def summarize_local(text, n=5):
    sents = _sentences(text)
    if len(sents) <= n:
        return sents
    stop = set("a an the and or but of to in on for with is are was were be been it its this that as at by from not".split())
    freq = {}
    for s in sents:
        for w in re.findall(r"[a-z']+", s.lower()):
            if w not in stop and len(w) > 2:
                freq[w] = freq.get(w, 0) + 1
    scored = [(i, sum(freq.get(w, 0) for w in re.findall(r"[a-z']+", s.lower())) / (len(s.split()) + 1), s) for i, s in enumerate(sents)]
    top = sorted(sorted(scored, key=lambda x: -x[1])[:n], key=lambda x: x[0])
    return [s for _, _, s in top]

NEAR_URL = "https://inference.api.near.ai/v1/chat/completions"

def summarize_near(text, n=5, model="deepseek-ai/DeepSeek-R1-Distill-Llama-8B"):
    key = os.environ.get("NEAR_AI_KEY")
    if not key:
        return None
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": "Summarize the text into {n} crisp bullet points. Reply with only the bullets.".replace("{n}", str(n))},
        {"role": "user", "content": text[:12000]}], "max_tokens": 500, "temperature": 0.3}).encode()
    req = urllib.request.Request(NEAR_URL, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

def summarize(text, n=5):
    out = summarize_near(text, n)
    if out:
        return out, "near-ai"
    return summarize_local(text, n), "local"
