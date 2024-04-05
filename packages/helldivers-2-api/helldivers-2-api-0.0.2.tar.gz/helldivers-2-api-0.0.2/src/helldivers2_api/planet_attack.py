from dataclasses import dataclass


@dataclass
class PlanetAttack:
    source_planet_id: int
    target_planet_id: int
