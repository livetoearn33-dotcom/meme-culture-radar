# 🎭 Meme Culture Radar

**Detect real-world meme trends → Match them to on-chain tokens → Safety audit → Act before the crowd.**

Meme Culture Radar bridges the gap between internet culture and on-chain opportunities. It monitors trending topics, viral moments, and cultural signals — then automatically searches Solana for tokens that match those trends, runs security audits, and gives you an actionable report.

## Why?

Every meme coin starts as a cultural moment. A viral video. A politician's gaffe. An anime reference. A TikTok sound. By the time it's on crypto Twitter, you're already late.

Meme Culture Radar catches the signal **at the source** — trending topics, search spikes, social media momentum — and immediately checks if someone has already created a token for it on Solana.

## How It Works

```
Layer 1: Culture Signal Detection
├── X/Twitter trending topics
├── Web search trend spikes
└── Keyword extraction + momentum scoring

        ↓

Layer 2: On-Chain Matching
├── search-tokens-v3 (keyword → token search)
├── launchpad-tokens (pump.fun new launches by keyword)
├── historical-coins (tokens created in last 24h)
└── Cross-reference: culture keyword × token name/symbol

        ↓

Layer 3: Safety + Timing
├── Security audit (honeypot / rug / tax)
├── Dev wallet analysis (rug history, holdings)
├── Market cap stage assessment
├── Smart money detection
└── Actionable verdict: 🟢 Early / 🟡 Heating Up / 🔴 Too Late / ⛔ Unsafe
```

## Features

- **🔍 Trend Detection** — Scans X trending topics and web search trends for emerging memes
- **🪙 Token Matching** — Searches Solana (pump.fun, Raydium, etc.) for tokens matching cultural keywords  
- **🔒 Safety First** — Every matched token gets a full security audit before recommendation
- **📊 Timing Analysis** — Market cap staging tells you if you're early, on time, or late
- **🐋 Smart Money Check** — Sees if notable wallets are already in
- **⛽ Gasless Trading** — Execute via Bitget Wallet's gasless swap (EIP-7702)
- **📡 Daily Reports** — Automated daily scan with actionable intelligence

## Quick Start

```bash
# Clone
git clone https://github.com/Live-2-Earn/meme-culture-radar.git
cd meme-culture-radar

# Install dependencies
pip install requests

# Run a full culture scan
python3 radar.py

# Search for a specific meme/trend
python3 radar.py --keyword "hawk tuah"

# Scan pump.fun for tokens matching a trend
python3 radar.py --keyword "skibidi" --launchpad

# Check a specific token
python3 radar.py --check sol:CONTRACT_ADDRESS
```

## Output Example

```
🎭 MEME CULTURE RADAR — 2026/03/26

📡 3 cultural signals detected:

1. 🔥 "Hawk Tuah" — Trending on X, mentions +340% in 6h
   🪙 On-chain match: $HAWK (Solana)
   📊 MC: $180K | Vol 6h: +520% | Dev holds: 3.2%
   🔒 Security: 🟢 No honeypot | Tax: 0/0%
   ⏱️ Timing: ⚡ EARLY — culture signal strong, MC still low
   
2. 🔥 "Skibidi" — New YouTube season, search volume surging
   🪙 On-chain match: $SKIBIDI (Solana) — 3 tokens found
   📊 Largest MC: $2.1M (already pumped)
   ⏱️ Timing: 🟡 HEATING UP — might be late unless new catalyst

3. 🔥 "Ohio" — TikTok variant going viral
   🪙 On-chain match: None found
   ⏱️ Timing: 👀 WATCHLIST — no token yet, monitor for launch
```

## Architecture

Built on [Bitget Wallet Skill](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill) APIs:

| Feature | API Used |
|---------|----------|
| Token search by keyword | `search-tokens-v3` |
| New token scanning | `launchpad-tokens` |
| Recent launches | `historical-coins` |
| Security audit | `security` |
| Dev analysis | `coin-dev` |
| Market data | `coin-market-info` |
| Swap quotes | `quote` |
| Trending tokens | `rankings` (Hotpicks) |

## For Content Creators

Meme Culture Radar isn't just a trading tool — it's a **content engine**:

- 📝 Daily "Meme Radar" reports → instant content for your crypto community
- 🎨 Spot trends early → create meme derivatives before they peak
- 🛡️ Safety reports → protect your community from scam tokens
- 📊 Data-backed analysis → credible content, not just speculation

## Wallet

Solana: `HpoyMGv39YFC21bwAj88LFKwTrr5aeYMf59uF2Vx42Me`

## License

MIT

## Credits

- [Bitget Wallet Skill](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill) — On-chain data & trading infrastructure
- Built for the [Solana Agent Economy Hackathon: Agent Talent Show](https://x.com/trendsdotfun/status/2031732992255967656)
- Created by [@Live_2_Earn](https://x.com/Live_2_Earn)
