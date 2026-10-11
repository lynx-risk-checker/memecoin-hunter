# Founder Strategy Roadmap — Capital Defense to On-Chain Alpha

**Project:** MEMECOIN HUNTER  
**Branch:** `agent/memecoin-hunter-foundation`  
**Purpose:** Translate the Founder’s four-phase strategy into engineering gates. This is a research and paper-trading plan, not a profit guarantee or a claim that any named trader’s results have been independently verified.

## Core rules

- Preserve capital first; survival overrides the mission target.
- No single wallet, influencer, narrative, or indicator is sufficient to authorize a buy.
- A cluster of linked wallets counts as one economic signal when evidence suggests common funding, coordination, or ownership.
- Small-cap positions must be sized as if the full position could go to zero.
- No averaging down automatically, no revenge trades, no all-in positions, and no chasing after a missed move.
- Take-profit, stop/invalidity conditions, liquidity/exitability and emergency-exit rules must be defined before entry.
- Convert realized tactical profits out of speculative exposure according to a predefined reserve policy; do not assume profits are permanent until realized and safely transferred.
- Live execution remains locked until the full validation gate is passed and the Founder explicitly authorizes a separate live-execution phase.

## Phase 1 — Capital Defense, Legal Rails, and Personal Operating Discipline

### Strategy intent
Establish safe fiat on/off-ramp rails, protect the core reserve, and reduce impulsive decisions before taking speculative exposure.

