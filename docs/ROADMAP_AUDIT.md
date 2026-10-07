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
| 16 | Exit / emergency kill switch | PARTIAL — protection/exit evaluation exists/unit-tested; runtime position-monitoring integration remains |
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
