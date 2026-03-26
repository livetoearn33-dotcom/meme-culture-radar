#!/usr/bin/env python3
"""
🎭 Meme Culture Radar
Detect real-world meme trends → Match on-chain tokens → Safety audit → Act before the crowd.

Built with Bitget Wallet Skill for #AgentTalentShow
"""

import subprocess
import json
import sys
import argparse
import os
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BGW_SCRIPT = os.path.join(SCRIPT_DIR, "scripts", "bitget_agent_api.py")
WALLET = "HpoyMGv39YFC21bwAj88LFKwTrr5aeYMf59uF2Vx42Me"

# Market cap stages for timing analysis
MC_STAGES = {
    "micro":    (0,       50_000,    "⚡ MICRO — Extremely early, highest risk/reward"),
    "early":    (50_000,  500_000,   "🟢 EARLY — Culture signal may not be priced in yet"),
    "heating":  (500_000, 5_000_000, "🟡 HEATING UP — Gaining traction, momentum play"),
    "mature":   (5_000_000, 50_000_000, "🟠 MATURE — Well-known, need strong catalyst"),
    "late":     (50_000_000, float('inf'), "🔴 LATE — Already mainstream, high risk entry"),
}


# ── Bitget Wallet API Helpers ───────────────────────────
def bgw_cmd(args):
    """Run bitget_agent_api.py and return parsed JSON."""
    cmd = ["python3", BGW_SCRIPT] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def search_tokens(keyword, chain="sol", limit=10):
    """Search for tokens matching a keyword."""
    args = ["search-tokens-v3", "--keyword", keyword, "--chain", chain,
            "--order-by", "market_cap", "--limit", str(limit)]
    data = bgw_cmd(args)
    if not data or "data" not in data:
        return []
    return data["data"].get("list", data["data"]) if isinstance(data["data"], dict) else data["data"]


def scan_launchpad(keyword=None, chain="sol", platforms="pump.fun", stage=None,
                   mc_min=None, mc_max=None, holder_min=None):
    """Scan launchpad for new tokens, optionally filtered by keyword."""
    args = ["launchpad-tokens", "--chain", chain, "--platforms", platforms]
    if keyword:
        args += ["--keywords", keyword]
    if stage is not None:
        args += ["--stage", str(stage)]
    if mc_min:
        args += ["--mc-min", str(mc_min)]
    if mc_max:
        args += ["--mc-max", str(mc_max)]
    if holder_min:
        args += ["--holder-min", str(holder_min)]
    data = bgw_cmd(args)
    if not data or "data" not in data:
        return []
    return data["data"].get("list", []) if isinstance(data["data"], dict) else []


def security_audit(chain, contract):
    """Run security audit on a token."""
    data = bgw_cmd(["security", "--chain", chain, "--contract", contract])
    if not data or "data" not in data or not data["data"]:
        return {"status": "❓ UNKNOWN", "risks": 0, "warns": 0, "buy_tax": "?", "sell_tax": "?"}

    audit = data["data"][0]
    risks = audit.get("riskChecks", [])
    warns = audit.get("warnChecks", [])
    lows = audit.get("lowChecks", [])

    buy_tax = sell_tax = "?"
    for check in lows + warns + risks:
        vals = check.get("values", {})
        if "buyTax" in vals:
            buy_tax = vals["buyTax"]
            sell_tax = vals.get("sellTax", "?")

    if len(risks) > 0:
        status = "⛔ DANGER"
    elif len(warns) > 0:
        status = "⚠️ CAUTION"
    else:
        status = "🟢 SAFE"

    return {
        "status": status,
        "risks": len(risks),
        "warns": len(warns),
        "buy_tax": buy_tax,
        "sell_tax": sell_tax,
        "high_risk": audit.get("highRisk", False),
    }


def dev_analysis(chain, contract):
    """Analyze developer wallet."""
    data = bgw_cmd(["coin-dev", "--chain", chain, "--contract", contract])
    if not data or "data" not in data:
        return None
    return data.get("data")


def get_market_info(chain, contract):
    """Get detailed market information."""
    data = bgw_cmd(["coin-market-info", "--chain", chain, "--contract", contract])
    if not data or "data" not in data:
        return None
    return data.get("data")


