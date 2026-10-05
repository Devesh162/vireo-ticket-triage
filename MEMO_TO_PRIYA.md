**To:** Priya Raman  **cc:** Arjun Mehta, Neha Kulkarni, Sameer Qureshi
**Re:** Headcount – please hold the Billing hires for now

**Short answer.** Billing is not our biggest real queue. About 4 in 10 tickets sitting in Billing are not billing problems. I recommend we do not commit the two hires to Billing yet, and fix ticket routing first.

**What I found (Jan 2025 – Jun 2026, 11,641 tickets).**
- The chat bot sets the category from the customer's first question, and the category decides the team. I re-read what customers actually wrote.
- Of 2,425 tickets sent to Billing, **954 (39%) belong to someone else**, mostly Logistics. Typical message: "I paid but the parcel never came." That is a delivery problem, not a payment problem. Agent notes say the same ("not a billing issue, moving to Logistics").
- It is not a recent blip. The share has been 31–48% every month since January 2025.
- Across the whole desk, about **1 in 4 tickets (23%) starts in the wrong team**. Those tickets are transferred 3x as often (0.34 vs 0.12 per ticket) and miss the first-response target almost twice as often (17% vs 9%).

**What changes on the chart.** Billing's share falls from about 21% to about 16%. Logistics rises from 16% to about 26% and becomes the biggest team. Returns Desk also rises (9% to 13%). So Neha's instinct about Logistics looks right, though the tool has not yet shown it is *understaffed*.

| Jan–Jun 2026, tickets per agent per month | As routed | Corrected |
|---|---|---|
| Billing (4 agents) | 37.5 | 30.5 |
| Logistics (5) | 24.5 | 37.9 |
| Returns Desk (3) | 21.4 | 32.3 |

**The number.** Cut wrongly-routed tickets from 23% of volume to under 8% (and the Billing queue from 39% to under 10%) by the end of the year. Direct saving is about **Rs 42,000 a quarter today** (transfer fees plus SLA store credits), roughly **Rs 28,000 a quarter** if two-thirds of the problem is removed. That is small. The larger number is the decision it protects: two hires cost about Rs 9 lakh a year, and this data says Billing is the wrong place for them.

**What I recommend.**
1. Do not allocate the two hires to Billing yet.
2. Fix the bot's intake question for "paid but not delivered" and "refund not received". Then re-run this check after 6–8 weeks.
3. If you still need to hire after that, Logistics is the stronger case on current numbers; Returns Desk second.

**How sure am I?** Fairly sure about the Billing finding (it is large and the agent notes confirm it). Less sure about exact figures. The classifier is keyword-based. In my check of 110 tickets it picked the right owning team in 97% of cases and the exact topic in 89%. The checker was Claude, not a person, so a human spot-check of the 50 tickets in the hand-label sheet is still needed. Tickets per agent is also not true workload: Logistics and Returns cases run for days, Billing's mostly close in minutes.

**Also noticed.** On 74 orders, a refund and a replacement were both issued across the order's tickets (policy §5 forbids this). That is up to about Rs 1.4 lakh in replacement cost and needs a check by Finance. Ticket volume stepped up in August 2025 alongside the Pulse 2 launch.
