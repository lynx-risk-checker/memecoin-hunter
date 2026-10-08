import json

import pytest

from src.data.solana_stream import (
    SolanaLogEvent,
    SolanaLogStream,
    SolanaWebSocketError,
    parse_logs_notification,
    websocket_endpoint,
)


def test_websocket_endpoint_converts_http_rpc():
    assert websocket_endpoint("https://example.com/?api-key=x") == "wss://example.com/?api-key=x"
    assert websocket_endpoint("http://localhost:8899") == "ws://localhost:8899"


def test_parse_logs_notification():
    message = json.dumps({
        "jsonrpc": "2.0",
        "method": "logsNotification",
        "params": {
            "subscription": 7,
            "result": {
                "context": {"slot": 123},
                "value": {
                    "signature": "SIG",
                    "err": None,
                    "logs": ["Program log: hello"],
                },
            },
        },
    })
    event = parse_logs_notification(message)
    assert event == SolanaLogEvent(7, "SIG", 123, None, ("Program log: hello",))


def test_parse_logs_notification_rejects_bad_shape():
    with pytest.raises(SolanaWebSocketError):
        parse_logs_notification("{}")


def test_stream_builds_mentions_subscription():
    sent = []

    class FakeSocket:
        async def send(self, payload):
            sent.append(json.loads(payload))

        async def recv(self):
            if len(sent) == 1:
                return json.dumps({"result": 9, "id": 1})
            return json.dumps({
                "params": {
                    "subscription": 9,
                    "result": {
                        "context": {"slot": 5},
                        "value": {"signature": "SIG", "err": None, "logs": []},
                    },
                }
            })

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    def factory(*args, **kwargs):
        class Context:
            async def __aenter__(self):
                return FakeSocket()

            async def __aexit__(self, *args):
                return False
        return Context()

    import asyncio

    async def run():
        stream = SolanaLogStream("https://example.com", websocket_factory=factory)
        iterator = stream.events(mentions="MINT")
        event = await anext(iterator)
        await iterator.aclose()
        return event

    event = asyncio.run(run())
    assert event.signature == "SIG"
    assert sent[0]["method"] == "logsSubscribe"
    assert sent[0]["params"][0] == {"mentions": ["MINT"]}
    assert sent[0]["params"][1] == {"commitment": "confirmed"}
