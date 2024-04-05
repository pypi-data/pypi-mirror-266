from dataclasses import dataclass

from helldivers2_api.faction import Faction


@dataclass
class GlobalEvent:
    assignment_id: int
    effect_ids: list[int]
    event_id: int
    flag: int  # ToDo: Unclear what this value means
    id32: int  # ToDo: Unclear what this value means
    message: str
    message_id: int
    affected_planets: list
    portrait_id: int  # ToDo: Unclear what this value means
    race: Faction
    title: str
    title_id: int
