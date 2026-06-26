#!/usr/bin/env python3
"""
Merge a full-roster research batch into squads.json.

    python merge_rosters.py raw/roster.json
    python build_squads.py          # then regenerate squads.js

The roster batch ({"rosters":[{code, formation, manager, xi:[11], bench:[...]}]})
replaces each team's player list (xi -> xi, bench -> subs) and refreshes
formation + manager, while KEEPING the existing bilingual style/watch prose,
fifaRank, group and nameEN. If a re-gathered team has no star players, the old
star/why flags are carried over by player-name match so the "who to watch"
section never goes empty.
"""
import json, os, sys, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "squads.json")
UPDATED = "2026-06-14"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", s)


def carry_stars(new_players, old_players):
    """If the new list has no stars, copy star/why from the old list by name."""
    if any(p.get("star") for p in new_players):
        return
    old_by_name = {norm(p["name"]): p for p in old_players if p.get("star")}
    for p in new_players:
        o = old_by_name.get(norm(p["name"]))
        if o:
            p["star"] = True
            if o.get("why"):
                p["why"] = o["why"]


def main():
    batch_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "raw", "roster.json")
    squads = json.load(open(JSON_PATH, encoding="utf-8"))
    raw = json.load(open(batch_path, encoding="utf-8"))
    rosters = (raw.get("result") or {}).get("rosters") or raw.get("rosters") or []
    if not rosters:
        sys.exit(f"no 'rosters' in {batch_path}")

    merged, skipped, missing = 0, [], []
    for r in rosters:
        code = (r.get("code") or "").strip().lower()
        if not code or code not in squads:
            skipped.append(code or "?")
            continue
        xi, bench = r.get("xi") or [], r.get("bench") or []
        if len(xi) != 11 or len(bench) < 10:
            missing.append(f"{code}(xi={len(xi)},bench={len(bench)})")
        # drop any bench player already in the XI (agents sometimes double-list a starter)
        xi_nos = {p.get("no") for p in xi}
        xi_names = {norm(p.get("name", "")) for p in xi}
        bench = [p for p in bench
                 if p.get("no") not in xi_nos and norm(p.get("name", "")) not in xi_names]
        old_all = (squads[code].get("xi") or []) + (squads[code].get("subs") or [])
        new_all = list(xi) + list(bench)
        carry_stars(new_all, old_all)
        t = squads[code]
        t["xi"] = xi
        t["subs"] = bench
        if r.get("formation"):
            t["formation"] = r["formation"]
        if r.get("manager"):
            t["manager"] = r["manager"]
        t["updated"] = UPDATED
        merged += 1

    json.dump(squads, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"merged rosters for {merged} teams")
    if skipped:
        print(f"skipped (no matching code): {skipped}")
    if missing:
        print(f"thin rosters (review): {missing}")
    sizes = {c: len((t.get('xi') or [])) + len((t.get('subs') or [])) for c, t in squads.items()}
    small = {c: n for c, n in sizes.items() if n < 22}
    print(f"squad sizes — min {min(sizes.values())}, max {max(sizes.values())}, avg {sum(sizes.values())//len(sizes)}")
    if small:
        print(f"under 22 players: {small}")


if __name__ == "__main__":
    main()