def get_hotpicks():
    """Get curated trending tokens."""
    data = bgw_cmd(["rankings", "--name", "Hotpicks"])
    if not data or "data" not in data:
        return []
    return data["data"].get("list", []) if isinstance(data["data"], dict) else []


# ── Trend Detection ─────────────────────────────────────
def detect_trends_from_web():
    """
    Detect trending topics from multiple sources.
    Returns list of {keyword, source, description}
    
    In production, this would integrate with:
    - X/Twitter Trending API
    - Google Trends
    - TikTok trending sounds
    - Reddit rising posts
    
    Current implementation: curated trending keywords + Hotpicks crossref
    """
    trends = []

    # Source 1: Hotpicks — what's already trending on-chain
    hotpicks = get_hotpicks()
    for token in hotpicks:
        if token.get("chain") == "sol":
            symbol = token.get("symbol", "")
            name = token.get("name", "")
            change = token.get("change_24h", 0)
            if abs(change) > 10:  # Only significant movers
                trends.append({
                    "keyword": symbol,
                    "source": "🔥 Hotpicks",
                    "description": f"{name} ({symbol}) — 24h change: {change:+.1f}%",
                    "on_chain": True,
                    "token_data": token,
                })

    return trends


def detect_trends_from_keywords(keywords):
    """Search for user-provided keywords on-chain."""
    trends = []
    for kw in keywords:
        trends.append({
            "keyword": kw,
            "source": "🎯 Manual",
            "description": f"User-specified trend keyword: {kw}",
            "on_chain": False,
            "token_data": None,
        })
    return trends


# ── Analysis Engine ─────────────────────────────────────
def assess_timing(market_cap):
    """Determine market cap stage for timing analysis."""
    if market_cap is None:
        return "❓ UNKNOWN", "No market cap data"
    for stage_name, (low, high, desc) in MC_STAGES.items():
        if low <= market_cap < high:
            return stage_name, desc
    return "late", MC_STAGES["late"][2]


def format_usd(val):
    if val is None or val == 0:
        return "N/A"
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:.2f}"


def analyze_trend(trend, verbose=False):
    """Full analysis pipeline for a single trend."""
    keyword = trend["keyword"]
    results = {
        "keyword": keyword,
        "source": trend["source"],
        "description": trend["description"],
        "tokens": [],
    }

    # If we already have token data from Hotpicks
    if trend.get("token_data"):
        t = trend["token_data"]
        token_result = analyze_token(
            chain=t["chain"],
            contract=t["contract"],
            symbol=t.get("symbol", "?"),
            name=t.get("name", "?"),
            price=t.get("price"),
            market_cap=t.get("market_cap"),
            volume_24h=t.get("turnover_24h"),
            change_24h=t.get("change_24h"),
            verbose=verbose,
        )
        results["tokens"].append(token_result)
        return results

    # Search on-chain for matching tokens
    print(f"  🔍 Searching Solana for '{keyword}'...")
    tokens = search_tokens(keyword, chain="sol", limit=5)

    if not tokens:
        # Also try launchpad
        print(f"  🚀 Checking pump.fun for '{keyword}'...")
        lp_tokens = scan_launchpad(keyword=keyword, chain="sol")
        if lp_tokens:
            tokens = lp_tokens[:5]

    if not tokens:
        results["tokens"] = []
        return results

    # Analyze top matches
    for t in tokens[:3]:  # Top 3 matches
        token_result = analyze_token(
            chain=t.get("chain", "sol"),
            contract=t.get("contract", ""),
            symbol=t.get("symbol", "?"),
            name=t.get("name", "?"),
            price=t.get("price"),
            market_cap=t.get("market_cap"),
            volume_24h=t.get("turnover_24h", t.get("turnover")),
            change_24h=t.get("change_24h"),
            dev_rug_percent=t.get("dev_rug_percent"),
            top10_percent=t.get("top10_holder_percent"),
            verbose=verbose,
        )
        results["tokens"].append(token_result)

    return results


