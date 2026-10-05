"""LLM classifier (optional). NOT run by the author - no API key was available.
Needs: pip install anthropic ; export ANTHROPIC_API_KEY=...
Batches 20 tickets per call, caches every answer in out/llm_cache.jsonl so re-runs cost nothing."""
import json, os, re
import pandas as pd

MODEL = os.environ.get("VIREO_MODEL", "claude-haiku-4-5-20251001")
TOPICS = ["Billing & Payments", "Delivery & Shipping", "Returns & Refunds", "Warranty & Repair", "Order Change / Cancel",
          "Account & Login", "App & Firmware", "Charging & Battery", "Connectivity", "Audio Quality", "Product Enquiry", "Unclear"]
SYSTEM = f"""You label customer-support tickets for a consumer-audio brand (earbuds, headphones, speakers, watches).
For each ticket choose the ONE topic that describes the customer's real problem. Topics: {TOPICS}.
Rules:
- Judge by what the customer actually describes, not by words the agent used to resolve it (e.g. a refund given for a parcel that never arrived is still 'Delivery & Shipping').
- Money taken but no parcel arrived = Delivery & Shipping. Money taken but NO ORDER exists, double charge, invoice/GST, coupon = Billing & Payments.
- Refund not credited, return pickup missed = Returns & Refunds. Repair/RMA status or hardware fault needing a certified replacement = Warranty & Repair.
- Cancel an order, change address/pincode = Order Change / Cancel.
- If you cannot tell, answer 'Unclear'. Do not guess.
Reply with ONLY a JSON list: [{{"i": <index>, "topic": "<topic>", "conf": <0-1>}}, ...]"""

def _client():
    import anthropic
    return anthropic.Anthropic()

def classify_df(df, batch=20, cache="out/llm_cache.jsonl"):
    os.makedirs("out", exist_ok=True)
    seen = {}
    if os.path.exists(cache):
        for line in open(cache):
            d = json.loads(line); seen[d["ticket_id"]] = d
    todo = df[~df.ticket_id.isin(seen)]
    cl = _client() if len(todo) else None
    for s in range(0, len(todo), batch):
        chunk = todo.iloc[s:s + batch]
        body = "\n\n".join(f"[{i}] CUSTOMER: {str(r.customer_message)[:600]}\n    AGENT NOTE: {str(r.agent_notes)[:300]}"
                           for i, r in enumerate(chunk.itertuples()))
        msg = cl.messages.create(model=MODEL, max_tokens=1500, system=SYSTEM, messages=[{"role": "user", "content": body}])
        txt = msg.content[0].text
        try:
            out = json.loads(re.search(r"\[.*\]", txt, re.S).group(0))
        except Exception:
            out = []                              # unparsable batch -> falls to 'Unclear' below
        got = {o["i"]: o for o in out if isinstance(o, dict) and "i" in o}
        with open(cache, "a") as f:
            for i, r in enumerate(chunk.itertuples()):
                o = got.get(i, {})
                tp = o.get("topic") if o.get("topic") in TOPICS else "Unclear"
                rec = {"ticket_id": r.ticket_id, "topic": tp, "conf": float(o.get("conf", 0) or 0),
                       "in_tok": msg.usage.input_tokens // len(chunk), "out_tok": msg.usage.output_tokens // len(chunk)}
                f.write(json.dumps(rec) + "\n"); seen[r.ticket_id] = rec
    res = pd.DataFrame([seen[t] for t in df.ticket_id], index=df.index)
    return res
