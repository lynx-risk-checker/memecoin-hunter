from src.data.instruction_parser import (
    extract_instruction_evidence,
    extract_log_evidence,
)


def test_extracts_program_id_and_parsed_type() -> None:
    tx = {
        "transaction": {
            "message": {
                "accountKeys": ["PROGRAM_A"],
                "instructions": [
                    {
                        "programId": "PROGRAM_A",
                        "parsed": {"type": "transfer"},
                        "accounts": [0, 2],
                    }
                ],
            }
        }
    }
    result = extract_instruction_evidence(tx)
    assert len(result) == 1
    assert result[0].program_id == "PROGRAM_A"
    assert result[0].parsed_type == "transfer"
    assert result[0].raw_accounts == (0, 2)
    assert result[0].source == "outer"
    assert result[0].instruction_index == 0


def test_resolves_program_id_index() -> None:
    tx = {
        "transaction": {
            "message": {
                "accountKeys": ["PROGRAM_A"],
                "instructions": [{"programIdIndex": 0, "data": "abc"}],
            }
        }
    }
    result = extract_instruction_evidence(tx)
    assert result[0].program_id == "PROGRAM_A"
    assert result[0].data == "abc"


def test_extracts_inner_instructions_without_interpreting_them() -> None:
    tx = {
        "transaction": {
            "message": {
                "accountKeys": ["PROGRAM_A"],
                "instructions": [],
            }
        },
        "meta": {
            "innerInstructions": [
                {
                    "index": 0,
                    "instructions": [
                        {"programId": "PROGRAM_A", "parsed": {"type": "transfer"}}
                    ],
                }
            ]
        },
    }
    result = extract_instruction_evidence(tx)
    assert len(result) == 1
    assert result[0].source == "inner"
    assert result[0].parent_index == 0
    assert result[0].parsed_type == "transfer"


def test_extracts_log_messages_as_observable_evidence() -> None:
    tx = {"meta": {"logMessages": ["Program log: swap-like event", None]}}
    result = extract_log_evidence(tx)
    assert result[0].message == "Program log: swap-like event"
    assert len(result) == 1


def test_missing_instruction_payload_is_not_invented() -> None:
    tx = {"transaction": {"message": {"accountKeys": ["PROGRAM_A"]}}}
    assert extract_instruction_evidence(tx) == ()
