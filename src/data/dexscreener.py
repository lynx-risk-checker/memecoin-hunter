from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.forensics.models import TokenSnapshot
from src.radar.models import TokenCandidate


class DexScreenerError(RuntimeError):
    """Raised when the DEX Screener API cannot be read safely."""


@dataclass(frozen=True)
class DexScreenerClient:
    base_url: str = "https://api.dexscreener.com"
    timeout_seconds: float = 10.0
    user_agent: str = "memecoin-hunter/0.1 (+read-only)"

    def _get(self, path: str, params: dict[str, str] | None = None) -> Any:
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            self.base_url.rstrip("/") + path + query,
            headers={
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise DexScreenerError(
                f"DEX Screener HTTP {exc.code} for {path}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise DexScreenerError(f"DEX Screener request failed: {path}") from exc

        if not isinstance(body, (dict, list)):
            raise DexScreenerError("DEX Screener returned an invalid JSON shape.")
        return body

    def latest_profiles(self) -> list[dict[str, Any]]:
        body = self._get("/token-profiles/latest/v1")
        if not isinstance(body, list):
            raise DexScreenerError("Latest token profiles response must be a list.")
        return [item for item in body if isinstance(item, dict)]

    def token_pairs(self, token_addresses: list[str]) -> list[dict[str, Any]]:
        if not token_addresses:
            return []
        if len(token_addresses) > 30:
            raise ValueError("DEX Screener accepts at most 30 token addresses per request.")
        body = self._get("/tokens/v1/solana/" + ",".join(token_addresses))
        if not isinstance(body, list):
            raise DexScreenerError("Token pairs response must be a list.")
        return [item for item in body if isinstance(item, dict)]

    @staticmethod
    def _best_solana_pair(
        pairs: list[dict[str, Any]], token_address: str
    ) -> dict[str, Any] | None:
        matches = []
        for pair in pairs:
            if pair.get("chainId") != "solana":
                continue
            base = pair.get("baseToken")
            if not isinstance(base, dict) or base.get("address") != token_address:
                continue
            liquidity = pair.get("liquidity")
            liquidity_usd = (
                float(liquidity["usd"])
                if isinstance(liquidity, dict) and isinstance(liquidity.get("usd"), (int, float))
                else -1.0
            )
            matches.append((liquidity_usd, pair))
        if not matches:
            return None
        return max(matches, key=lambda item: item[0])[1]

    def discover(self, max_tokens: int = 30) -> list[TokenCandidate]:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive.")

        profiles = self.latest_profiles()
        addresses: list[str] = []
        for profile in profiles:
            if profile.get("chainId") != "solana":
                continue
            address = profile.get("tokenAddress")
            if isinstance(address, str) and address.strip() and address not in addresses:
                addresses.append(address)
            if len(addresses) >= max_tokens:
                break

        pairs = self.token_pairs(addresses)
        now = datetime.now(timezone.utc)
        candidates: list[TokenCandidate] = []
        seen: set[str] = set()

        for address in addresses:
            pair = self._best_solana_pair(pairs, address)
            if pair is None or address in seen:
                continue
            base = pair.get("baseToken")
            if not isinstance(base, dict):
                continue

            created_at = pair.get("pairCreatedAt")
            age_seconds = None
            if isinstance(created_at, (int, float)):
                age_seconds = max(0.0, now.timestamp() - (float(created_at) / 1000.0))

            liquidity = pair.get("liquidity")
            liquidity_usd = None
            if isinstance(liquidity, dict) and isinstance(liquidity.get("usd"), (int, float)):
                liquidity_usd = float(liquidity["usd"])

            market_cap = pair.get("marketCap")
            if not isinstance(market_cap, (int, float)):
                market_cap = pair.get("fdv")
            market_cap_usd = float(market_cap) if isinstance(market_cap, (int, float)) else None

            candidates.append(
                TokenCandidate(
                    address=address,
                    observed_at=now,
                    source="dexscreener",
                    symbol=base.get("symbol") if isinstance(base.get("symbol"), str) else None,
                    name=base.get("name") if isinstance(base.get("name"), str) else None,
                    liquidity_usd=liquidity_usd,
                    market_cap_usd=market_cap_usd,
                    age_seconds=age_seconds,
                )
            )
            seen.add(address)

        return candidates

    def snapshot(self, token_address: str) -> TokenSnapshot:
        if not token_address.strip():
            raise ValueError("Token address is required.")

        pairs = self.token_pairs([token_address])
        pair = self._best_solana_pair(pairs, token_address)
        if pair is None:
            raise DexScreenerError("No Solana pair found for token.")

        base = pair.get("baseToken")
        price = pair.get("priceUsd")
        liquidity = pair.get("liquidity")
        volume = pair.get("volume")
        txns = pair.get("txns")
        market_cap = pair.get("marketCap")
        if not isinstance(market_cap, (int, float)):
            market_cap = pair.get("fdv")

        liquidity_usd = liquidity.get("usd") if isinstance(liquidity, dict) else None
        volume_usd = volume.get("h24") if isinstance(volume, dict) else None
        buys = txns.get("h24", {}).get("buys") if isinstance(txns, dict) else None
        sells = txns.get("h24", {}).get("sells") if isinstance(txns, dict) else None

        required = {
            "priceUsd": price,
            "liquidity.usd": liquidity_usd,
            "volume.h24": volume_usd,
            "txns.h24.buys": buys,
            "txns.h24.sells": sells,
        }
        missing = [name for name, value in required.items() if not isinstance(value, (int, float))]
        if missing:
            raise DexScreenerError(
                "Snapshot is incomplete; missing numeric fields: " + ", ".join(missing)
            )

        if not isinstance(base, dict) or not isinstance(base.get("address"), str):
            raise DexScreenerError("Snapshot base token data is invalid.")

        return TokenSnapshot(
            token_address=token_address,
            observed_at=datetime.now(timezone.utc),
            price_usd=float(price),
            liquidity_usd=float(liquidity_usd),
            volume_usd=float(volume_usd),
            buy_count=int(buys),
            sell_count=int(sells),
            unique_buyers=0,
            unique_sellers=0,
            holder_count=0,
            market_cap_usd=float(market_cap) if isinstance(market_cap, (int, float)) else None,
        )
