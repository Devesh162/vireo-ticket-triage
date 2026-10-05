"""Vireo ticket triage: find the TRUE issue behind each ticket, compare with the bot's tag,
and show what that does to monthly volume by category and by team.

Usage:
  python run.py                       # free keyword baseline (no API key needed)
  python run.py --classifier llm      # Claude (needs ANTHROPIC_API_KEY); results cached
  python run.py --classifier llm --limit 200
Outputs go to ./out/ (results.csv, summary.md, charts/*.png, monthly_*.csv)
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
import rules

DATA = os.environ.get("VIREO_DATA", "data")   # client CSVs go here (git-ignored: contains customer data)
SPECIALIST = ["Billing", "Logistics", "Returns Desk", "Escalations & Warranty"]
START, END = "2025-01-01", "2026-06-30 23:59"   # decision D1: brief says Jan-25..Jun-26
TRANSFER_COST, BREACH_CREDIT, AGENT_HOUR = 305, 350, 165
TARGET_H = {"chat": .25, "voice": 2, "social": 4, "email": 8}
IST_FIX = pd.Timedelta(hours=5.5)                # decision D2: legacy resolved_at is UTC

def load():
    t = pd.read_csv(os.path.join(DATA, "tickets.csv"))
    for c in ["created_at", "first_response_at", "resolved_at"]:
        t[c] = pd.to_datetime(t[c])
    n0 = len(t)
    t = t[(t.created_at >= START) & (t.created_at <= END)].copy()
    t.attrs["dropped_pre2025"] = n0 - len(t)
    leg = t.source_system == "legacy_fd"
    t.loc[leg, "resolved_at"] = t.loc[leg, "resolved_at"] + IST_FIX
    t["resp_h"] = (t.first_response_at - t.created_at).dt.total_seconds() / 3600
    t["breach"] = t.resp_h > t.channel.map(TARGET_H)
    t["month"] = t.created_at.dt.to_period("M").astype(str)
    return t

def classify(t, kind, limit):
    if kind == "llm":
        import llm_classify
        res = llm_classify.classify_df(t if not limit else t.head(limit))
        t = t.loc[res.index].copy()
        t["true_topic"], t["conf"], t["pred_src"] = res.topic, res.conf, "llm"
    else:
        r = [rules.classify(m, n) for m, n in zip(t.customer_message, t.agent_notes)]
        t["true_topic"] = [x[0] for x in r]; t["conf"] = [x[1] for x in r]; t["pred_src"] = [x[2] for x in r]
    t["true_team"] = [rules.owner(tp, tm) or tm for tp, tm in zip(t.true_topic, t.assigned_team)]
    # 'Unclear' / frontline topics never count as misrouted (we only flag confident specialist moves)
    t["misrouted"] = (t.true_team != t.assigned_team) & t.true_team.isin(SPECIALIST) & (t.true_topic != "Unclear")
    t["tag_ok_specialist"] = ~t.misrouted
    return t

def money(t):
    out = {}
    h = t[t.source_system == "helpdesk"]
    mis_h = h[h.misrouted]
    out["n"] = len(t); out["months"] = t.month.nunique()
    out["misrouted"] = int(t.misrouted.sum()); out["misrouted_pct"] = t.misrouted.mean()
    bill = t[t.assigned_team == "Billing"]
    out["billing_n"] = len(bill); out["billing_mis"] = int(bill.misrouted.sum())
    out["billing_mis_pct"] = bill.misrouted.mean()
    # transfers: observed on helpdesk rows only (blank != 0)
    out["xfer_rate_mis"] = float(mis_h.transfers.mean()); out["xfer_rate_ok"] = float(h[~h.misrouted].transfers.mean())
    out["xfer_cost_per_mis"] = (out["xfer_rate_mis"] - out["xfer_rate_ok"]) * TRANSFER_COST
    # breach: excess breach rate of misrouted vs other tickets, Rs350 each
    b_mis, b_ok = t[t.misrouted].breach.mean(), t[~t.misrouted].breach.mean()
    out["breach_mis"], out["breach_ok"] = float(b_mis), float(b_ok)
    out["breach_cost_per_mis"] = (b_mis - b_ok) * BREACH_CREDIT
    out["cost_per_mis"] = out["xfer_cost_per_mis"] + out["breach_cost_per_mis"]
    out["cost_total"] = out["cost_per_mis"] * out["misrouted"]
    out["cost_per_quarter"] = out["cost_total"] / (out["months"] / 3)
    return out

def team_table(t):
    """Tagged vs corrected volume per team, last 6 months, per agent."""
    ag = pd.read_csv(os.path.join(DATA, "agents.csv")); ag = ag[ag.to_date.isna()]
    heads = ag.groupby("team").agent_id.nunique()
    rec = t[t.created_at >= "2026-01-01"]
    m = 6
    tab = pd.DataFrame({"agents": heads,
        "tagged_per_month": rec.groupby("assigned_team").size() / m,
        "true_per_month": rec.groupby("true_team").size() / m})
    tab["tagged_per_agent"] = tab.tagged_per_month / tab.agents
    tab["true_per_agent"] = tab.true_per_month / tab.agents
    helpdesk = rec[rec.source_system == "helpdesk"]
    tab["transfer_rate"] = helpdesk.groupby("assigned_team").transfers.apply(lambda s: (s > 0).mean())
    tab["breach_rate"] = rec.groupby("assigned_team").breach.mean()
    return tab.round(2)

def charts(t):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    os.makedirs("out/charts", exist_ok=True)
    for col, name in [("category", "tagged_category"), ("true_topic", "true_topic"),
                      ("assigned_team", "tagged_team"), ("true_team", "true_team")]:
        pd.crosstab(t.month, t[col]).to_csv(f"out/monthly_{name}.csv")
    fig, ax = plt.subplots(2, 2, figsize=(16, 10))
    for a, (col, ttl) in zip(ax.ravel(), [("category", "Volume by category (bot tag)"), ("true_topic", "Volume by category (corrected)"),
                                          ("assigned_team", "Volume by team (as routed)"), ("true_team", "Volume by team (corrected)")]):
        pd.crosstab(t.month, t[col]).plot(kind="bar", stacked=True, ax=a, width=.85, colormap="tab20")
        a.set_title(ttl); a.set_xlabel(""); a.legend(fontsize=7, loc="upper left", ncol=2)
        a.tick_params(axis="x", labelsize=7)
    plt.tight_layout(); plt.savefig("out/charts/monthly_overview.png", dpi=130); plt.close()
    # Billing deep-dive
    b = t[t.assigned_team == "Billing"]
    pd.crosstab(b.month, b.true_topic).plot(kind="bar", stacked=True, figsize=(11, 5), width=.85, colormap="tab20")
    plt.title("What the 'Billing' queue actually contains"); plt.tight_layout()
    plt.savefig("out/charts/billing_queue_composition.png", dpi=130); plt.close()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--classifier", choices=["rules", "llm"], default="rules")
    ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    os.makedirs("out", exist_ok=True)
    t = classify(load(), a.classifier, a.limit)
    m = money(t); tt = team_table(t)
    t.drop(columns=["tag_ok_specialist"]).to_csv("out/results.csv", index=False)
    charts(t)
    flow = pd.crosstab(t.assigned_team, t.true_team)
    with open("out/summary.md", "w") as f:
        f.write(f"# Summary ({a.classifier} classifier)\n\nTickets analysed: {m['n']} ({t.month.min()} to {t.month.max()}); "
                f"{t.attrs.get('dropped_pre2025', 0)} pre-2025 rows excluded\n\n")
        f.write(f"- Misrouted to a specialist team: **{m['misrouted']} ({m['misrouted_pct']:.1%})**\n")
        f.write(f"- Billing queue: {m['billing_n']} tickets, **{m['billing_mis']} ({m['billing_mis_pct']:.1%}) belong elsewhere**\n")
        f.write(f"- Transfers (helpdesk rows only): misrouted {m['xfer_rate_mis']:.2f}/ticket vs {m['xfer_rate_ok']:.2f} for the rest\n")
        f.write(f"- First-response breach rate: misrouted {m['breach_mis']:.1%} vs {m['breach_ok']:.1%}\n")
        f.write(f"- Cost per misrouted ticket: Rs {m['cost_per_mis']:.0f} (transfers Rs {m['xfer_cost_per_mis']:.0f} + breach credits Rs {m['breach_cost_per_mis']:.0f})\n")
        f.write(f"- **Total: Rs {m['cost_total']:,.0f} over {m['months']} months = Rs {m['cost_per_quarter']:,.0f} per quarter**\n\n")
        f.write("## Routed team (rows) vs corrected team (columns)\n\n" + flow.to_markdown() + "\n\n")
        f.write("## Team load, Jan-Jun 2026 (monthly, per current agent)\n\n" + tt.to_markdown() + "\n")
    print(open("out/summary.md").read())

if __name__ == "__main__":
    main()
