# Roadmap Audit — MEMECOIN HUNTER

Audit basis: repository branch agent/memecoin-hunter-foundation, current source tree and tests. This document distinguishes code presence, unit-test coverage, and real-runtime evidence.

## Phase status

| Phase | Area | Status |
|---|---|---|
| 0 | Foundation / safety | VERIFIED (unit) |
| 1 | Real Solana data | VERIFIED for prior RPC smoke; continual evidence BELUM TERVERIFIKASI |
| 2 | Token Radar | VERIFIED (unit + prior real smoke) |
| 3 | 5-minute forensics | PARTIAL — DEX Screener h24 fields are proxies, not native 5m on-chain flow |
| 4 | Dev DNA | PARTIAL — runtime developer attribution/history BELUM TERVERIFIKASI |
| 5 | Smart Money / wallet intelligence | PARTIAL — real wallet intelligence BELUM TERVERIFIKASI; PnL/win-rate/entry-quality model missing |
| 6 | Wallet graph / economic clusters | PARTIAL — real multi-wallet cluster evidence BELUM TERVERIFIKASI; correlation/double-counting needs hardening |
| 7 | Manipulation / insider detection | PARTIAL — real Solana end-to-end veto BELUM TERVERIFIKASI |
| 8 | Liquidity / exitability | PARTIAL — basic liquidity-ratio heuristic only; route-aware exitability/dynamic slippage missing |
| 9 | Narrative / social intelligence | PARTIAL — scoring exists; no live social/public-feed ingestion |
| 10 | Asymmetric Edge | PARTIAL — components exist, but no production end-to-end orchestrator |
| 11 | Risk veto / decision | PARTIAL — veto unit-tested; state machine/kill-switch integration missing |
| 12 | Paper trading / journal | PARTIAL — minimal PnL/win-rate only; journal, slippage, latency, drawdown, PF, expectancy, rug-loss metrics missing |
| 13 | Capital Mission | VERIFIED for target definitions; mission runtime/state persistence BELUM TERVERIFIKASI |
| 14 | Mobile PWA cockpit | NOT BUILT |
| 15 | Execution engine | SAFETY LOCK VERIFIED; live execution intentionally not built |
| 16 | Exit / emergency kill switch | NOT BUILT |
| 17 | Adaptive research | NOT BUILT |
| 18 | Full validation | NOT BUILT |
| 19 | Small live capital | NOT READY |
| 20 | Mission mode | NOT BUILT |

## Findings that must not be skipped

1. Real-runtime integration is the immediate gate. Unit tests do not prove the Solana funding/cluster/manipulation path on real chain data.
2. 5-minute forensics is not yet native 5-minute on-chain flow. DEX Screener h24 volume/transactions are cumulative 24-hour fields.
3. Smart-money intelligence is incomplete: historical PnL, win rate, holding time, early-entry quality and reliability scoring are missing.
4. Liquidity/exitability is too simple for live trading: no route/quote/exit simulation.
5. Paper trading is too thin for validation: required journal and robust performance metrics are missing.
6. There are two decision paths: src/decision.py and src/strategy/edge.py. They are not unified and this is a consistency risk.
7. README mission text was stale relative to the canonical six-mission definition and is corrected by this audit update.
8. Live execution remains locked.

## Immediate next gate

Run scripts/smoke_wallet_intelligence_real_data.py. It starts from a real Solana token, reads real transaction signatures, parses real transactions, discovers candidate wallet owners, infers explicit funding flows, and runs wallet-link/synchronization/counterparty/shared-funding/cluster/manipulation.

Passing this script proves runtime plumbing only; it does not prove profitable strategy performance or common ownership.
