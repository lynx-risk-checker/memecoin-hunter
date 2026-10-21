# Roadmap Audit — MEMECOIN HUNTER

Audit basis: branch `agent/memecoin-hunter-foundation`, current source/tests, and Founder-reported real runtime smoke results. Exact runtime numeric outputs were not independently inspected in this chat.

## Phase status

| Phase | Area | Status |
|---|---|---|
| 0 | Foundation / safety | VERIFIED (unit) |
| 1 | Real Solana data | VERIFIED for RPC/DEX real smoke; continual evidence BELUM TERVERIFIKASI |
| 2 | Token Radar | VERIFIED (unit + prior real smoke) |
| 3 | 5-minute forensics | PARTIAL — native on-chain block-time flow engine exists/unit-tested; continual real 5m dataset evidence BELUM TERVERIFIKASI |
| 4 | Dev DNA | PARTIAL — evidence-scored developer DNA model implemented/tested; runtime attribution/history still requires real transaction evidence |
| 5 | Smart Money / wallet intelligence | PARTIAL — wallet history, FIFO reconstruction, holding time, price-aware accounting, swap evidence, instruction evidence, execution-price accounting, and explicit DEX semantic evidence are implemented/tested; real confirmed DEX swap semantics and real-wallet PnL remain BELUM TERVERIFIKASI |
| 6 | Wallet graph / economic clusters | PARTIAL — real smoke pipeline reported PASS; economic ownership inference and double-counting hardening remain incomplete |
| 7 | Manipulation / insider detection | PARTIAL — real smoke pipeline reported PASS; substantive manipulation ground-truth validation BELUM TERVERIFIKASI |
| 8 | Liquidity / exitability | PARTIAL — basic ratio engine plus route-aware quote contract implemented/tested; real quote provider and exit simulation remain to be wired |
| 9 | Narrative / social intelligence | PARTIAL — scoring plus source/observation ingestion contract implemented/tested; live public-feed adapters remain |
| 10 | Asymmetric Edge | PARTIAL — edge→risk→protection path now has a single orchestrator; full live-data orchestration remains to be wired |
| 11 | Risk veto / decision | PARTIAL — integrated pipeline, decision snapshot, and persistent kill-switch latch implemented/tested; runtime wiring remains |
| 12 | Paper trading / journal | PARTIAL — persistent JSONL journal and journal→metrics adapter implemented/tested; long-run real-market evidence missing |
| 13 | Capital Mission | PARTIAL — target definitions/runtime evaluation plus persistent mission-state store implemented/tested; continual evidence remains |
| 14 | Mobile PWA cockpit | PARTIAL — mobile PWA shell and snapshot viewer implemented; production hosting/auth/operational UX remain |
| 15 | Execution engine | SAFETY LOCK VERIFIED; live execution intentionally not built |
| 16 | Exit / emergency kill switch | PARTIAL — protection/exit evaluation, persistent kill switch, and position-monitor integration are implemented/tested; live runtime stream integration remains |
| 17 | Adaptive research | PARTIAL — signal outcome grouping/scoring plus positive-rate evidence implemented/tested; persistent research loop remains |
| 18 | Full validation | PARTIAL — explicit validation gate implemented/tested; real OOS/walk-forward evidence gate remains |
| 19 | Small live capital | NOT READY |
| 20 | Mission mode | NOT BUILT |

## Evidence boundary

The Founder reported a successful real Solana wallet-intelligence smoke run reaching real transaction parsing and completion. This supports runtime plumbing. Exact wallet/cluster/manipulation numeric values remain **BELUM TERVERIFIKASI** here.

A smoke pass is not evidence of profitability, common economic ownership, manipulation ground truth, or live-trading readiness.

## Immediate engineering priority

1. Verify real confirmed DEX swaps end-to-end: explicit program semantics → execution price → realized PnL → Smart Money reliability. A real-RPC smoke script now exists; it refuses to promote a swap without an explicit operator-supplied DEX program specification.
2. Harden cluster aggregation against correlated-signal double counting.
3. Build route-aware liquidity/exitability with real quotes.
4. Add persistent paper journal and connect performance metrics.
5. Wire the production orchestrator to the complete real-data chain: radar → forensics → wallet/cluster → manipulation → liquidity → edge → risk → paper → protection.
6. Keep live execution locked.
7. Harden edge quality with independent-signal weighting, correlated-wallet penalties, and real quote/exitability evidence before any BUY_ALLOWED decision is treated as actionable.

