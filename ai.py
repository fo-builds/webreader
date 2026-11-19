"""AI layer: summarize extracted page text via the Cohere API (free trial key)."""
import os, json, urllib.request

def cohere_summarize(text, key=None, length="medium"):
    key = key or os.environ.get("COHERE_API_KEY", "")
    if not key:
        return {"error": "no COHERE_API_KEY set"}
    body = json.dumps({
        "model": "command-a-03-2025",
        "messages": [{"role": "user", "content":
            "Summarize the following article into 5 crisp bullet points, then one line on why it matters.\n\n" + text[:12000]}]
    }).encode()
    req = urllib.request.Request(
        "https://api.cohere.com/v2/chat", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.load(r)
    return {"summary": resp["message"]["content"][0]["text"]}

def cohere_chat(message, key=None):
    key = key or os.environ.get("COHERE_API_KEY", "")
    if not key:
        return {"error": "no COHERE_API_KEY set"}
    body = json.dumps({
        "model": "command-a-03-2025",
        "messages": [{"role": "user", "content": message}]
    }).encode()
    req = urllib.request.Request(
        "https://api.cohere.com/v2/chat", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.load(r)
    return {"answer": resp["message"]["content"][0]["text"]}
