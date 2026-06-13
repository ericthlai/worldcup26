**English** · [简体中文](README.zh-CN.md)

# World Cup 2026 Handbook ⚽

A mobile-first prediction playground for the FIFA World Cup 2026 — Bay Area / US-hosted-matches edition. Rank the groups, project the knockout bracket, and watch live win probabilities from a real prediction market.

**▶ Play it:**
- 🇬🇧 English — https://ericthlai.github.io/worldcup26/en/
- 🇨🇳 中文 — https://ericthlai.github.io/worldcup26/

> Open it and make your picks — everything saves automatically in your own browser. No login, nothing uploaded. For fun only.

## Features
- **Fixtures** — all 52 US-hosted group matches, each with a live **win / draw / win** probability bar from the [Polymarket](https://polymarket.com) prediction market
- **Groups** — tap teams to rank each group; top 2 advance, 3rd enters the best-third pool
- **Bracket** — interactive knockout bracket that auto-fills from your group rankings, plus a live **title-odds board**
- **Share** — generate a shareable prediction-card image

## Tech
Single static page, no build step: [Preact](https://preactjs.com) + [HTM](https://github.com/developit/htm) loaded from local files, predictions stored in `localStorage`, live odds fetched client-side from the public Polymarket Gamma API. Hosted free on GitHub Pages.

The English (`/en/`) and Chinese (`/`) versions share the same logic and the same saved predictions; a footer link switches between them.

## Run locally
```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Disclaimer
Kickoff times per the official FIFA app. The percentages are *implied probabilities* from the Polymarket betting market, shown for entertainment only.
