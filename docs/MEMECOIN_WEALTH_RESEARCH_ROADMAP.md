# MEMECOIN HUNTER — Global Meme-Coin Wealth Research & Roadmap Addendum

**Status:** Research synthesis; implementation not yet verified.  
**Branch:** `agent/memecoin-hunter-foundation`  
**Operating constraints:** DRY RUN + PAPER TRADING; LIVE EXECUTION LOCKED; no private keys in frontend; no merging to `main` without Founder approval.  
**Evidence rule:** Public reporting and public-chain data only. Do not infer secret techniques, ownership, realized profit, or current net worth without evidence.

## 1. Executive conclusion

There is no reliable public census of every meme-coin millionaire/billionaire in every country. Many holders are pseudonymous, wallet balances are not the same as realized profit, and a wallet's apparent mark-to-market value may be impossible to liquidate at quoted prices. The research below therefore records **documented case studies**, not a complete global ranking.

The recurring opportunity pattern is not a single hidden indicator. It combines (a) early access before broad attention, (b) a narrative/community that persists, (c) liquidity and venue access, (d) enough conviction to hold through volatility, and (e) the ability to realize gains. The survivorship bias is severe: public stories emphasize winners and omit the much larger set of losses.

We must not copy reckless leverage or “all-in” behavior. MEMECOIN HUNTER should try to detect measurable early demand and independent participation while controlling downside, execution costs, and exit liquidity.

## 2. Documented case studies

### A. Early Shiba Inu holder — wallet reported as worth billions (2020–2021)

- Public reporting described an Ethereum address that bought roughly $8,000 of SHIB in August 2020 and, by October 2021, had a quoted mark-to-market value reported around $5.7 billion.
- This is an on-chain balance/valuation story, not proof the entire amount was realized or could have been sold near the quoted price without severe slippage.
- Potentially transferable lesson: very early entry into a token before broad adoption can create extreme returns, but the strategy also has extreme tail risk and requires surviving a long period when the asset may be illiquid or nearly worthless.
- Research source: Vice, “An $8K Shiba Inu Investment Turned Into $5.7 Billion. But Can They Cash Out?” https://www.vice.com/en/article/an-dollar8k-shiba-inu-investment-turned-into-dollar57-billion-in-shib/

### B. “Rob,” early SHIB holder and partial profit-taker (reported 2021)

- Fortune reported that a UK warehouse manager researched SHIB, invested about $8,000 in stages, and withdrew roughly $500,000 in May 2021 while retaining exposure. Fortune later reported his remaining holdings were valued above $1 million at that time.
- His reported process included reading the project's “woofpaper,” following the community, and discussing conviction with a small peer group.
- Transferable lesson: study the token's public thesis and community, but independently verify contract, liquidity, ownership/concentration, and actual market activity. Partial realization can convert a paper gain into money outside the volatile asset.
- Caveat: this is one self-reported case and does not establish that holding through every drawdown is optimal.
- Source: Fortune, “A risky Shiba Inu coin bet made this warehouse manager a millionaire” https://fortune.com/2021/11/04/shiba-inu-coin-shib-army-price-increase-warehouse-manager/

### C. Glauber Contessoto — “Dogecoin Millionaire” (2021), later reported PEPE holdings (2025)

- A 2021 New York Times interview transcript describes his path from Reddit/online attention to Dogecoin, an initial small purchase, and then a much larger position reportedly totaling about $250,000, including borrowed/margin funds. His story illustrates narrative discovery and social momentum, but also leverage and concentration risk.
- Decrypt reported in June 2025 that six wallets shared and verified with the outlet held approximately $1.116 million of PEPE, alongside a reported DOGE position. These figures are dated snapshots, not a timeless net-worth statement.
- Transferable lesson: monitor social attention and the transition from niche discussion to broad attention; do not copy debt-financed all-in sizing. Treat public wallet claims as dated evidence and distinguish holdings from realized PnL.
- Sources:
  - The Daily / New York Times interview transcript (May 2021): https://podscripts.co/podcasts/the-daily/a-conversation-with-a-dogecoin-millionaire
  - Decrypt (June 8, 2025): https://decrypt.co/324050/dogecoin-millionaire-pepe-stacking-meme-coins-next

### D. Joe McCann / Asymmetric — institutional-style meme-coin risk process

