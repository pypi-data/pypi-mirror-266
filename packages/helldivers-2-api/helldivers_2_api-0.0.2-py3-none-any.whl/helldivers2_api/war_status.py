from dataclasses import dataclass

from helldivers2_api.campaign import Campaign
from helldivers2_api.global_event import GlobalEvent
from helldivers2_api.joint_operation import JointOperation
from helldivers2_api.planet_attack import PlanetAttack
from helldivers2_api.planet_event import PlanetEvent
from helldivers2_api.planet_status import PlanetStatus


@dataclass
class WarStatus:
    active_election_policy_effects: list
    campaigns: list[Campaign]
    community_targets: list  # ToDo: Unclear how to parse this value
    global_events: list[GlobalEvent]
    impact_multiplier: float
    joint_operations: list[JointOperation]
    planet_active_effects: list  # ToDo: Unclear how to parse this value
    planet_attacks: list[PlanetAttack]
    planet_events: list[PlanetEvent]
    planet_status: list[PlanetStatus]
    story_beat_id: int
    super_earth_war_results: list  # ToDo: Unclear how to parse this value
    time: int
    war_id: int