## Latest engineering work

- Added `scripts/smoke_real_dex_swap_semantics.py` to inspect confirmed real Solana transactions and join balance-flow candidates with explicitly supplied DEX program semantics.
- The script requires `SOLANA_RPC_URL`, wallet address, target/quote mints, DEX name, and explicit DEX program IDs. It does not invent program IDs or discriminators.
- Jupiter's current official Swap API documentation confirms Swap V2 is the current API and distinguishes the Meta-Aggregator from the Router; this project has not hard-coded Jupiter program semantics without transaction-level verification. citeturn1view0
- Solana's official RPC documentation confirms `getTransaction` exposes confirmed transaction metadata, instructions, inner instructions, logs, and balance deltas needed for forensic reconstruction. citeturn0search1turn0search2

## Safety

- No private keys in source/frontend.
- No real order placement.
- No merge to `main` without explicit Founder approval.
- Fixtures are not runtime evidence.
- No profitability claim without out-of-sample/paper evidence.

## Current checkpoint

The branch is now materially ahead of the original foundation and continues to advance and is not behind. The latest completed structural work includes persistent paper journaling, route-quote validation, a production decision orchestrator, developer DNA scoring, adaptive research scoring, an explicit validation gate, and a mobile PWA cockpit shell. These are implementation milestones; they do not substitute for real-market runtime evidence.


## Founder checkpoint — 2026-10-12

### Repository audit

- Working branch: `agent/memecoin-hunter-foundation`; changes remain isolated from `main`.
- Latest previously recorded foundation checkpoint: `ccec695b4782ce54ba05fa1415b0292d793d0887`.
- Branch had advanced beyond that checkpoint; the prior reported dashboard commit `63ed88f343f67f47c7e9b09a9d9deca2204250e9` loads the versioned `web/app.js` asset.
- Combined status for `63ed88f343f67f47c7e9b09a9d9deca2204250e9` reported `success` from the Railway-linked check. This is not proof that the deployed service has the required runtime variables.
- Current source `src/web_snapshot.py` already uses `urlsplit(self.path).path`, so query parameters on `/snapshot?ui=...&t=...` are stripped before route matching. Do not reapply the old query-string fix.

### Verified blocker

- `build_snapshot()` reads `SOLANA_RPC_URL` from the process environment. If it is empty, the response intentionally reports `sources.solana_rpc.status = NOT_CONFIGURED` while the DEX radar may still report `READY`.
- The repository's `.env.example` leaves `SOLANA_RPC_URL=` blank by design. A successful Codespaces smoke test does not populate the Railway service environment.
- Therefore, Solana RPC configuration on the actual iPhone-serving deployment remains **BELUM TERVERIFIKASI / reported NOT_CONFIGURED** until the deployment's runtime variable is set and the public snapshot reports RPC `CONNECTED` with a real slot.
- Never put the RPC URL/API key in source code, dashboard output, commits, or this document. Configure it as a secret/environment variable in the hosting provider.

### Change in this checkpoint

- Added regression test `test_snapshot_route_accepts_ui_query_parameters` to guard the existing query-aware route behavior.
- Commit: `7ca5609b61a6eb3f291c59f4b2a6c22aa0b7aa1a`.
- Test status for this new commit: **BELUM TERVERIFIKASI** until GitHub Actions completes or Founder runs `pytest -q` in Codespaces.

### Next runtime proof required

1. Configure `SOLANA_RPC_URL` in the Railway service that serves the iPhone dashboard, without exposing the value.
2. Redeploy/restart that service if the host does not automatically redeploy environment changes.
3. Request the public `/snapshot` endpoint and verify `sources.solana_rpc.status = CONNECTED` plus a numeric `slot`.
4. Confirm the iPhone dashboard reflects that same result. Until these checks pass, production RPC is not verified.