- Business Insider's 2025 interview reported that McCann preferred established “blue-chip” meme coins with sustained large market caps rather than very new, illiquid tokens; tracked stablecoin flows and momentum; and used strict portfolio risk controls.
- In an interview transcript, he described a concentration policy limiting a position outside the top 20 crypto assets to 2% of fund AUM. This is a fund-specific policy, not a universally correct retail sizing rule.
- Transferable lesson: monitor liquidity/capital rotation, require position limits, and recognize that the best signal is not useful if the position cannot be exited. We should test separate early-stage and established-token strategies rather than treating them as one market.
- Sources:
  - Business Insider (2025): https://www.businessinsider.com/how-hedge-fund-trades-meme-coins-crypto-positions-joe-mccann-2025-2
  - Unchained interview transcript: https://podscripts.co/podcasts/unchained/joe-mccann-on-why-bitcoin-is-the-king-and-memecoins-are-over-for-now-ep-801

### E. Cross-token return analysis — CoinGecko

- CoinGecko's retrospective analysis of ten meme coins found that hypothetical initial investment required to reach $1 million varied enormously by token and entry date. It used historical start dates and all-time-high prices, so it is a hindsight illustration, not a live strategy or a realizable backtest.
- Transferable lesson: the entry window dominates returns, but choosing the winning token in advance is extremely hard. The bot must log failed candidates and losses, not just winners.
- Source: CoinGecko, updated April 30, 2026: https://www.coingecko.com/research/publications/meme-coin-millionaire

## 3. “Hidden” techniques: what is and is not knowable

We cannot honestly reveal private playbooks that have not been published, identify anonymous wallet owners without evidence, or infer secret algorithms from a balance alone. Instead, build a **forensic hypothesis lab** that tests observable behaviors:

1. **Early-entry reconstruction:** compare token launch/first-liquidity time, first buy timestamps, wallet age, first exposure, and subsequent distribution.
2. **Wallet cohort analysis:** track recurring wallets across launches, net quote-asset flow, realized trade PnL only where swaps and quote flows can be reconstructed, and current inventory separately.
3. **Independent-wallet validation:** cluster shared funding, synchronized entries, common counterparties, and transfer relationships so one coordinated group is not counted as many smart-money confirmations.
4. **Liquidity and exit reality:** estimate position-size-dependent impact, route availability, pool depth, fees, priority fees, and adverse price movement; compare quoted price with executable output.
5. **Narrative lead/lag:** measure public attention velocity and persistence, then test whether attention precedes or merely follows on-chain volume and price.
6. **Capital rotation:** monitor stablecoin flows and cross-token / cross-chain flows only where the data source is reliable and timestamps align.
7. **Distribution/exit signatures:** identify early-wallet sell pressure, liquidity removal, concentrated supply, and correlated exits.
8. **Profit realization:** separate token balances and unrealized gains from realized quote-denominated PnL; do not label a wallet “profitable” based on balance snapshots alone.
9. **Survivorship-bias audit:** include dead, rugged, abandoned, and losing tokens in the dataset.
10. **Execution quality:** record signal time, decision time, quote time, fill/assumed fill, slippage, and exit delay. A copy-trading signal that arrives late may be unusable.

## 4. Roadmap integration — add these modules to the existing roadmap (do not replace it)

### R1 — Public Wealth Casebook (research/data governance)
- Maintain a source-backed registry of documented traders, token, dates, public wallet links where attribution is explicitly supported, reported holdings, reported realized sales, and confidence.
- Every claim gets evidence class: `PUBLIC_REPORT`, `ONCHAIN_OBSERVED`, `SELF_REPORTED`, `ESTIMATED_UNREALIZED`, or `UNVERIFIED`.
- Preserve source timestamp and valuation timestamp; never treat current balance as realized profit.
- Acceptance: every case has citations, caveats, and a reproducible evidence trail.

### R2 — Early Wallet & Launch Cohort Engine
- Collect token launch/first-pool/first-trade timing and wallet entry timing from confirmed successful transactions.
- Calculate entry delay, early-wallet concentration, subsequent holding/selling, quote-flow PnL where supported, and wallet repeatability across independent launches.
- Fail closed when transaction coverage is incomplete.

### R3 — Independent Smart-Money Reliability
- Extend the current wallet graph and economic-cluster engine with time-decayed, sample-size-adjusted metrics.
- Score only confirmed trades with quote-asset accounting; track unrealized inventory separately.
- Penalize common funding, synchronized activity, shared counterparties, and likely coordinated clusters.
- Require minimum sample size and out-of-sample validation before a wallet can influence a BUY decision.

