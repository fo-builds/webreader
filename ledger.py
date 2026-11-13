"""Pay-per-use usage ledger on NEAR testnet. Each metered feature call gets a
signed function-call transaction to a ledger contract, so usage is verifiable
on-chain. Enabled when NEAR_LEDGER_KEY is set (an NEAR testnet secret key) and
NEAR_LEDGER_ACCOUNT names the signer; NEAR_LEDGER_CONTRACT the target contract
(defaults to status_message.testnet, a public example contract). Falls back to a
local JSONL ledger when signing is unavailable, so the bot never blocks on it."""
import json, os, time

LOCAL_LEDGER = os.environ.get("NEAR_LEDGER_FILE", "usage_ledger.jsonl")

def _local_log(entry):
    with open(LOCAL_LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def meter(feature, detail=""):
    entry = {"ts": int(time.time()), "feature": feature, "detail": detail[:200],
             "account": os.environ.get("NEAR_LEDGER_ACCOUNT", "local")}
    key = os.environ.get("NEAR_LEDGER_KEY")
    contract = os.environ.get("NEAR_LEDGER_CONTRACT", "status_message.testnet")
    if not key:
        return _local_log(entry)
    try:
        from near_api import Account  # optional; near-api-py
        acc = Account(os.environ.get("NEAR_RPC", "https://rpc.testnet.near.org"), os.environ.get("NEAR_LEDGER_ACCOUNT"), key)
        tx = acc.sign_and_submit_tx([{"type": "FunctionCall", "method_name": "set_status",
            "args": {"message": f"webreader:{feature}:{detail[:80]}"}, "gas": 30000000000000,
            "deposit": 0}], contract)
        entry["tx"] = str(getattr(tx, "transaction_hash", tx))[:100]
        entry["on_chain"] = True
        return _local_log(entry)
    except Exception as e:
        entry["local_fallback"] = repr(e)[:120]
        return _local_log(entry)
