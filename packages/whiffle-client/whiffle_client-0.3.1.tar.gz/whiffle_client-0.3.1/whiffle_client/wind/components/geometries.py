from dataclasses import dataclass, field


@dataclass
class Geometries:
    turbines: dict = field(default=None)
    suggested_les_domain: dict = field(default=None)
    les_domain: dict = field(default=None)
    meso_domain: dict = field(default=None)
