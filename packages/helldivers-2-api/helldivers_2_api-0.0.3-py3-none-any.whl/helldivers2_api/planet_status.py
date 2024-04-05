from dataclasses import dataclass

from helldivers2_api.faction import Faction
from helldivers2_api.planet import Planet


@dataclass
class PlanetStatus:
    planet_id: int
    planet_info: Planet
    health: int
    owner: Faction
    players: int
    regen_per_second: float
