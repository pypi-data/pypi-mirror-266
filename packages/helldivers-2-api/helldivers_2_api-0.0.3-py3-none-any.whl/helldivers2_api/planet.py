from dataclasses import dataclass

from helldivers2_api.sector import Sector


@dataclass
class Planet:
    planet_id: int
    name: str
    sector: Sector
