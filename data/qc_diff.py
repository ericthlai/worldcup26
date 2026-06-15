#!/usr/bin/env python3
"""
QC diff: compare squads.json (our data, run A) against an independent
re-research pass (run B, raw/qc.json) and flag discrepancies.

    python qc_diff.py

Flags, by descending confidence:
  NUMBER   same player, different shirt number   (our_no -> verifier_no)
  MISSING  our player not found in verifier's 26-man squad (possible wrong/extra player)
  MANAGER  head-coach name mismatch
  FORMATION  informational, differing formation

These are CANDIDATES for human review, not auto-fixes — projected XIs and
partial verifier squads create some noise. Review against raw/qc.json before
editing squads.json.
"""
import json, os, re, sys, unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
MINE = json.load(open(os.path.join(HERE, "squads.json"), encoding="utf-8"))
QC_RAW = json.load(open(os.path.join(HERE, "raw", "qc.json"), encoding="utf-8"))
QC_LIST = (QC_RAW.get("result") or {}).get("qc") or QC_RAW.get("qc") or QC_RAW
QC = {t["code"].strip().lower(): t for t in QC_LIST if isinstance(t, dict) and t.get("code")}

DROP = {"jr", "junior", "jnr", "ii", "iii", "de", "da", "do", "dos", "das", "van", "von", "der", "el", "al"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s):
    return [t for t in norm(s).split() if t]


def core_tokens(s):
    return [t for t in tokens(s) if t not in DROP] or tokens(s)


def match(my_name, vlist):
    """Find best verifier entry for my_name. Returns (entry, score) or (None,0)."""
    mn = norm(my_name)
    mt = core_tokens(my_name)
    if not mt:
        return None, 0
    best, best_score = None, 0
    for v in vlist:
        vn = norm(v["name"])
        vt = core_tokens(v["name"])
        if not vt:
            continue
        score = 0
        if mn == vn:
            score = 100
        elif mt[-1] == vt[-1]:  # same surname
            score = 60
            if mt[0][:1] == vt[0][:1]:  # same first initial
                score += 25
            if mt[0] == vt[0]:
                score += 10
        else:
            shared = set(t for t in mt if len(t) >= 4) & set(vt)
            if shared:
                score = 35 + 5 * len(shared)
        if score > best_score:
            best, best_score = v, score
    return (best, best_score) if best_score >= 50 else (None, best_score)


def main():
    flags = {"NUMBER": [], "MISSING": [], "MANAGER": [], "FORMATION": []}
    no_verifier = []
    thin = []
    for code, t in MINE.items():
        q = QC.get(code)
        if not q:
            no_verifier.append(code)
            continue
        vsquad = q.get("squad") or []
        if len(vsquad) < 22:
            thin.append(f"{code} ({len(vsquad)})")
        # manager
        if q.get("manager") and norm(q["manager"]) != norm(t["manager"]):
            # accept surname match (coach often given as full vs short)
            if core_tokens(q["manager"])[-1:] != core_tokens(t["manager"])[-1:]:
                flags["MANAGER"].append(f"{code}: ours='{t['manager']}' verifier='{q['manager']}'")
        # formation (informational)
        if q.get("formation") and q["formation"].replace(" ", "") != t["formation"].replace(" ", ""):
            flags["FORMATION"].append(f"{code}: ours={t['formation']} verifier={q['formation']}")
        # players
        for p in t["xi"] + t["subs"]:
            v, score = match(p["name"], vsquad)
            where = "XI" if p in t["xi"] else "sub"
            if v is None:
                # only flag MISSING when verifier squad is reasonably complete
                if len(vsquad) >= 22:
                    flags["MISSING"].append(f"{code}: {where} #{p['no']} {p['name']} ({p['club']}) — not in verifier's {len(vsquad)}-man list")
            elif v.get("no") and v["no"] != p["no"]:
                flags["NUMBER"].append(f"{code}: {p['name']} — ours #{p['no']}, verifier #{v['no']}  [{p['club']}]")

    print(f"QC diff — {len(MINE)} teams ours, {len(QC)} verified\n")
    if no_verifier:
        print(f"NO verifier data for: {', '.join(no_verifier)}\n")
    if thin:
        print(f"Thin verifier squads (<22, MISSING flags suppressed): {', '.join(thin)}\n")
    for k in ["NUMBER", "MISSING", "MANAGER", "FORMATION"]:
        print(f"=== {k} ({len(flags[k])}) ===")
        for f in flags[k]:
            print("  " + f)
        print()
    total_actionable = len(flags["NUMBER"]) + len(flags["MISSING"]) + len(flags["MANAGER"])
    print(f"Actionable candidates (NUMBER+MISSING+MANAGER): {total_actionable}")


if __name__ == "__main__":
    main()
