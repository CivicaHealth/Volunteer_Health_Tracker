# Example models using dataclasses
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ShotType:
    id: int
    name: str
    frequency: int  # days

@dataclass
class VolunteerRecord:
    name: str
    shots: Dict[int, str] = field(default_factory=dict)  # {shot_id: last_date as "YYYY-MM-DD"}
