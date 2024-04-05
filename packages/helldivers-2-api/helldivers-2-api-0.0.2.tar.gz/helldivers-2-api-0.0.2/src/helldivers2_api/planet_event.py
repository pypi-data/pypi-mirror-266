from dataclasses import dataclass
from enum import IntEnum

from helldivers2_api.faction import Faction


class PlanetEventType(IntEnum):
    # Never seen anything but 1, but adding 0 and 2, just so the package does not break once we see it
    UNKNOWN = 0
    DEFENSE = 1
    ALSO_UNKNOWN = 2


@dataclass
class PlanetEvent:
    campaign_id: int
    event_type: PlanetEventType
    expire_time: int
    health: int
    event_id: int
    joint_operation_ids: list[int]
    max_health: int
    planet_index: int
    faction: Faction
    start_time: int