### R4 — Narrative Attention / On-Chain Lead-Lag
- Measure public narrative mention velocity, unique authors, persistence, source reliability, and attention concentration.
- Join to on-chain volume, unique buyers, liquidity changes, and price/mcap velocity.
- Backtest whether attention is predictive, lagging, or manipulable; never treat social mentions alone as a BUY signal.

### R5 — Capital Rotation Monitor
- Track reliable stablecoin flows, SOL/ETH and other quote-asset movements, exchange/pool flows, and sector/token rotation where accessible.
- Include timestamp alignment, flow attribution confidence, and source outage handling.
- Distinguish transfers from actual buys/sells.

### R6 — Liquidity-Aware Position Sizing & Exit Simulation
- Size positions from available exit liquidity, expected impact, slippage, fees, volatility, and hard loss limits.
- Simulate partial exits and adverse scenarios; reject positions that cannot be exited within policy limits.
- Keep LIVE EXECUTION LOCKED; begin with replay and paper fills only.

### R7 — Winner/Loser Research and Anti-Survivorship
- Maintain a full cohort of tokens discovered by Radar, including rejects and eventual failures.
- Evaluate precision, recall, false positives, rugs avoided, realized paper expectancy, profit factor, maximum drawdown, turnover, and missed opportunities.
- Split train/test by time and use walk-forward tests; prevent future information leaking into features.

### R8 — Wealth Preservation & Profit-Realization Policy
- Add paper-only rules for staged exits, trailing protection, thesis invalidation, time-based exits, and portfolio-level drawdown stops.
- Track unrealized peak equity versus realized equity and withdrawal/retention scenarios.
- Never force holding solely because a wallet/influencer says they are holding.

### R9 — Strategy Families (separate, never mix without evidence)
- **Early-launch discovery:** tiny initial liquidity and high rug/impact risk; strict fail-closed filters and small paper risk.
- **Narrative acceleration:** requires measured attention acceleration plus independent on-chain confirmation.
- **Smart-money follow-through:** requires independent wallet clusters, confirmed swap semantics, and quote-flow evidence.
- **Established meme momentum:** larger, persistent liquidity/market cap and broader flow signals; separate thresholds and risk policy.
- **Mean-reversion/exit protection:** only if tested; never assume a dip is a bargain.

### R10 — Research-to-Production Gate
- Every strategy must pass data-quality audit, no-lookahead backtest, time-based OOS and walk-forward tests, realistic fees/slippage/latency, at least 100 paper trades, persistent journal, positive out-of-sample expectancy, and risk-limit checks.
- No strategy receives execution permission because it resembles a famous winner.
- Live execution remains locked until Founder explicitly authorizes a separately reviewed phase and all evidence gates pass.

## 5. Implementation order for MEMECOIN HUNTER

1. Fix and verify the existing real snapshot/dashboard query-route issue before judging the cockpit.
2. Complete WebSocket event → confirmed transaction fetch → successful-tx parser → token/quote balance-flow → BUY/SELL evidence → rolling five-minute flow.
3. Complete DEX swap semantics and quote-denominated realized PnL; keep unsupported cases explicitly unverified.
4. Add wallet cohort + independent cluster scoring to existing Smart Money / Edge; do not replace current modules.
5. Add liquidity-aware exit simulation and paper trade journal.
6. Add narrative attention and capital rotation data sources only after their provenance, rate limits, and timestamps are documented.
7. Build the Wealth Casebook and winner/loser cohort dataset; validate strategy families separately.
8. Run realistic replay, OOS and walk-forward validation; do not enable live execution based on backtest alone.

## 6. Hard guardrails

- No leverage/all-in behavior copied from viral anecdotes.
- No fake volume, wash-trading, wallet spoofing, coordinated manipulation, or pump-and-dump tactics.
- No private-key/seed collection, no live signing, no real orders.
- No invented wallet identities, private techniques, PnL, or certainty.
- No BUY if liquidity, exitability, swap semantics, wallet independence, or required evidence is missing.
- Preserve current repo and branch; do not merge `main` without Founder approval.

## 7. Evidence status

This document is a **research roadmap addendum**, not implementation evidence. Each new module remains `BELUM TERVERIFIKASI` until code, tests, real-data smoke output, and paper-trading results are reviewed. Profitability is not established.