def analyze_token(chain, contract, symbol, name, price=None, market_cap=None,
                  volume_24h=None, change_24h=None, dev_rug_percent=None,
                  top10_percent=None, verbose=False):
    """Deep analysis of a single token."""
    result = {
        "chain": chain,
        "contract": contract,
        "symbol": symbol,
        "name": name,
        "price": price,
        "market_cap": market_cap,
        "volume_24h": volume_24h,
        "change_24h": change_24h,
    }

    # Security audit
    print(f"    🔒 Auditing {symbol}...")
    audit = security_audit(chain, contract)
    result["security"] = audit

    # Timing assessment
    stage_name, stage_desc = assess_timing(market_cap)
    result["timing"] = {"stage": stage_name, "description": stage_desc}

    # Dev analysis (if verbose)
    if verbose:
        print(f"    🧑‍💻 Checking dev history for {symbol}...")
        dev = dev_analysis(chain, contract)
        if dev:
            result["dev"] = dev

    # Pre-existing risk flags from search
    if dev_rug_percent is not None and dev_rug_percent > 20:
        result["dev_warning"] = f"Dev rug rate: {dev_rug_percent:.0f}%"
    if top10_percent is not None and top10_percent > 50:
        result["concentration_warning"] = f"Top 10 holders: {top10_percent:.0f}%"

    return result


