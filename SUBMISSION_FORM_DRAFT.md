# Submission form – DRAFT (edit anything marked ⚠ before you submit)

**1. What did you build, and what business outcome does it move? State the number and the money.**
A Python tool (`run.py`) that re-labels each of 11,641 tickets (Jan 2025–Jun 2026) from the customer's own words, compares it with the chat bot's tag, and redraws monthly volume by category and by team. Finding: 23.0% of all tickets (2,672) land in the wrong specialist team, and 39% of the Billing queue (954 of 2,425) is really Logistics/Returns work. Goal: cut mis-routed tickets from 23% to under 8% by year end. Direct saving today is Rs 42,242 a quarter (Rs 67 transfer cost + Rs 27 SLA credits per mis-routed ticket × 2,672 ÷ 6 quarters); about Rs 28,000 a quarter if two-thirds is fixed. The bigger consequence is the hiring decision: Rs 9 lakh a year for two hires should not go to Billing on the current evidence.

**2. What does one run cost, and what would a month cost at ~650 tickets/week?**
The delivered run (keyword classifier) uses no paid calls: Rs 0, about 10 seconds. For the optional LLM version (never run – estimate only): about 90 input + 25 output tokens per ticket (avg ticket text is 220 characters ≈ 55 tokens, plus a shared prompt split across 20 tickets). At Claude Haiku 4.5 list prices I recalled from memory ⚠ (verify: $1 / $5 per million tokens): 90 × $1/1M + 25 × $5/1M = $0.000215 per ticket. Full 11,641 tickets ≈ $2.50. A month: 650 × 52 ÷ 12 ≈ 2,817 tickets × $0.000215 ≈ $0.61 (about Rs 55).

**3. How do you know it works?**
I reviewed 110 random tickets in two rounds. Round 1: 60 tickets, 86.7% exact topic, 96.7% right owning team. I then fixed regex bugs that round exposed (e.g. "charged" matching "charging", "in app" matching the app rule, "DOA" in a note pulling a pairing fault into Warranty). Round 2 on a fresh 50 tickets: 92% topic, 98% owning team. Combined: 89% topic, 97% team. Weaknesses: tiny sample (95% interval roughly ±6 points); **the reviewer was Claude, not a human** ⚠ (please label `data/hand_label_sheet.csv` yourself and replace these numbers); round 2 shows only the fixed version. Cross-check without labels: message-only vs note-only labels agree 85% on the owning team. Errors are: terse messages with no keyword (→ Unclear), words that mean two things, and the note fallback picking up resolution wording.

**4. Did you change, narrow, or push back on the client's ask?**
Yes. Asked for: biggest team by tagged volume gets two hires. I treated the tag as untrusted (Sameer's email says the bot sets it and agents rarely re-tag), measured mis-routing, and recommend holding the Billing hires. I also narrowed "auto-categorise" to "find the owning team", because that is what changes the headcount answer. Frontline sub-topics are lower quality and not used for the money. I would tell Priya this before the chart, since she has half-promised the hires.

**5. What is wrong with what you are handing over?**
- Classifier is keywords, not AI; the LLM path is untested.
- Validation was done by Claude on 110 tickets, not by a person.
- Many messages use the same templates, so the sample is less independent than it looks.
- "Misrouted" only counts confident moves into Billing/Logistics/Returns/Warranty; Order Change/Cancel tagged Billing is left in Billing (undercount).
- One hardware-fault wording ("single earbud dead") could belong to Frontline or Tier 2; I did not resolve it.
- Tickets per agent is not workload: handle time is calendar time (first reply to resolution), not effort, and uses today's roster.
- The transfer and SLA saving per ticket is a difference of averages, not proof of cause.
- Re-imported legacy duplicates (policy §9) not found; none removed.
- Refund + replacement on 74 orders is an unverified flag.
- Volume rise from Aug 2025 (Pulse 2 launch) not analysed further.

**6. What did you deliberately leave out, and why?**
Tier 2 vs Tier 1 comparison (policy §6 forbids it); CSAT (45% response, no link to the headcount question); lot-code / defect analysis (checked quickly, no strong signal, not the question); a staffing model in agent-hours (no effort data); fixing the bot (not our scope); a dashboard.

**7. Anything you built or found that nobody asked for?**
SLA breach credits: 1,292 tickets × Rs 350 ≈ Rs 4.5 lakh over 18 months, Billing worst (about 20% vs 6–11% elsewhere). Refund + replacement on 74 orders (up to Rs 1.4 lakh). Legacy timestamp bug (UTC vs IST). Public repo must not contain customer data, so `data/` is git-ignored.

**8. What did you use AI for?** ⚠ edit to match what you really did
Claude (Sonnet 5.5) in claude.ai wrote the exploration code, the keyword classifier, the pipeline, the LLM module, the validation review, and drafts of the memo and this form. It helped: fast data profiling, spotting the Billing mismatch. It wasted time: first classifier versions leaked resolution wording from notes. Discarded: an early regex set and a "Returns" mapping for cancellations. No other tools. Cost: ⚠ your plan cost, Rs 0 in API calls. Screen recording link: ⚠ add.

**9. Someone picks this up on Monday and you are unreachable – the three things.**
1) `python run.py` after copying the CSVs into `data/`; read `out/summary.md`. 2) Do the human check: label `data/hand_label_sheet.csv` and replace the accuracy numbers. 3) Do not use the LLM path before a 200-ticket trial (`--limit 200`), and never commit `data/`.

**10. Honest hours spent.** ⚠ one number, yours.

**GitHub URL / Drive link:** ⚠ add.
