# MEMECOIN HUNTER — Roadmap Addendum (Technical + Strategy)
**Founder checkpoint:** 2026-10-13  
**Scope:** Additive extension to the existing architecture and `docs/ROADMAP_AUDIT.md`. This document does not replace existing modules, reset the project, authorize deletion, or change execution safety.

## 1. Executive status

| Module / capability | Status | Evidence required to advance |
|---|---|---|
| Solana RPC + DexScreener | Foundation previously verified; production configuration/runtime continuity remains unverified | Public snapshot from current deployment; RPC `CONNECTED`, numeric slot, source timestamps/freshness, DEX health |
| Volume 5M/1H and TXNS/min | Prior implementation reported verified | Confirm current production output is real, timestamped, and fresh; distinguish missing data from zero |
| Solana WebSocket | Real event receipt previously verified | Repeatable runtime evidence, reconnect/backoff behavior, dropped-event accounting |
| WebSocket → successful transaction → BUY/SELL | PARTIAL | End-to-end signature trace through fetch, success filter, parser, token/quote balance evidence, direction and rolling flow |
| Early Wallet & Launch Cohort | NEW — BELUM TERVERIFIKASI | First-seen/launch-relative wallet observations with reproducible transaction linkage and time boundaries |
| Smart Money + independent Wallet Graph | PARTIAL foundations | Confirmed swap accounting, economic-independence evidence, cluster double-counting controls and calibration |
| Realized PnL from confirmed swaps | PARTIAL — full real-wallet PnL BELUM TERVERIFIKASI | Explicit DEX swap semantics, token + quote deltas, decimals, fees, execution price, defined accounting and auditable examples |
| Narrative Attention / on-chain Lead–Lag | NEW — BELUM TERVERIFIKASI | Timestamped sourced attention series, coverage/freshness and out-of-sample lead–lag analysis |
| Capital Rotation Monitor | NEW — BELUM TERVERIFIKASI | Comparable activity/volume across defined token or narrative groups, timestamps and coverage limits |
| Liquidity-aware Position & Exit Simulation | PARTIAL | Real route quotes, position sizing, price impact, fees, slippage, exit routes and conservative failure handling |
| Global Wealth Casebook | NEW — research only | Traceable public sources, dates/regime/method/evidence-quality tags; anecdotes separated from verified facts |
| Winning and Losing Token Dataset | NEW — BELUM TERVERIFIKASI | Point-in-time records, defined labels, failed-token coverage, provenance and leakage-safe time splits |
| Paper trading + out-of-sample validation | PARTIAL; evidence insufficient | Persistent journal, at least 100 valid paper trades, realistic costs, OOS and walk-forward results including negative cases |
| iPhone dashboard | PARTIAL — current production version/UI connection must be verified | Current schema and deployment identity, freshness/source states, iPhone render/cache checks and data-to-panel traceability |
| Profitability / durable edge | **BELUM TERVERIFIKASI** | Positive, robust out-of-sample expectancy after costs with drawdown and uncertainty reported |
| Live execution | **LOCKED** | No unlock through this roadmap; requires all gates and explicit Founder authorization |

A status describes the evidence currently available, not the ambition of the module. Newly listed modules remain **BELUM TERVERIFIKASI** until implementation, tests, real-data output and relevant paper-trading evidence are inspectable.

## 2. Architecture: additive, not a replacement

The new strategy modules extend the current chain:

`Solana RPC / WebSocket + DexScreener → Token Radar → transaction evidence → Early Flow / 5M Forensics → swap accounting → wallet history / cohorts / graph → Smart Money + cluster/manipulation → liquidity/exit simulation → narrative/rotation → Asymmetric Edge → Risk Veto → paper execution/journal → protection/exit → validation gate → iPhone cockpit`

The chain is not considered end-to-end complete merely because each component exists. Every edge between components needs a traceable input/output contract, timestamps, source provenance, explicit missing-data behavior, and a test or runtime proof. Risk Veto and capital-defense controls can block a signal at any stage.

### Strategic roles

- **GABRIEL REY — Capital Defense + Macro Regime:** classifies AGGRESSIVE / NORMAL / DEFENSIVE / HALTED from sourced market conditions, volatility/liquidity regime, drawdown, system health, evidence freshness and risk limits. When required macro sources are unavailable, the regime must degrade conservatively rather than infer safety.
- **ORANGIE — Attention Velocity + Early Discovery:** detects discovery and acceleration from timestamped token activity and sourced public attention. A narrative mention is not a BUY signal by itself.
- **BEVAN PRAMUDITO — Smart Money + Wallet Graph + Narrative Rotation:** combines confirmed swap outcomes, wallet histories, economic links, independence scoring and narrative/rotation observations. Apparent wallet diversity must be discounted when evidence shows correlated behavior.
- These are research/architecture roles, not proof that a strategy works. Capital defense and Risk Veto always override discovery, narrative, wallet, edge and mission objectives.

