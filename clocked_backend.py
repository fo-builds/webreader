"""Optional Clocked backend (https://clocked.rezolve.ai): verbatim extraction with
source positions and confidence. Enabled when CLOCKED_API_KEY is set; returns None
otherwise so the bot falls back to local parsing."""
import os

def extract_fields(text, fields, timeout=60):
    key = os.environ.get("CLOCKED_API_KEY")
    if not key or not text:
        return None
    try:
        from clocked_sdk import Clocked
        with Clocked(api_key=key, timeout=timeout) as c:
            r = c.extract(text=text[:20000], fields=fields)
            data = r.data if hasattr(r, "data") else r
            out = {}
            for k, v in (data.get("fields") or {}).items():
                out[k] = {"value": v.get("value"), "confidence": v.get("confidence")}
            return out
    except Exception:
        return None