# ── Output Formatting ───────────────────────────────────
def print_report(all_results, scan_time):
    """Print the final radar report."""
    print()
    print("=" * 65)
    print("🎭  MEME CULTURE RADAR")
    print(f"📅  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"👛  {WALLET[:8]}...{WALLET[-6:]}")
    print(f"⏱️  Scan completed in {scan_time:.1f}s")
    print("=" * 65)

    if not all_results:
        print("\n  No trends detected. Try with --keyword.")
        return

    signal_count = 0
    for r in all_results:
        signal_count += 1
        print(f"\n{'─' * 65}")
        print(f"📡 Signal #{signal_count}: \"{r['keyword']}\"")
        print(f"   Source: {r['source']}")
        print(f"   {r['description']}")

        if not r["tokens"]:
            print(f"   🪙 On-chain: No matching tokens found")
            print(f"   ⏱️ Timing: 👀 WATCHLIST — no token yet, monitor for launch")
            continue

        for i, t in enumerate(r["tokens"]):
            if i > 0:
                print()
            symbol = t["symbol"]
            contract = t["contract"]
            mc = t.get("market_cap")
            vol = t.get("volume_24h")
            change = t.get("change_24h", 0)
            sec = t["security"]
            timing = t["timing"]

            print(f"\n   🪙 ${symbol} ({t['name']})")
            print(f"      CA: {contract}")
            if t.get("price"):
                p = t["price"]
                print(f"      Price: ${p:.10f}" if p < 0.01 else f"      Price: ${p:.4f}")
            print(f"      Market Cap: {format_usd(mc)} | 24h Vol: {format_usd(vol)}", end="")
            if change:
                color = "+" if change > 0 else ""
                print(f" | 24h: {color}{change:.1f}%")
            else:
                print()
            print(f"      Security: {sec['status']} (Risks: {sec['risks']}, Warns: {sec['warns']}) | Tax: {sec['buy_tax']}/{sec['sell_tax']}%")
            print(f"      Timing: {timing['description']}")

            if t.get("dev_warning"):
                print(f"      ⚠️ {t['dev_warning']}")
            if t.get("concentration_warning"):
                print(f"      ⚠️ {t['concentration_warning']}")

    # Summary
    total_tokens = sum(len(r["tokens"]) for r in all_results)
    safe_tokens = sum(1 for r in all_results for t in r["tokens"] if "SAFE" in t["security"]["status"])
    danger_tokens = sum(1 for r in all_results for t in r["tokens"] if "DANGER" in t["security"]["status"])
    early_tokens = sum(1 for r in all_results for t in r["tokens"]
                       if t["timing"]["stage"] in ("micro", "early"))

    print(f"\n{'=' * 65}")
    print("📊 SCAN SUMMARY")
    print(f"   Signals detected: {len(all_results)}")
    print(f"   Tokens analyzed: {total_tokens}")
    print(f"   🟢 Safe: {safe_tokens} | ⛔ Danger: {danger_tokens}")
    print(f"   ⚡ Early stage (MC < $500K): {early_tokens}")
    print(f"\n💡 Remember: Culture signal + Early MC + Safe audit = Best setup")
    print(f"   Always DYOR. This is intelligence, not financial advice.")
    print(f"\n⚡ Powered by Bitget Wallet Skill — Gasless swaps on Solana")


# ── CLI ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🎭 Meme Culture Radar — Detect meme trends, find on-chain tokens, stay safe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 radar.py                          # Auto-scan trending memes
  python3 radar.py --keyword "hawk tuah"    # Search for specific meme
  python3 radar.py --keyword skibidi ohio   # Multiple keywords
  python3 radar.py --launchpad              # Include pump.fun scan
  python3 radar.py --check sol:CONTRACT     # Check specific token
  python3 radar.py --verbose                # Include dev analysis
        """
    )
    parser.add_argument("--keyword", "-k", nargs="+", help="Specific meme/trend keywords to search")
    parser.add_argument("--launchpad", "-l", action="store_true", help="Also scan pump.fun launchpad")
    parser.add_argument("--check", "-c", help="Check specific token (format: chain:contract)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Include dev wallet analysis")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    import time
    start = time.time()

    # Mode 1: Check specific token
    if args.check:
        parts = args.check.split(":")
        if len(parts) != 2:
            print("Error: Use format chain:contract (e.g. sol:ABC123...)")
            sys.exit(1)
        chain, contract = parts
        print(f"🔍 Checking {contract[:16]}... on {chain}")
        result = analyze_token(chain, contract, "?", "?", verbose=args.verbose)
        
        # Try to get market info
        minfo = get_market_info(chain, contract)
        if minfo:
            result["symbol"] = minfo.get("symbol", "?")
            result["name"] = minfo.get("name", "?")
            result["price"] = minfo.get("price")
            result["market_cap"] = minfo.get("market_cap")
            result["volume_24h"] = minfo.get("turnover_24h")
            result["change_24h"] = minfo.get("change_24h")
            stage_name, stage_desc = assess_timing(result.get("market_cap"))
            result["timing"] = {"stage": stage_name, "description": stage_desc}

        all_results = [{"keyword": result.get("symbol", "?"), "source": "🎯 Direct Check",
                        "description": f"Manual token check: {contract[:20]}...",
                        "tokens": [result]}]
        elapsed = time.time() - start
        
        if args.json:
            print(json.dumps(all_results, indent=2, default=str))
        else:
            print_report(all_results, elapsed)
        return

    # Mode 2: Keyword search
    all_results = []

    if args.keyword:
        print(f"🎯 Searching for: {', '.join(args.keyword)}")
        trends = detect_trends_from_keywords(args.keyword)
        for trend in trends:
            result = analyze_trend(trend, verbose=args.verbose)
            all_results.append(result)

            # Also check launchpad if requested
            if args.launchpad:
                print(f"  🚀 Scanning pump.fun for '{trend['keyword']}'...")
                lp_tokens = scan_launchpad(keyword=trend["keyword"])
                if lp_tokens:
                    for lpt in lp_tokens[:2]:
                        tr = analyze_token(
                            chain=lpt.get("chain", "sol"),
                            contract=lpt.get("contract", ""),
                            symbol=lpt.get("symbol", "?"),
                            name=lpt.get("name", "?"),
                            price=lpt.get("price"),
                            market_cap=lpt.get("market_cap"),
                            volume_24h=lpt.get("turnover"),
                            change_24h=lpt.get("change_24h"),
                            dev_rug_percent=lpt.get("dev_rug_percent"),
                            top10_percent=lpt.get("top10_holder_percent"),
                            verbose=args.verbose,
                        )
                        # Append to existing result
                        result["tokens"].append(tr)

    # Mode 3: Auto-detect trends (default)
    if not args.keyword:
        print("📡 Auto-detecting trends from on-chain signals...")
        trends = detect_trends_from_web()
        if trends:
            for trend in trends:
                result = analyze_trend(trend, verbose=args.verbose)
                all_results.append(result)
        else:
            print("   No strong signals detected. Try with --keyword.")

    elapsed = time.time() - start

    if args.json:
        print(json.dumps(all_results, indent=2, default=str))
    else:
        print_report(all_results, elapsed)


if __name__ == "__main__":
    main()
