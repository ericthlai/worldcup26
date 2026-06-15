#!/usr/bin/env python3
"""
Build the World Cup 2026 squad database.

Pipeline:
    raw/*.json  --(--assemble)-->  squads.json  --(always)-->  squads.js

Normal update flow (after a lineup change, transfer, injury):
    1. edit  squads.json   (the canonical database — clean JSON)
    2. run   python build_squads.py
    3. refresh the site — squads.js is regenerated, the front end picks it up.

Bootstrap from the research workflow output:
    python build_squads.py --assemble
    (merges every raw/*.json batch into squads.json, then writes squads.js)

The site loads squads.js (a window.WC_SQUADS global) via a <script> tag, so no
fetch/CORS is needed and it works offline. squads.js is AUTO-GENERATED; never
hand-edit it — edit squads.json instead.
"""
import json, sys, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
JSON_PATH = os.path.join(HERE, "squads.json")
JS_PATH = os.path.join(HERE, "squads.js")
DEFAULT_UPDATED = "2026-06-14"

# canonical team ordering (group -> codes), mirrors GROUPS in index.html
GROUPS = {
    "A": ["mex", "rsa", "kor", "cze"], "B": ["can", "bih", "qat", "sui"],
    "C": ["bra", "mar", "hai", "sco"], "D": ["usa", "par", "aus", "tur"],
    "E": ["ger", "cuw", "civ", "ecu"], "F": ["ned", "jpn", "swe", "tun"],
    "G": ["bel", "egy", "irn", "nzl"], "H": ["esp", "cpv", "ksa", "uru"],
    "I": ["fra", "sen", "irq", "nor"], "J": ["arg", "alg", "aut", "jor"],
    "K": ["por", "cod", "uzb", "col"], "L": ["eng", "cro", "gha", "pan"],
}
ORDER = [code for g in sorted(GROUPS) for code in GROUPS[g]]
TEAM_GROUP = {code: g for g, codes in GROUPS.items() for code in codes}
POS = {"GK", "RB", "CB", "LB", "RWB", "LWB", "DM", "CM", "AM", "RM", "LM", "RW", "LW", "CF", "ST"}

PLAYER_KEYS = ["no", "name", "pos", "club", "cc", "val", "star", "why", "note"]
TEAM_KEYS = ["code", "nameEN", "fifaRank", "group", "formation", "manager",
             "style", "watch", "xi", "subs", "updated"]

warnings = []


def bi(o):
    """Coerce a bilingual prose field to {en, zh} strings."""
    if not isinstance(o, dict):
        return None
    en = o.get("en") or o.get("EN") or ""
    zh = o.get("zh") or o.get("ZH") or ""
    if not en and not zh:
        return None
    return {"en": str(en), "zh": str(zh)}


def bi_list(o):
    """Coerce a bilingual bullet field to {en:[...], zh:[...]}."""
    if not isinstance(o, dict):
        return {"en": [], "zh": []}
    def lst(x):
        if isinstance(x, list):
            return [str(s) for s in x if str(s).strip()]
        if isinstance(x, str) and x.strip():
            return [x.strip()]
        return []
    return {"en": lst(o.get("en")), "zh": lst(o.get("zh"))}


def clean_player(p, code, where):
    if not isinstance(p, dict):
        return None
    out = {}
    try:
        out["no"] = int(p.get("no"))
    except (TypeError, ValueError):
        out["no"] = 0
        warnings.append(f"{code}: {where} player '{p.get('name')}' has no/invalid number")
    out["name"] = str(p.get("name", "")).strip()
    pos = str(p.get("pos", "")).strip().upper()
    if pos not in POS:
        warnings.append(f"{code}: {where} player '{out['name']}' has unknown pos '{pos}'")
    out["pos"] = pos
    out["club"] = str(p.get("club", "")).strip()
    out["cc"] = str(p.get("cc", "")).strip().upper()
    try:
        out["val"] = round(float(p.get("val", 0)), 2)
    except (TypeError, ValueError):
        out["val"] = 0
    if p.get("star") is True:
        out["star"] = True
    why = bi(p.get("why"))
    if why:
        out["why"] = why
    note = bi(p.get("note"))
    if note:
        out["note"] = note
    if not out["name"]:
        return None
    return out