### Public snapshot supplied by Founder (2026-10-12 review)

- The supplied response has `observed_at = 2026-10-08T18:14:42.356331+00:00`, only `source: dexscreener`, and no top-level `sources.solana_rpc` object.
- It reports candidate decision `WATCH`, while the current branch snapshot builder emits `decision: WAIT` and includes a top-level `sources` map for DEX Screener, Solana RPC, and watched wallets.
- This schema mismatch is evidence that the supplied response is from an older code path/version or a different server instance; the exact deployment source is **BELUM TERVERIFIKASI**. Do not assume the current branch is what the iPhone endpoint is serving.
- The next check must therefore verify both deployment version and runtime configuration: current-format snapshot + RPC `CONNECTED` + numeric slot. Until then, production end-to-end status remains **BELUM TERVERIFIKASI**.


---

# MASTER ROADMAP — FOUNDER CHECKPOINT (Technical + Strategy)
Updated: 2026-10-13
Scope: additive extension of the existing architecture. This roadmap does not reset, replace, or authorize removal of existing modules.

## 1. Strategic intelligence roles

These are strategy/research roles in the Founder architecture. They must become measurable, source-backed signals before they can affect decisions; names or narratives alone are not evidence.

| Strategic role | Mission | Required measurable inputs | Status |
|---|---|---|---|
| GABRIEL REY — Capital Defense + Macro Regime | Protect capital and classify market regime | Market breadth/conditions, volatility and liquidity regime, drawdown, system health, evidence freshness, risk limits | ROADMAP; full live-data integration BELUM TERVERIFIKASI |
| ORANGIE — Attention Velocity + Early Discovery | Find early opportunities and detect attention/narrative acceleration | Token discovery timestamps, rate of change in activity, volume/transaction acceleration, sourced attention observations, narrative rotation | ROADMAP; live attention-feed adapters and validated lead signal BELUM TERVERIFIKASI |
| BEVAN PRAMUDITO — Smart Money + Wallet Graph + Narrative Rotation | Track wallet activity and independently corroborate capital/narrative rotation | Confirmed swaps, wallet history, realized PnL quality, funding/economic links, wallet independence, narrative observations and timing | PARTIAL foundations exist; production-grade independent validation BELUM TERVERIFIKASI |

Regime output: AGGRESSIVE / NORMAL / DEFENSIVE / HALTED. Capital-defense and Risk Veto rules always override discovery, narrative, wallet, edge, or capital-mission signals.

## 2. Full technical pipeline and checkpoint

