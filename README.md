# Vireo Audio – ticket routing check

Question from the client: *"Which team is biggest? Give it two hires."*
This tool checks whether the bot's category tag (which also decides the team) can be trusted, re-labels every
ticket from what the customer actually wrote, and redraws the monthly volume by category and by team.

## Run it (clean machine, ~1 minute, no API key needed)
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pandas matplotlib tabulate
mkdir data                                              # copy the 5 client CSVs into ./data
#   tickets.csv agents.csv orders.csv customers.csv products.csv
python run.py                                           # free keyword classifier
```
Outputs in `out/`: `summary.md` (numbers + tables), `charts/monthly_overview.png`,
`charts/billing_queue_composition.png`, `monthly_*.csv`, `results.csv` (one row per ticket, with `true_topic`,
`true_team`, `misrouted`).

Optional LLM classifier (**written but never run – no API key was available to the author**):
```bash
pip install anthropic && export ANTHROPIC_API_KEY=...
python run.py --classifier llm --limit 200              # try 200 first; answers are cached in out/llm_cache.jsonl
```

## Files
| File | What |
|---|---|
| `run.py` | cleaning, money maths, team table, charts |
| `rules.py` | keyword classifier (message first, agent note only as fallback) |
| `llm_classify.py` | Claude version, batches of 20, cached |
| `validation_labels_by_claude.csv` | 110 reviewed tickets: prediction + verdict (labelled by Claude, not a human) |
| `data/hand_label_sheet.csv` (not committed) | 50 tickets with blank columns for a human to label |

## Decisions I had to make (and why)
1. **Window = Jan 2025 – Jun 2026.** The brief says 18 months from Jan 2025; the file also holds 139 tickets from Jun–Dec 2024 (3–32 a month, looks like a partial migration). Excluded.
2. **Legacy `resolved_at` is UTC** (policy §9). 64% of legacy rows had negative handle time until I added 5.5 h. Fixed in `load()`.
3. **Blank `transfers` ≠ 0.** Transfer stats use post-migration (`helpdesk`) rows only.
4. **Message beats agent note** for the true topic: notes describe the *resolution* ("refund initiated as lost in transit" on a parcel that never arrived) and sometimes copy the bot's wrong tag.
5. **Only confident moves to a specialist team count as "misrouted"** (Billing, Logistics, Returns, Warranty). Frontline sub-topics (battery vs pairing) are not counted – they don't change who works the ticket. "Unclear" is never counted.
6. **Cancellation / address change stays with Frontline**, not Returns or Logistics (policy §6 gives those teams pickups/refunds and delivery/reshipment only). Judgement call.
7. **Legacy refund unit:** policy §9 warns the old tool used a "native unit". Refund ÷ order value is 1.0 in the same proportions in both systems, so I treated both as rupees.
8. **Tickets per agent uses today's roster** (all 44 agents have no end date) for Jan–Jun 2026 only.
9. **Duplicates:** policy §9 says some legacy tickets were re-imported. I could not find them (no duplicate on customer+message, customer+order+notes, or ±5.5 h shifts). Not removed.

## Known problems
See `SUBMISSION_FORM_DRAFT.md`, "What is wrong".
