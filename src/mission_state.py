from __future__ import annotations

from dataclasses import dataclass

from .mission import MISSIONS


@dataclass(frozen=True)
class MissionState:
    capital_idr: int
    mission_index: int
    status: str

    @property
    def mission(self):
        return MISSIONS[self.mission_index]

    @property
    def progress(self) -> float:
        return self.mission.progress(self.capital_idr)


def evaluate_mission(capital_idr: int) -> MissionState:
    if capital_idr < 0:
        raise ValueError("capital_idr cannot be negative")

    for index, mission in enumerate(MISSIONS):
        if capital_idr < mission.target_idr:
            return MissionState(
                capital_idr=capital_idr,
                mission_index=index,
                status=mission.status(capital_idr),
            )

    return MissionState(
        capital_idr=capital_idr,
        mission_index=len(MISSIONS) - 1,
        status="TARGET_REACHED",
    )
