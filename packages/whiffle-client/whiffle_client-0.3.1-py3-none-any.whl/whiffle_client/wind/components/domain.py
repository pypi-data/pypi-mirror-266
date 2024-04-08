from dataclasses import dataclass, field


@dataclass
class Domain:
    longitude: float = field(default=None)
    latitude: float = field(default=None)
    cells: list[float] = field(default=None)
    resolution: list[float] = field(default=None)