| # | Module | Required outcome | Current checkpoint |
|---:|---|---|---|
| 1 | Solana + DEX data | RPC, DexScreener, WebSocket, timestamps, health and source provenance | RPC/DEX foundation exists; production RPC configuration and continual runtime proof BELUM TERVERIFIKASI |
| 2 | Token Radar | Pair discovery, market cap, liquidity, volume 5M/1H, TXNS 5M/1H, TXNS/min | Implemented; previous tests and smoke evidence reported |
| 3 | Early-Flow Engine | Detect changes in activity and buy/sell pressure from observed data | Partial; full streaming and end-to-end signal evidence BELUM TERVERIFIKASI |
| 4 | 5-Minute Forensics | T+0, 30s, 1m, 3m, 5m; buyer/seller acceleration, volume and momentum | Core/batch foundations exist; continuous real-data windows BELUM TERVERIFIKASI |
| 5 | Dev DNA | Developer history, funding, sell patterns, token/security risk | Partial scoring/model; real attribution and history evidence required |
| 6 | Smart Money Engine | Wallet history, trade outcomes, early entry, reliable realized PnL | Partial wallet/swap foundations; real confirmed-swap PnL BELUM TERVERIFIKASI |
| 7 | Wallet Graph Engine | Wallet ↔ wallet ↔ token ↔ developer ↔ funding | Partial wallet/economic-link components; production graph and ownership evidence BELUM TERVERIFIKASI |
| 8 | Cluster / Manipulation | Shared funding, coordination, fake diversity, correlated-signal penalties | Partial; ground-truth validation and double-counting resistance incomplete |
| 9 | Liquidity / Exitability | Real quotes, depth/price impact, slippage and exit simulation | Quote contract/basic engine exist; live quote provider and end-to-end exitability BELUM TERVERIFIKASI |
| 10 | Narrative Engine | Sourced social trends, attention velocity and on-chain confirmation | Scoring/ingestion contract exists; live public-feed adapters and lead–lag validation BELUM TERVERIFIKASI |
| 11 | Asymmetric Edge | Flow + Smart Money + Dev DNA + Cluster + Liquidity + Narrative + Momentum + EV | Partial orchestrator/decision path exists; complete live-data integration BELUM TERVERIFIKASI |
| 12 | Risk Veto | EV, developer risk, manipulation, liquidity, slippage, position and loss limits | Core safety logic exists; complete runtime wiring and end-to-end tests remain |
| 13 | Paper Trading + Journal | Entry/exit, PnL, slippage, source evidence and reproducible journal | Partial persistent journal foundations; long-run end-to-end paper evidence insufficient |
| 14 | Exit + Protection | Profit/stop rules, liquidity-aware exit and emergency exit | Partial protection/exit logic; continuous market-data integration BELUM TERVERIFIKASI |
| 15 | Validation Gate | 100+ paper trades, out-of-sample, walk-forward, drawdown and EV | Gate implementation exists; evidence threshold not met |
| 16 | Wealth Preservation / Capital Mission | Regime-aware capital defense, mission progress and adaptive research | Mission foundations exist; continual evidence and wealth-casebook loop remain |
| 17 | Mobile Intelligence Cockpit | iPhone PWA, public HTTPS backend, real snapshot and transparent source status | UI shell exists; production version/runtime connection and required visual modules need verification |
| 18 | Execution safety | No live orders while evidence and validation are insufficient | LIVE EXECUTION LOCKED; must remain locked |

## 3. New strategy and research modules to add to the existing pipeline

| Module | Implementation requirement | Evidence gate | Status |
|---|---|---|---|
| Early Wallet & Launch Cohort | Record wallets active around token launch/first observed liquidity; preserve first-seen time and source signatures; compare cohort behavior without assuming profitability | Real transaction timestamps and reproducible wallet/token linkage | NEW — BELUM TERVERIFIKASI |
| Wallet Independence for Smart Money | Score distinct economic actors, funding overlap and correlated timing; penalize apparent wallet diversity when evidence suggests common control | Evidence-backed links; avoid declaring common ownership from timing alone | PARTIAL foundations; production calibration BELUM TERVERIFIKASI |
| Realized PnL from Confirmed Swaps | Reconstruct token/quote asset amounts, decimals, fees and execution price; use FIFO/defined accounting; do not label SOL price as USD without a valid conversion source | Confirmed transaction + explicit swap semantics + consistent quote valuation | PARTIAL; full real-wallet PnL BELUM TERVERIFIKASI |
| Narrative Attention / On-chain Lead–Lag | Store sourced attention observations and timestamps; compare attention acceleration with subsequent on-chain activity using lag windows | Identified sources, freshness, coverage and out-of-sample tests; correlation is not causation | NEW — BELUM TERVERIFIKASI |
| Capital Rotation Monitor | Track changes in activity/volume across token groups or narratives and flag candidate rotation | Comparable, timestamped observations and clear coverage limits | NEW — BELUM TERVERIFIKASI |
| Liquidity-aware Position & Exit Simulation | Simulate entries/exits using route quotes, estimated price impact, fees, slippage and liquidity changes | Quote provider tested against real routes; conservative assumptions and auditable outputs | PARTIAL; end-to-end proof BELUM TERVERIFIKASI |
| Wealth Casebook (global research) | Maintain a sourced casebook of public, documented wealth-building/trading cases, including dates, market regime, asset, method and evidence quality | Traceable public sources; separate verified facts from anecdotes; never use success stories as proof of strategy edge | NEW — research scope, not an executable signal |
| Winning and Losing Token Dataset | Build a point-in-time dataset of winners and losers, including delisted/failed tokens where data can be recovered; preserve features as they were observable at decision time | No look-ahead leakage; source provenance, missingness, label definitions and reproducible splits | NEW — BELUM TERVERIFIKASI |
| Independent Strategy Evaluation | Test Early Flow, wallet cohort, Smart Money, narrative lead–lag, rotation and combined Edge separately | Out-of-sample and walk-forward results, costs, slippage, drawdown and negative cases | NEW — BELUM TERVERIFIKASI |

