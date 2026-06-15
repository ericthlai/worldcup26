# Squad data — QC report

**Date:** 2026-06-14
**Scope:** all 48 World Cup 2026 squads in `squads.json` (768 players: 48 × 11 projected XI + ~5 key subs).

## Method

1. **Gather** — 48 independent research agents (one per team) sourced each squad from
   the official FIFA 26-man lists, Transfermarkt (values) and June-2026 lineup previews.
2. **Build validation** (`build_squads.py`) — schema sanitize + checks: every XI = 11
   players, no duplicate shirt numbers within a team, all positions valid, all club
   countries 3-letter. **Result: 0 warnings.**
3. **Broad audit** — all required fields populated, market values in a sane range
   (€0.05M–€200M), every team has ≥1 star player with a reason. **Result: clean.**
4. **Independent verification** — a *second*, independent set of 48 agents re-researched
   each team's official 26-man squad (numbers, clubs, manager) from scratch. Their output
   (`raw/qc.json`) was diffed against our data by player name (`qc_diff.py`).
5. **Adjudication** — every disagreement was resolved against authoritative sources
   (footyheadlines, Sky Sports, club/FA announcements). The verifier is a second opinion,
   **not** ground truth — see below.

## Findings

| Category | Count | Verdict |
|---|---|---|
| Manager mismatches | 0 / 48 | ✅ all coaches consistent |
| Shirt-number — confirmed OUR error (fixed) | 2 | ✅ fixed (Scotland) |
| Shirt-number — confirmed VERIFIER error (our data correct) | 15 | ✅ no change |
| Shirt-number — unresolved, low-stakes | 6 | ⚠️ flagged below |
| "Missing from squad" flags | 28 | ✅ all false positives (transliteration / verifier gaps) |
| Formation differences | 19 | ➖ verifier defaulted to generic shapes; ours more specific |

### Fixed (authoritatively confirmed)
- **Scotland** — Nathan Patterson `#9 → #22`, George Hirst `#24 → #18`
  (source: Sky Sports / The Scotsman official squad-number announcement).

### Confirmed correct in our data (verifier was wrong)
- **Netherlands** — the verifier reported a completely different number scheme (14 players).
  Cross-checked against footyheadlines: **our numbers are correct** (Depay 19, Gakpo 18,
  De Jong 10, Dumfries 6, Van Dijk 4, Timber 2 …). No change.
- **Argentina** — Lautaro Martínez is **#22** (verifier said #6). No change.
- **Türkiye / Saudi Arabia "missing" flags** — players like Kenan Yıldız, Salem Al-Dawsari,
  Firas Al-Buraikan are genuinely in the squads; the verifier's lists were incomplete or
  used different romanizations. No change.

### Unresolved (low confidence, low stakes — left as gathered)
These single shirt numbers were flagged by the verifier but **not** authoritatively
confirmed either way; we keep the gathered (official-list-sourced) value rather than trust
the demonstrably-noisy verifier. Worth a manual check if precision matters:

| Team | Player | Ours | Verifier |
|---|---|---|---|
| Türkiye | Mert Müldür (starter) | 23 | 18 |
| Qatar | Boualem Khoukhi | 16 | 13 |
| Qatar | Assim Madibo | 23 | 16 |
| DR Congo | Arthur Masuaku | 11 | 26 |
| Curaçao | Deveron Fonville | 13 | 24 |
| Curaçao | Tahith Chong | 22 | 21 |

To resolve later: confirm the number against the team's official squad-number announcement,
edit `squads.json`, run `python build_squads.py`.

## Rendering QC

Verified in-browser (mobile 375px + desktop), both **中文** and **English** pages:
schedule rows open a match detail with **both** full squads (numbers, EN names, positions,
clubs, € values, tactics, who-to-watch); the **Teams** tab browses all **48/48**; single-team
detail renders correctly; overlay scrolls; 5-tab nav fits without overflow; no console errors;
no language leakage on the English page.

## Confidence

High on structure, managers, clubs, positions, star players and tactics; high on shirt numbers
for the major teams (spot-verified). Six bench/role-player numbers remain unconfirmed (listed
above). Market values are Transfermarkt-grade snapshots and will drift over time.
