import datetime
import json
from dataclasses import InitVar, asdict, dataclass, field

import pandas as pd
import yaml
from yamlinclude import YamlIncludeConstructor

from whiffle_client.wind.components import Domain, Geometries, Metmast, Turbine
from whiffle_client.wind.loaders import csv_loader_constructor

YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader)
yaml.add_constructor("!include-csv", csv_loader_constructor)

READ_ONLY_FIELDS = set(
    [
        "id",
        "user",
        "status",
        "messages",
        "creation_datetime",
        "last_updated",
        "reference_number",
        "configuration_valid",
        "geometries",
        "domain",
    ]
)


@dataclass
class WindSimulationTask:
    # Init only attributes
    name: InitVar[str] = ""

    # Metadata attributes
    id: str = field(default=None)
    status: str = field(default=None)
    messages: list[dict] = field(default=None)
    user: dict = field(default=None)
    creation_datetime: datetime.datetime = field(default=None)
    last_updated: datetime.datetime = field(default=None)
    reference_number: str = field(default=None)
    reference_code: str = field(default=None)
    simulation_name: str = field(default=None)
    run_simulations: bool = field(default=True)
    # test_run: bool = field(default=None)
    configuration_valid: bool = field(default=None)

    # Time attributes
    dates: list[datetime.datetime] = field(default=None)

    # Domain/object/geolocated elements attributes
    turbines: list[Turbine] = field(default=None)
    geometries: Geometries = field(default=None)
    domain: Domain = field(default=None)
    metmasts: list[Metmast] = field(default=None)
    metmasts_heights: list[float] = field(default=None)

    # Output attributes
    wind_resource_grid: dict = field(default=None)
    fields: dict = field(default=None)

    def __post_init__(self, name: str = None):
        if not self.simulation_name:
            self.simulation_name = name

        if isinstance(self.dates, dict):
            dates_range = pd.date_range(
                self.dates["start"], self.dates["end"], freq="1D"
            )
            self.dates = [date.date().isoformat() for date in dates_range]

    @classmethod
    def from_request(cls, params):
        instance_params = {}
        for dataclass_key in WindSimulationTask.__dataclass_fields__:
            if dataclass_key in params:
                # We want to populate instance with dataclass defaults
                instance_params[dataclass_key] = params[dataclass_key]
        return cls(**instance_params)

    @classmethod
    def from_yaml(cls, path):
        params = yaml.load(open(path), Loader=yaml.FullLoader)

        turbines = []
        for windfarm_name in params.get("turbines", {}):
            windfarm = params["turbines"][windfarm_name]
            for name, location in zip(windfarm["name"], windfarm["location"]):
                turbines.append(
                    {
                        "name": name,
                        "longitude": location[0],
                        "latitude": location[1],
                        "turbine_model": windfarm["turbine_model"],
                        "windfarm": windfarm_name,
                    }
                )
        params["turbines"] = turbines

        metmasts = []
        if params.get("metmasts", False):
            for name, location in zip(
                params["metmasts"]["name"], params["metmasts"]["location"]
            ):
                metmasts.append(
                    {
                        "name": name,
                        "longitude": location[0],
                        "latitude": location[1],
                    }
                )
        params["metmasts"] = metmasts
        params["metmasts_heights"] = params.get("metmasts_heights", [])

        instance_params = {}
        for dataclass_key in WindSimulationTask.__dataclass_fields__:
            if dataclass_key in params:
                # We want to populate instance with dataclass defaults
                instance_params[dataclass_key] = params[dataclass_key]
        return cls(**instance_params)

    def __str__(self) -> str:
        return f"WindSimulationTask:\n{json.dumps(asdict(self), indent=4)}"

    def __repr__(self) -> str:
        return json.dumps(asdict(self))

    def _get_api_params(self):
        params = asdict(self)
        _ = [params.pop(key, None) for key in READ_ONLY_FIELDS]
        return params