def clean_team(t):
    code = (t.get("code") or "").strip().lower()
    if not code:
        return None
    out = {"code": code}
    out["nameEN"] = str(t.get("nameEN", "")).strip()
    fr = t.get("fifaRank")
    try:
        out["fifaRank"] = int(fr) if fr is not None else None
    except (TypeError, ValueError):
        out["fifaRank"] = None
    out["group"] = (t.get("group") or TEAM_GROUP.get(code, "")).strip().upper()
    out["formation"] = str(t.get("formation", "")).strip()
    out["manager"] = str(t.get("manager", "")).strip()
    out["style"] = bi(t.get("style")) or {"en": "", "zh": ""}
    out["watch"] = bi_list(t.get("watch"))
    out["xi"] = [q for q in (clean_player(p, code, "XI") for p in (t.get("xi") or [])) if q]
    out["subs"] = [q for q in (clean_player(p, code, "sub") for p in (t.get("subs") or [])) if q]
    out["updated"] = str(t.get("updated") or DEFAULT_UPDATED)
    if len(out["xi"]) != 11:
        warnings.append(f"{code}: XI has {len(out['xi'])} players (expected 11)")
    # duplicate shirt-number check within the XI
    nums = [p["no"] for p in out["xi"]]
    dupes = {n for n in nums if nums.count(n) > 1 and n}
    if dupes:
        warnings.append(f"{code}: duplicate XI shirt numbers {sorted(dupes)}")
    return out


def load_raw():
    teams = {}
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.json")))
    if not files:
        sys.exit(f"No raw batches in {RAW_DIR}")
    for f in files:
        data = json.load(open(f, encoding="utf-8"))
        arr = None
        if isinstance(data, dict):
            arr = (data.get("teams")
                   or (data.get("result") or {}).get("teams"))
        if arr is None and isinstance(data, list):
            arr = data
        if not arr:
            warnings.append(f"{os.path.basename(f)}: no teams array found")
            continue
        for t in arr:
            c = clean_team(t)
            if c:
                teams[c["code"]] = c
    return teams


def emit_js(squads):
    body = json.dumps(squads, ensure_ascii=False, indent=2)
    header = (
        "/* ============================================================\n"
        "   WORLD CUP 2026 — SQUAD DATABASE  (window.WC_SQUADS)\n"
        "   AUTO-GENERATED from squads.json by build_squads.py.\n"
        "   DO NOT edit this file by hand — edit squads.json and rerun\n"
        "       python build_squads.py\n"
        "   Player values are Transfermarkt market value in EUR millions.\n"
        "   ============================================================ */\n"
    )
    with open(JS_PATH, "w", encoding="utf-8") as fh:
        fh.write(header)
        fh.write("window.WC_SQUADS = ")
        fh.write(body)
        fh.write(";\n")


def main():
    if "--assemble" in sys.argv:
        teams = load_raw()
        ordered = {c: teams[c] for c in ORDER if c in teams}
        # keep any extras not in ORDER (shouldn't happen) appended
        for c in teams:
            if c not in ordered:
                ordered[c] = teams[c]
        json.dump(ordered, open(JSON_PATH, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        squads = ordered
        print(f"assembled {len(squads)} teams -> squads.json")
    else:
        if not os.path.exists(JSON_PATH):
            sys.exit("squads.json not found — run with --assemble first")
        raw = json.load(open(JSON_PATH, encoding="utf-8"))
        # squads.json may be a dict keyed by code or a list of teams
        items = raw.values() if isinstance(raw, dict) else raw
        cleaned = {}
        for t in items:
            c = clean_team(t)
            if c:
                cleaned[c["code"]] = c
        squads = {c: cleaned[c] for c in ORDER if c in cleaned}
        for c in cleaned:
            if c not in squads:
                squads[c] = cleaned[c]

    emit_js(squads)
    covered = len(squads)
    missing = [c for c in ORDER if c not in squads]
    print(f"wrote squads.js — {covered}/48 teams")
    if missing:
        print(f"missing teams: {', '.join(missing)}")
    if warnings:
        print(f"\n{len(warnings)} data warnings:")
        for w in warnings:
            print("  -", w)


if __name__ == "__main__":
    main()
