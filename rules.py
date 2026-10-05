"""Keyword baseline: assigns a TRUE topic from message + agent note (no API needed)."""
import re

# (topic, regex). Order = tie-break priority. Matched against lower-cased text.
TOPICS = [
 ("Billing & Payments", r"double (payment|charge)|charged twice|duplicate (payment|charge|debit)|deducted twice|"
    r"\bgst|invoice|gateway|utr\b|upi (shows|says)|amount deducted|failed order after payment|"
    r"payment (failed|went through)|no order (was )?(created|placed)|discount not applied|coupon|"
    r"card charged|charged two|two times|paid once|price (adjust|drop|diff)|promo|bank says|went to you but|rs \d+ went|payment (page )?(said )?success"),
 ("Returns & Refunds", r"refund (not|pending|delay|status|still|was)|rfnd|waiting for (my |the )?(refund|money)|"
    r"amount is nowhere|money (for the return|hasn.t come back)|money back|return (was )?(accepted|approved|received)|"
    r"reverse pick|pick ?up|pickup|pkp|no one (showed|came)|nobody came|return request|want to return"),
 ("Delivery & Shipping", r"not (been )?deliver|never (came|arrived)|shipment not|not rec(ei|ie)ved|haven.t received|not rcvd|"
    r"delivery delay|dlvry delay|delayed delivery|stuck on shipped|tracking|marked it delivered|doorstep|"
    r"empty.?handed|nothing in hand|wrong (item|product|variant|colour|color)|incorrect product|got (white|black|blue)|"
    r"not what i (paid|asked)|transit damage|damaged in transit|arrived (broken|damaged)|"
    r"(change|update|fix).{0,12}address|address (update|change)|typo in (the )?(flat|address)|pincode|wrong pin|reship|"
    r"order (is )?(late|delayed)|where is my order|parcel|money went out"),
 ("Order Change / Cancel", r"cancel|ordered by mistake|wrong colour, don.t ship|stop the shipment|reverse it"),
 ("Warranty & Repair", r"\brma\b|rma\d|repair|warranty|service cent|claim number|sent the unit in|"
    r"touch|tap ten times|screen (lights|crack|flicker|is)|unresponsive|strap|won.t (turn|switch) on|no audio at all|left side|right side"),
 ("Account & Login", r"log ?in|otp|login code|password|account (locked|unlock)|sign ?in|verification code"),
 ("App & Firmware", r"(?<!in )(?<!the )\bapp (crash|not|keeps|closes|won)|vireo app|firmware|\bfw\b|update failed|progress bar|bricked|crash"),
 ("Charging & Battery", r"batter|charging(?! case)|not charg|won.t charge|dies by|drain|power(s)? off"),
 ("Connectivity", r"pair|bluetooth|disconnect|connect(ion)? (drop|lost)|not discoverable|drops|reconnect"),
 ("Audio Quality", r"audio|sound|\bmic\b|microphone|buzz|distort|static|crackl|underwater|volume|bass|silent"),
 ("Product Enquiry", r"enquiry|inquiry|compatib|before i buy|does .* work with|will this|pre-?sales|spec sheet|can i connect|which (model|one)"),
]
OWNER = {
 "Billing & Payments":"Billing", "Delivery & Shipping":"Logistics",
 "Returns & Refunds":"Returns Desk", "Warranty & Repair":"Escalations & Warranty",
}
def owner(topic, current_team):
    """Frontline topics keep the frontline team the ticket already sits in (channel-based)."""
    return OWNER.get(topic, current_team if "Frontline" in current_team else None)

def score(text):
    text = text.lower(); hits = {}
    for name, rx in TOPICS:
        m = re.findall(rx, text)
        if m: hits[name] = len(m)
    return hits

def classify(message, note):
    """Message-first: the customer's own words decide; the agent note is only a fallback.
    (Notes often describe the *resolution* - e.g. 'refund initiated as lost in transit' on a
    delivery problem - and some copy the bot's wrong tag.)  Returns (topic, confidence, source)."""
    order = [n for n, _ in TOPICS]
    for src, text in (("message", message), ("note", note)):
        h = score(text)
        if h:
            best = sorted(h.items(), key=lambda kv: (-kv[1], order.index(kv[0])))
            return best[0][0], round(best[0][1] / sum(h.values()), 2), src
    return "Unclear", 0.0, "none"