### Engineering work
- Keep `DRY_RUN=True`, `PAPER_TRADING=True`, and live execution locked by default.
- Add an operational preflight: data health, RPC health, quote freshness, liquidity, wallet-cluster independence, risk limits, daily-loss limit, and kill-switch state.
- Separate accounting buckets in the mission ledger: core reserve, tactical risk budget, fees, realized profits, and airdrop budget.
- Add a hard position-size ceiling and daily-loss halt. Treat speculative token capital as fully losable.
- Add a trade checklist and cooldown / sleep-deprivation self-check as manual operating controls; the bot must never encourage a user to trade because of urgency or a missed move.
- Document custody and key-management boundaries. Never store a seed phrase or private key in source code, browser storage, logs, or the dashboard.
- Fiat rails must use a provider whose current authorization is verified from the official Indonesian regulator’s current list before deposits are made. Do not rely on old Bappebti-only descriptions: OJK announced the transition of crypto-asset regulation and supervision from Bappebti in 2025 and ended the transition in January 2026. Check the latest OJK register at the time of use. See the official [OJK announcement](https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/Nota-Kesepahaman-OJK-Bappebti-2026.aspx) and [OJK crypto-trading regulation page](https://www.ojk.go.id/id/regulasi/Pages/PADK-Nomor-3-Tahun-2026-Penyelenggaraan-Perdagangan-Aset-Keuangan-Digital-termasuk-Aset-Kripto.aspx).
- The Bitcoin/core-reserve idea is a portfolio policy choice, not a bot signal. MEMECOIN HUNTER itself hunts Solana spot tokens and must not silently convert the mission wallet into a BTC portfolio.

### Gate to advance
- Safety defaults and risk-veto tests pass.
- No secrets in source/log/frontend.
- Kill switch demonstrably blocks new paper entries.
- Capital buckets and drawdown limits are visible in the cockpit.
- Regulatory status of any fiat provider is verified from an official, current register.

## Phase 2 — Macro Regime and Liquidity Compass

### Strategy intent
Use macro context to determine whether the overall posture should be normal, defensive, or halted—not to predict prices with certainty.

### Engineering work
- Create a regime panel for BTC trend/volatility, distance from major cycle events, global liquidity proxies, Fed policy/rate data, and institutional-flow data when reliable sources are available.
- Label every macro field with source, observation time, freshness, and missing-data state.
- Treat Bitcoin’s four-year cycle as context, not a deterministic clock. The 2024 halving occurred in April 2024; the next is estimated for 2028, but exact timing and market response are uncertain. See [Bitcoin.org halving overview](https://bitcoin.org/en/halving).
- Define regime states: `NORMAL`, `DEFENSIVE`, `HALTED`. Macro conditions may lower risk budgets or veto new entries, but must never override token-level safety checks.
- Do not label the current market as “winter,” “accumulation,” or “peak” until the selected indicators and their timestamps have been fetched and evaluated. Current regime: **BELUM TERVERIFIKASI**.

### Gate to advance
- Data source and freshness checks exist.
- Regime logic is backtested and does not use future information.
- Missing/stale macro data defaults to conservative behavior.
- Macro signals never override liquidity, manipulation, or risk vetoes.

## Phase 3 — On-Chain Alpha and Asymmetric Opportunity Research

### Strategy intent
Identify early buying pressure and independent, historically credible wallets without blindly copying trades.

### Engineering work
1. **Wallet database:** collect candidate wallets from real confirmed transactions; record provenance, observation window, token universe, and confidence. A target list of 50–100 wallets is a research target, not proof of skill. Expand only when measured data quality supports it.
2. **Wallet performance:** calculate realized PnL only from verified swap semantics and price evidence; report sample size, win rate, expectancy, drawdown, holding time, and fees. Never label a wallet “smart money” on activity alone.
3. **Wallet graph and cluster forensics:** link wallets through shared funding, counterparties, timing, token overlap, and repeated patterns. Mark inferred links as probabilistic. Count correlated wallets as one effective signal.
4. **Alerting:** emit a watch alert when independent candidate wallets accumulate the same token. An alert triggers research; it does not automatically place an order.
5. **Five-minute early-flow analysis:** track volume and transaction acceleration, unique-wallet growth, buy/sell imbalance, liquidity change, market-cap velocity, and the time each observation was captured.
6. **Dev DNA and manipulation:** investigate prior launches, dev selling, liquidity removal, concentrated ownership, synchronized activity, and likely wash/coordinated flows.
7. **Liquidity and exitability:** require current quote/route evidence, estimated price impact, slippage, depth, and a plausible exit before considering a position.
8. **Narrative rotation:** score narrative attention velocity and persistence from available public sources, then require on-chain confirmation. Social attention alone is not a buy signal.
9. **Airdrop farming:** treat this as a separate research track with a capped time/fee budget. Token allocation is uncertain; never count a possible airdrop as guaranteed income or expose the core reserve to speculative protocols.
10. **Decision sequence:** `RADAR → FORENSICS → WALLET/CLUSTER → DEV/MANIPULATION → LIQUIDITY/EXITABILITY → EDGE → RISK VETO → PAPER`. Any missing critical evidence results in `WATCH`, `WAIT`, or `BUY BLOCKED`.

### Gate to advance
- Real confirmed transaction stream is joined to transaction parsing and successful-transaction filtering.
- Swap evidence and realized PnL are independently reviewable.
- Wallet sample size and uncertainty are displayed.
- Cluster double-counting tests pass.
- Real quotes and exitability are available.
- End-to-end paper records are persisted; no synthetic records count as evidence.

## Phase 4 — Narrative Rotation, Exit Discipline, and Wealth Preservation

### Strategy intent
Treat low-cap tokens as tactical trades, not permanent holdings. Protect realized gains and stop trading when edge or market quality disappears.

### Engineering work
- Define pre-entry invalidation, partial take-profit, trailing/exit conditions, time stop, liquidity-drop trigger, dev-sell trigger, manipulation trigger, and emergency exit.
- Recompute exitability before every exit decision; do not assume a token can be sold just because it was bought.
- Record realized PnL after fees, slippage, and price impact. Unrealized gains do not count as preserved wealth.
- Add a post-trade allocation policy: configurable portion of realized gains moves to a reserve bucket only after execution/settlement is confirmed. Asset allocation is a Founder decision, not an automatic promise to buy BTC or traditional assets.
- Rotate only when a new narrative has independently verified flow and adequate exit liquidity. Do not rotate solely because social-media attention is high.
- Stop new entries after daily loss limit, repeated execution/data failures, or a persistent kill-switch event.

### Gate to advance
- At least 100 paper trades, with out-of-sample and walk-forward evaluation, persistent journal, realistic fees/slippage, drawdown analysis, and positive profitability evidence under the project’s validation rules.
- Robustness against failed transactions, stale data, rug scenarios, concentrated clusters, and liquidity withdrawal is tested.
- The Founder reviews the evidence and explicitly authorizes any future live phase. Passing a paper gate still does not guarantee future profit.

## Current evidence checkpoint

The real DexScreener snapshot supplied by the Founder showed:
- Status: `READY`; mode: `PAPER / DRY RUN`; execution: `LOCKED`.
- One radar candidate, `PLAY`, had market cap about US$11,478, reported 5-minute volume US$19,315, 303 transactions in 5 minutes (60.6/min), and **unknown liquidity** (`null`).
- Smart Money, dev, cluster, exitability, and manipulation were all `NOT_EVALUATED`; evidence status was `RADAR_ONLY`.
- Decision remained `WATCH`. This is a successful radar snapshot, not an entry signal and not evidence of profitability.
- Current macro regime: **BELUM TERVERIFIKASI**.
- Real confirmed DEX swap semantics, wallet-level realized PnL, and continuous paper-trading profitability: **BELUM TERVERIFIKASI**.
- The cockpit must not display missing fields as zero or fabricate buy/sell series, wallet counts, or performance metrics.

## Immediate priority order

1. Fix and runtime-verify snapshot URL routing and the mobile cockpit’s real-data rendering.
2. Wire WebSocket log events to `getTransaction`, successful-transaction filtering, parser, and rolling flow metrics.
3. Resolve why real confirmed-transaction discovery returned zero parsed transactions before drawing conclusions about a token.
4. Validate explicit DEX swap semantics and realized PnL from real evidence.
5. Complete cluster independence, liquidity/exitability, and risk-veto integration.
6. Persist real paper decisions and performance metrics over a meaningful sample.
7. Add macro regime data only with source/freshness provenance.
8. Keep live execution locked until the validation gate and Founder authorization.

## Safety and evidence policy

- This roadmap does not guarantee a return, a token allocation, an airdrop, or a particular capital milestone.
- No fabricated market data, synthetic runtime evidence, or invented wallet identities.
- No private keys or seed phrases in source/frontend/logs.
- No live orders and no merge to `main` without explicit Founder approval.
