from dataclasses import dataclass, field


@dataclass
class Turbine:
    name: str = field(default=None)
    longitude: float = field(default=None)
    latitude: float = field(default=None)
    turbine_model: str = field(default=None)
    windfarm: str = field(default="windfarm")
    internal: bool = field(default=True)
    thrustless: bool = field(default=False)