## 3. Technical work packages and acceptance gates

### P0 — Production truth: snapshot, deployment and iPhone
1. Identify the exact public endpoint and deployed version that serves the iPhone dashboard; compare it to the current branch schema.
2. Verify the deployed process has `SOLANA_RPC_URL` configured without revealing the value. A local/Codespaces environment does not prove the hosting environment is configured.
3. Verify the snapshot reports `sources.solana_rpc.status = CONNECTED` and a real numeric slot, plus DEX status, `observed_at`, freshness and explicit error/missing states.
4. Confirm the iPhone UI renders the same current snapshot and versioned assets, including cache-busting/reload behavior.
5. **Pass gate:** endpoint, schema, source health, slot, timestamps and visible UI are mutually consistent. Until then, production end-to-end status remains BELUM TERVERIFIKASI.

### P1 — WebSocket to evidence-backed BUY/SELL and rolling 5-minute flow
Implement and trace: event/signature receipt → transaction fetch → successful-transaction filter → parser → token and quote-asset balance changes → BUY/SELL/UNKNOWN classification → deduplicated rolling 5-minute aggregation. Include slot/block time, signature, parser version, source timestamp and reason codes. Handle failed transactions, missing metadata, retries, reconnects, duplicate events and out-of-order events explicitly.
- **Pass gate:** inspectable real signatures reproduce the expected direction and flow; failed, ambiguous and incomplete transactions are not silently promoted into trades.

### P2 — Confirmed DEX swap semantics and realized PnL
Require transaction-level DEX semantics rather than program-ID presence alone. Reconstruct token/quote asset deltas, token decimals, quote decimals, fees, execution price and accounting lots. Define FIFO or another explicit consistent accounting method. Do not treat a transfer as a swap, token quantity as PnL, or SOL as USD without a valid conversion source. Preserve raw evidence and explain rejected/ambiguous candidates.
- **Pass gate:** multiple inspectable real confirmed swaps reconcile within declared tolerances and produce auditable realized PnL. Unresolved cases remain UNKNOWN.

### P3 — Early Wallet, launch cohorts, Smart Money and graph independence
Record first-seen and launch-relative activity, transaction linkage and observation coverage. Build wallet↔wallet↔token↔developer↔funding relationships only from explicit evidence. Distinguish direct funding, shared intermediary, common timing and mere co-ownership hypotheses. Score economic independence; penalize correlated signals and prevent one coordinated group from counting as many independent confirmations.
- **Pass gate:** graph edges have provenance and confidence/limitations; cluster aggregation resists double counting; Smart Money outcome metrics use confirmed swaps and consistent PnL.

### P4 — Liquidity-aware position sizing and exit simulation
Connect a real quote/route provider. Simulate intended notional and both entry and exit, including fees, slippage, route availability, price impact, liquidity deterioration and conservative failure scenarios. Position size must be capped by risk policy and exitability, not only a signal score. Quotes expire; stale/unavailable quotes fail closed.
- **Pass gate:** route-level input/output, quote time, cost assumptions, expected net result and rejection reason are inspectable for entry and exit. Simulation is not represented as an actual fill.

### P5 — OHLCV and mobile cockpit data wiring
Use a real OHLCV source or aggregate candles from actual timestamped trades/prices. Never manufacture candles from a single quote, random values, fixtures or interpolation. Connect each visual panel to the same evidence-backed data contracts.
Required panels: Token Radar; OHLCV candles + volume/timeframes; Early Flow/5M timeline; evidence-driven animated wallet graph; cohorts/Smart Money; Dev DNA/funding/cluster; manipulation evidence; liquidity/quote/impact/exitability; Edge components and missing reasons; regime/Risk Veto; paper positions/journal/protection; validation progress and Capital Mission.
Every panel must distinguish applicable states such as CONNECTED/COLLECTED, STALE, UNAVAILABLE, NOT_CONFIGURED, NOT_EVALUATED and INSUFFICIENT_EVIDENCE. Animation may visualize actual events but must not invent relationships, trades, prices or PnL.
- **Pass gate:** panel values can be traced to snapshot/API evidence and timestamps on iPhone; empty states remain honest.