## 4. Candlestick and mobile cockpit requirements

The candlestick panel must use a real OHLCV source or candles aggregated from actual timestamped price/trade observations. A single spot quote, random values, test fixtures or interpolated prices must never be represented as observed candles.

Required cockpit panels:
- Token Radar with source, observed-at time, freshness and actual market metrics.
- Real OHLCV candlestick chart with timeframe selection and volume bars.
- Early Flow and 5-minute forensic timeline.
- Animated wallet-flow graph whose nodes/edges/BUY/SELL pulses derive from actual observed evidence; if evidence is absent, display an explicit pending/empty state.
- Smart Money and Early Wallet/Launch Cohort panels with evidence quality and timestamps.
- Dev DNA, funding links, cluster/manipulation and confidence/limitations.
- Liquidity, route quote, estimated slippage, price impact and exitability.
- Asymmetric Edge with component contributions and explicit missing-evidence reasons.
- Risk Veto, regime status, paper positions, exit/protection, trade journal and validation progress.
- Capital Mission progress only from recorded balances/journal; target amounts are objectives, not profit promises.

Every panel must distinguish at minimum: CONNECTED/COLLECTED, STALE, UNAVAILABLE, NOT_CONFIGURED, NOT_EVALUATED and INSUFFICIENT_EVIDENCE as appropriate. UI animation may visualize actual changing data, but must not invent wallet relationships, transactions, candles, prices or PnL. A rendered graph is not proof that its underlying inference is correct.

## 5. Dataset, casebook and evaluation controls

1. Capture point-in-time features before outcomes are known; store observation time, token mint, source, signature/URL where applicable, and parser/version.
2. Define success/failure labels before training or scoring. Include failed, rugged, inactive and unavailable tokens where the data is recoverable; record censoring and missing-data limitations.
3. Split by time, not random rows alone, to reduce leakage. Keep a true out-of-sample period and use walk-forward evaluation.
4. Compare each signal alone, independent combinations, and a baseline. Report trade count, win rate, expectancy after costs, profit factor, maximum drawdown, slippage, coverage and uncertainty.
5. Include false positives, failed tokens and no-trade periods. Do not select only famous winners or survivorship-biased examples.
6. Wealth Casebook sources inform research hypotheses only; anecdotal success is not evidence that the system has an edge.
7. No strategy is promoted based on fixtures or in-sample performance alone.

## 6. Ordered engineering execution

1. **Deployment/data truth:** verify the iPhone-serving public snapshot endpoint is from the current branch/version; verify runtime RPC status and slot, DEX status, timestamps and stale-data behavior.
2. **Real transaction path:** complete WebSocket event → transaction fetch → successful-transaction filter → parser → evidence-backed BUY/SELL → rolling 5-minute aggregation.
3. **Swap accounting:** confirm explicit DEX semantics and quote-asset valuation; verify realized PnL on inspectable transactions.
4. **Wallet cohorts and graph:** preserve launch/first-seen timing; create only evidence-backed nodes/edges; harden independence and correlated-wallet penalties.
5. **Liquidity-aware simulation:** connect a real quote provider and test entry/exit costs, price impact and adverse liquidity changes.
6. **Candlestick:** identify and integrate a legitimate OHLCV source or aggregate real timestamped trades; expose provenance and freshness.
7. **Dashboard connection and visuals:** wire each panel to snapshot/data endpoints; build the actual candlestick and evidence-driven animated graph; verify mobile UI and cache/version behavior.
8. **Narrative and capital rotation:** add sourced public observations, attention velocity and lead–lag tests only after source/freshness checks.
9. **Casebook and dataset:** build point-in-time winner/loser records with provenance and leakage controls.
10. **Paper-trade end-to-end:** journal every decision, entry/exit, fees, slippage, PnL and evidence; collect at least 100 valid paper trades.
11. **Validation:** out-of-sample + walk-forward + negative cases + drawdown/EV review. Report failures as well as successes.
12. **Release gate:** audit source, tests, runtime and safety. Live execution remains locked; no merge to main without explicit Founder approval.

