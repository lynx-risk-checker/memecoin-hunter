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
    source: str = "outer"
    instruction_index: int | None = None
    parent_index: int | None = None


@dataclass(frozen=True)
class LogEvidence:
    message: str


def _program_ids(message: dict[str, Any]) -> list[str]:
    keys = message.get("accountKeys", [])
    if not isinstance(keys, list):
        return []
    result: list[str] = []
    for item in keys:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and isinstance(item.get("pubkey"), str):
            result.append(item["pubkey"])
    return result


def _parse_instruction(
    instruction: Any,
    program_ids: list[str],
    *,
    source: str,
    instruction_index: int | None,
    parent_index: int | None,
) -> InstructionEvidence | None:
    if not isinstance(instruction, dict):
        return None

    program_id = instruction.get("programId")
    program_index = instruction.get("programIdIndex")
    parsed = instruction.get("parsed")
    parsed_type = (
        parsed.get("type")
        if isinstance(parsed, dict) and isinstance(parsed.get("type"), str)
        else None
    )
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
        return None

    return InstructionEvidence(
        program_id=resolved_program_id,
        program_index=program_index if isinstance(program_index, int) else None,
        parsed_type=parsed_type,
        raw_accounts=raw_accounts,
        data=data,
        source=source,
        instruction_index=instruction_index,
        parent_index=parent_index,
    )


def extract_instruction_evidence(
    transaction: dict[str, Any],
) -> tuple[InstructionEvidence, ...]:
    """Extract observable outer and inner instruction metadata.

    This function deliberately does not interpret arbitrary instruction data as
    a swap. It only exposes what the RPC transaction payload makes observable.
    """
    tx = transaction.get("transaction")
    if not isinstance(tx, dict):
        raise ValueError("Transaction must contain transaction.")
    message = tx.get("message")
    if not isinstance(message, dict):
        raise ValueError("Transaction must contain message.")

    program_ids = _program_ids(message)
    result: list[InstructionEvidence] = []

    instructions = message.get("instructions", [])
    if isinstance(instructions, list):
        for index, instruction in enumerate(instructions):
            evidence = _parse_instruction(
                instruction,
                program_ids,
                source="outer",
                instruction_index=index,
                parent_index=None,
            )
            if evidence is not None:
                result.append(evidence)

    meta = transaction.get("meta")
    inner = meta.get("innerInstructions") if isinstance(meta, dict) else None
    if isinstance(inner, list):
        for group in inner:
            if not isinstance(group, dict):
                continue
            parent_index = group.get("index")
            parent_index = parent_index if isinstance(parent_index, int) else None
            instructions = group.get("instructions", [])
            if not isinstance(instructions, list):
                continue
            for index, instruction in enumerate(instructions):
                evidence = _parse_instruction(
                    instruction,
                    program_ids,
                    source="inner",
                    instruction_index=index,
                    parent_index=parent_index,
                )
                if evidence is not None:
                    result.append(evidence)

    return tuple(result)


def extract_log_evidence(transaction: dict[str, Any]) -> tuple[LogEvidence, ...]:
    meta = transaction.get("meta")
    if not isinstance(meta, dict):
        return ()
    logs = meta.get("logMessages")
    if not isinstance(logs, list):
        return ()
    return tuple(
        LogEvidence(message)
        for message in logs
        if isinstance(message, str)
    )
