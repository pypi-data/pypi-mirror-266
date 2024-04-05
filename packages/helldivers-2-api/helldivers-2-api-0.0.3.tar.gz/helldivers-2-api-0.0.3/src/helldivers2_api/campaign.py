from dataclasses import dataclass


@dataclass
class Campaign:
    count: int
    campaign_id: int
    planet_index: int
    campaign_type: int  # ToDo: Map to ENUM