## 7. Status and evidence rules

- VERIFIED means the specified test/runtime behavior has inspectable evidence; it does not imply profitability.
- PARTIAL means some code or tests exist, but the full runtime/evidence chain is incomplete.
- NEW / NOT BUILT means it is a roadmap item, not a delivered capability.
- BELUM TERVERIFIKASI means there is not enough inspectable evidence to claim it works as intended.
- Unit tests with fixtures verify code behavior under test conditions; they do not prove real market behavior.
- Prior real RPC/WebSocket smoke results prove only the observed request/event, not continuous production operation or strategy profitability.
- Profitability, competitive edge and live readiness remain BELUM TERVERIFIKASI.
- DRY RUN and PAPER TRADING stay ON; LIVE EXECUTION stays LOCKED.
- No merge to main without explicit Founder approval.


## Founder roadmap update — 2026-10-13

The detailed additive technical/strategy checkpoint is maintained in [`docs/ROADMAP_TECHNICAL_STRATEGY_ADDENDUM_2026-10-13.md`](ROADMAP_TECHNICAL_STRATEGY_ADDENDUM_2026-10-13.md). It formalizes the status matrix and acceptance gates for Early Wallet/Launch Cohort, independent Smart Money/Wallet Graph, confirmed-swap realized PnL, Narrative Attention/On-chain Lead–Lag, Capital Rotation, liquidity-aware position/exit simulation, the global Wealth Casebook, point-in-time winner/loser dataset, paper trading, out-of-sample/walk-forward validation, and iPhone dashboard verification.

**Current strategic order:** (1) verify deployment snapshot/version and production RPC on the iPhone-serving service; (2) finish WebSocket-to-evidence-backed BUY/SELL and rolling 5-minute flow; (3) verify swap semantics and quote-asset PnL; (4) connect cohorts and wallet independence; (5) real quote/exit simulation; (6) OHLCV and dashboard data wiring; (7) sourced narrative/rotation; (8) point-in-time casebook/dataset; (9) at least 100 valid paper trades and OOS/walk-forward validation; (10) release/safety gate.

This checkpoint is documentation and prioritization only. It does not claim new modules are implemented or runtime-verified. Profitability remains **BELUM TERVERIFIKASI**; DRY RUN/PAPER TRADING stay ON; LIVE EXECUTION stays LOCKED; no merge to `main` without explicit Founder approval.


## Live five-minute forensic endpoint — 2026-10-14

- Added `GET /forensics?token=<mint>` to the existing production snapshot service.
- Uses the configured `SOLANA_RPC_URL` (Helius in the Founder environment) and a DexScreener-identified Solana pool to fetch confirmed signatures and transaction metadata.
- Parses successful transactions, applies a trailing 300-second block-time window, and surfaces token/SOL balance-flow candidates with wallet, signature, slot, and time evidence.
- The cockpit polls this endpoint for the selected token and displays candidate counts and evidence links.
- Candidate flow is **not** labelled as a confirmed DEX swap: program/instruction semantics, quote accounting, and realized PnL remain separate acceptance gates.
- RPC sampling is bounded; the response reports `sample_exhaustive` / `data_complete` honestly when a signature limit is reached or transactions cannot be parsed.
- Regression tests cover recent candidate aggregation and the no-RPC-configured state. GitHub Actions passed the endpoint implementation/test commit; the latest UI syntax and final deployment must still be verified independently.


## Founder-visible dashboard update — 2026-10-15

