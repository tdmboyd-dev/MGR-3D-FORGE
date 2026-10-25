"""Strict contracts for deterministic CPU world creation."""

from dataclasses import dataclass, asdict
import json


@dataclass(frozen=True)
class WorldSpec:
    seed: int = 8964
    columns: int = 4
    rows: int = 4
    buildings: int = 10
    lot_size: float = 18.0
    road_width: float = 6.0
    name: str = "MGR Forge Test Neighborhood"

    def __post_init__(self):
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or not (0 <= self.seed <= 2**32 - 1):
            raise ValueError("seed must be an unsigned 32-bit integer")
        if not all(type(v) is int and 1 <= v <= 100 for v in (self.columns, self.rows)):
            raise ValueError("rows/columns must be integers from 1 to 100")
        if type(self.buildings) is not int or not (0 <= self.buildings <= self.columns * self.rows):
            raise ValueError("buildings cannot exceed available lots")
        if not (4 <= self.lot_size <= 100) or not (2 <= self.road_width <= 30):
            raise ValueError("invalid lot or road size")
        if not isinstance(self.name, str) or not (1 <= len(self.name) <= 120):
            raise ValueError("name must be 1-120 characters")

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("world spec must be a JSON object")
        unknown = set(data) - set(cls.__dataclass_fields__)
        if unknown:
            raise ValueError(f"unrecognized world fields: {sorted(unknown)}")
        return cls(**data)

    def as_dict(self):
        return asdict(self)
