# Squad database — World Cup 2026 watch handbook

This folder is the **backend database** for the team / match scouting feature
(projected XI, shirt numbers, positions, clubs, market values, tactics, watch
points). Edit the data here; the front end refreshes automatically — no rebuild
of the app itself.

## Files

| File | Role | Edit by hand? |
|---|---|---|
| `squads.json` | **Canonical database.** One entry per team, clean JSON. | ✅ Yes — this is the source of truth. |
| `squads.js` | Generated `window.WC_SQUADS` global the site loads. | ❌ No — auto-generated, overwritten on build. |
| `build_squads.py` | Build/validate script. | only to change rules |
| `raw/*.json` | Provenance: raw research-workflow output batches. | ❌ No — kept for history. |

The site (`../index.html` and `../en/index.html`) loads `squads.js` via a
`<script>` tag, so it works offline and needs no fetch/CORS.

## Update flow (after a lineup change, injury, transfer, value move)

```bash
# 1. edit squads.json  (find the team by its 3-letter code, e.g. "bra")
# 2. regenerate squads.js + run validation
cd site/data
python build_squads.py
# 3. refresh the page — done.
```

`build_squads.py` (no flag) reads `squads.json`, sanitizes it, prints any data
warnings (missing teams, XI not 11 players, duplicate shirt numbers, unknown
positions), and writes `squads.js`.

## Rebuild the whole database from research batches

```bash
python build_squads.py --assemble   # merges raw/*.json -> squads.json -> squads.js
```

## Schema (per team)

```jsonc
"bra": {
  "code": "bra",                 // 3-letter code, matches TEAMS in index.html
  "nameEN": "Brazil",
  "fifaRank": 5,                  // or null
  "group": "C",
  "formation": "4-3-3",
  "manager": "Carlo Ancelotti",
  "style":  { "en": "...", "zh": "..." },        // 1–2 sentence tactical identity
  "watch":  { "en": ["..."], "zh": ["..."] },    // 2–3 "what to watch" bullets
  "xi":   [ Player x11 ],         // projected starting XI, GK -> DEF -> MID -> FWD
  "subs": [ Player x3-5 ],        // key impact subs / depth
  "updated": "2026-06-14"
}
```

```jsonc
// Player
{
  "no": 11,                       // FIFA-registered shirt number
  "name": "Vinícius Júnior",      // English kit name
  "pos": "LW",                    // GK RB CB LB RWB LWB DM CM AM RM LM RW LW CF ST
  "club": "Real Madrid",
  "cc": "ESP",                    // club country, 3-letter UPPERCASE
  "val": 180,                     // Transfermarkt market value, EUR millions (0 = unlisted)
  "star": true,                   // optional — flags a must-watch player
  "why":  { "en": "...", "zh": "..." },   // optional — one line, only on star players
  "note": { "en": "...", "zh": "..." }    // optional — short role note (subs)
}
```

Player names, numbers, positions, clubs and values are **language-neutral** and
shared by both the Chinese and English pages. Only prose (`style`, `watch`,
`why`, `note`) is bilingual; fill both `en` and `zh`.