- Moved the live 5-minute on-chain forensic card from the Wallets workspace onto the first Radar screen so the delivered endpoint is visible without navigating away from the dashboard.
- Made the forensic card visually distinct and changed the headline to **5M LIVE ON-CHAIN FORENSICS**.
- The roadmap matrix now reflects the forensic endpoint's runtime response state (live RPC sample, incomplete sample, or unavailable); it does not mark the module complete based on endpoint reachability alone.
- Bumped HTML/JS asset query versions and service-worker cache from UI38/v38 to UI39/v39 to reduce stale iPhone/PWA assets.
- Railway logs from the deployed service show HTTP 200 for `/snapshot` and `/forensics` requests. This confirms route reachability only; it does not by itself prove valid live transaction evidence or that every installed iPhone PWA has refreshed.
- Next acceptance check: open the public dashboard with a cache-busting query or refresh the installed PWA, confirm the 5M panel is on the first Radar screen, and inspect its selected-token evidence state. DEX instruction semantics, developer attribution, realized PnL, and live execution remain unverified/locked.


## Developer DNA evidence adapter — 2026-10-15

- Added `GET /dev-dna?token=<mint>` using the configured Solana RPC endpoint. It scans a bounded confirmed-signature sample for parsed SPL `initializeMint` / `initializeMint2` instructions.
- When observed, the endpoint reports the initialization transaction, first signer candidate, and mint authority as distinct evidence fields; it samples that signer's bounded history for other observed mint initializations.
- It explicitly returns `risk_score: null` and `classification: NOT_SCORED`. Signer identity, developer control, rug history, profitability, and manipulation are not inferred from initialization evidence alone.
- Added a live Dev DNA panel in the Token Terminal with links to the candidate signer and mint authority. It loads when the selected token changes and does not claim a reputation score.
- Acceptance limits: bounded signature samples can miss older initialization/history; no confirmed dev attribution, rug labels, or profitable-launch ground truth is integrated yet. Phase 4 remains **PARTIAL**.


---

## Founder checkpoint — 2026-10-22 (bounded RPC retry hardening)

### Change committed to the working branch

- Updated `src/data/solana_rpc.py` to retry transient HTTP 429 and selected 5xx responses with bounded exponential backoff, honoring numeric `Retry-After` values up to a 2-second cap.
- HTTP 403 and other non-retryable errors still fail closed; retry count is bounded and configurable.
- Added regression tests for 429-then-success and no retry on 403.
- Source commit: `addc92531c1194d8e39ad6f2cea788be864dfa22`.
- Test commit: `c9a398c89c8e9896aa11dcf38fd2d8e7da4b2356`.
- Test status: **TESTS ADDED — EXECUTION BELUM TERVERIFIKASI**. The available session could not reach GitHub to clone the branch, and no passing CI result was observed during this checkpoint.
- Deployment status: production still points to deployment `c7c94624-ba10-443e-8cad-3437745c2083`, commit `988fc2ce5313019ac2b2e4ff870e989fb233d298`; this code change is **NOT DEPLOYED**.
- Trading status remains **NOT READY**. This retry change reduces avoidable transient failures but does not resolve provider capacity, high request volume, missing confirmed DEX semantics, missing quote-backed exitability, or insufficient out-of-sample paper evidence.

### Required follow-up

1. Execute `pytest -q` on the branch and fix any regression before deployment.
2. Reconnect/deploy the intended working branch only after tests pass; verify the terminal deployment status.
3. Verify production RPC health, slot, freshness and real on-chain endpoints on the deployed build.
4. Continue the full roadmap. Do not enable live execution.


### Verification update — 2026-10-22

- An isolated local harness ran the three focused `tests/test_solana_rpc.py` cases against the fetched branch implementation and matching test logic: **3 passed**. This is focused verification only; the full repository test suite and CI are still **BELUM TERVERIFIKASI**.
- Railway service configuration was read without exposing secret values. The service is configured to follow `agent/memecoin-hunter-foundation` and has a `SOLANA_RPC_URL` variable name, but its value and runtime connectivity were not exposed or verified.
- A deployment trigger was attempted for the intended branch; Railway returned **“Deploys have been paused temporarily.”** No new deployment was created. Production remains on the previously observed deployment and must not be described as updated.
- A live HTTP read of the public `/snapshot` endpoint could not be completed from this session. Production end-to-end dashboard/data verification remains **BELUM TERVERIFIKASI**.
