from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InstructionEvidence:
    program_id: str
    program_index: int | None
    parsed_type: str | None
    raw_accounts: tuple[int, ...]
    data: str | None


def extract_instruction_evidence(transaction: dict[str, Any]) -> tuple[InstructionEvidence, ...]:
    """Extract observable instruction metadata without interpreting swap semantics."""
    tx = transaction.get("transaction")
    if not isinstance(tx, dict):
        raise ValueError("Transaction must contain transaction.")
    message = tx.get("message")
    if not isinstance(message, dict):
        raise ValueError("Transaction must contain message.")

    keys = message.get("accountKeys", [])
    if not isinstance(keys, list):
        return ()

    program_ids: list[str] = []
    for item in keys:
        if isinstance(item, str):
            program_ids.append(item)
        elif isinstance(item, dict) and isinstance(item.get("pubkey"), str):
            program_ids.append(item["pubkey"])

    instructions = message.get("instructions", [])
    if not isinstance(instructions, list):
        return ()

    result: list[InstructionEvidence] = []
    for instruction in instructions:
        if not isinstance(instruction, dict):
            continue

        program_id = instruction.get("programId")
        program_index = instruction.get("programIdIndex")
        parsed = instruction.get("parsed")
        parsed_type = parsed.get("type") if isinstance(parsed, dict) and isinstance(parsed.get("type"), str) else None

        accounts = instruction.get("accounts", [])
        raw_accounts = tuple(
            int(index) for index in accounts
            if isinstance(index, int) and index >= 0
        )

        data = instruction.get("data")
        data = data if isinstance(data, str) else None

        if isinstance(program_id, str):
            resolved_program_id = program_id
        elif isinstance(program_index, int) and 0 <= program_index < len(program_ids):
            resolved_program_id = program_ids[program_index]
        else:
            continue

        result.append(
            InstructionEvidence(
                program_id=resolved_program_id,
                program_index=program_index if isinstance(program_index, int) else None,
                parsed_type=parsed_type,
                raw_accounts=raw_accounts,
                data=data,
            )
        )

    return tuple(result)