### P6 — Narrative attention, lead–lag and capital rotation
Ingest public attention observations with source identity, observation time, collection time, coverage and freshness. Measure attention velocity and compare it with subsequent on-chain changes across predefined lag windows. Monitor rotation only across comparable, explicitly defined token/narrative groups.
- **Pass gate:** source quality and missingness are reported; hypotheses are evaluated out of sample; correlation is not presented as causation. Do not let unverified narrative data override Risk Veto.

### P7 — Global Wealth Casebook and point-in-time winner/loser dataset
Casebook entries must include public source(s), dates, asset, regime, described method, outcome window and evidence quality. Separate independently verified facts from anecdotes and survivorship-biased stories. Dataset records must capture what was observable at decision time, source/provenance, mint, timestamps, parser/feature versions, label definition and censoring/missingness. Include failed, rugged, inactive and unavailable tokens wherever recoverable.
- **Pass gate:** reproducible data dictionary, predeclared labels, leakage checks and time-based splits exist. Casebook stories create hypotheses only; they do not prove profitability.

### P8 — Paper trading, journal and validation
Persist every decision, signal evidence, quote, simulated entry/exit, fees, slippage, latency assumptions, PnL, veto/rejection and parser/strategy version. Do not count duplicate, incomplete or invalid simulations toward the minimum 100 valid paper trades. Evaluate each strategy alone, independent combinations and a baseline. Run out-of-sample and walk-forward tests, include no-trade periods and losing cases, and report trade count, expectancy after costs, win rate, profit factor, max drawdown, slippage, coverage and uncertainty.
- **Pass gate:** at least 100 valid paper trades plus documented OOS/walk-forward results. Positive in-sample results alone do not pass. Even a pass does not automatically authorize live execution.

### P9 — Release and safety gate
Audit source, tests, real runtime evidence, data quality, deployment identity, risk veto, persistent kill switch, paper journal and validation report. Report unresolved blockers. DRY RUN and PAPER TRADING remain ON; LIVE EXECUTION remains LOCKED. No merge to `main` without explicit Founder approval.

## 4. Evidence protocol and non-negotiable controls

For every module, report separate states:
- **IMPLEMENTED:** code exists.
- **TESTED:** relevant automated tests passed; specify whether fixture/unit/integration.
- **RUNTIME VERIFIED:** observed in the intended running environment.
- **EVIDENCE VERIFIED:** underlying real data and inference are inspectable and reproducible.
- **PARTIAL / BLOCKED / BELUM TERVERIFIKASI / NOT IMPLEMENTED:** use whenever applicable; do not collapse these into “done.”

Controls:
1. Evidence → trace the data path → identify root cause → minimal patch → targeted tests → broader tests → runtime verification. No blind patching.
2. Missing, stale, contradictory or incomplete critical evidence fails closed; it must not be replaced with fake values.
3. Wallet timing, a shared token, a transfer, or a program ID alone does not prove common ownership, coordination or a DEX swap.
4. Unit tests and fixtures prove code behavior under test conditions, not real-market behavior.
5. No secrets in code, logs, frontend, documentation or commits.
6. Do not disable risk vetoes to make signals or results look better.
7. Do not claim profitability, robust edge or live readiness without sufficient cost-adjusted out-of-sample evidence.

## 5. Ordered execution queue

1. **P0:** Verify deployment snapshot/version, production RPC configuration, source health/freshness and iPhone rendering.
2. **P1:** Finish WebSocket → successful transaction → evidence-backed BUY/SELL → rolling 5-minute flow.
3. **P2:** Finish confirmed DEX swap semantics and quote-asset realized PnL.
4. **P3:** Connect launch cohorts and wallet independence to Smart Money/Edge, including correlated-signal penalties.
5. **P4:** Complete real quote, liquidity-aware position sizing and exit simulation.
6. **P5:** Wire dashboard panels and real OHLCV/transaction-driven wallet-flow visuals.
7. **P6:** Add verified narrative sources and capital-rotation analysis.
8. **P7:** Build the global Wealth Casebook and point-in-time winner/loser dataset.
9. **P8:** Run realistic paper trading to at least 100 valid trades and complete OOS/walk-forward evaluation.
10. **P9:** Review the full release gate; keep live execution locked absent separate explicit authorization.

## 6. Founder status at this checkpoint

- Research is complete as an initial phase only; it is not a census of every meme-coin millionaire worldwide.
- The repository roadmap and this addendum are documentation/research planning changes, not proof that new modules have been implemented.
- Running Codespaces is not required merely to read these documents; code changes still require appropriate tests.
- Pytest is not required solely for a documentation-only change, but this addendum does not assert that tests were run.
- No merge to `main` is performed by this document.
- Profitability remains **BELUM TERVERIFIKASI**.
- DRY RUN / PAPER TRADING remain ON; LIVE EXECUTION remains LOCKED.
