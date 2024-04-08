#!/usr/bin/env python3

import json
import os
import pathlib
from typing import List
from urllib.parse import urlparse

import pkg_resources
import platformdirs
import requests
import yaml
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from whiffle_client.io import download_write_chunks, VALID_DOWNLOAD_FILES
from whiffle_client.wind.wind_simulation_task import WindSimulationTask

API_VERSION = "v1"  # TODO: make this configurable -> ENV?
CONFIG_FILE_NAME = "whiffle_config.yaml"

CONFIG_FILE_PATH_LOCATIONS = [
    f"{platformdirs.user_config_dir('whiffle')}/{CONFIG_FILE_NAME}",  # app path
    f"{CONFIG_FILE_NAME}",  # workdir path
    pkg_resources.resource_filename(
        "whiffle_client", f"resources/{CONFIG_FILE_NAME}"
    ),  # package resource
]


class WindSimulationClient:
    """
    Client for the Wind Simulation API.
    """

    # API variables
    SERVER_URL: str = ""
    ENDPOINTS_URL: str = f"/api/{API_VERSION}/wind"

    # Type method
    def __init__(self, access_token: str = None, server_url: str = None):
        """
        Initialize the client.

        Authentication order:
        1. `access_token` passed when creating class.
        2. token in CONFIG_FILE_PATH_LOCATIONS (JSON format)

        Parameters
        ----------
        access_token : str, optional
            Token for client session auth
        url : str, optional
            Url pointing to API
        """

        if access_token is None:
            config = self._get_config()
            access_token = config["user"]["token"]
        headers = f"Bearer {access_token}"

        if server_url is None:
            config = self._get_config()
            server_url = config["whiffle"]["url"]
        self.SERVER_URL = server_url

        # More docs: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry
        status_forcelist = (500, 502, 503, 504)
        retry = Retry(
            total=5,  # Total number of retries to allow
            backoff_factor=0.1,  # Incremental time between retry requests
            status_forcelist=status_forcelist,  # A set of integer HTTP status codes that will force a retry on
        )
        adapter = HTTPAdapter(max_retries=retry)

        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers = {
            "Content-Type": "application/json",
            "Authorization": headers,
        }

    def __repr__(self) -> str:
        return f"Whiffle wind client connected to url: {self.SERVER_URL}"

    @staticmethod
    def _get_config():
        """Gathers client configuration from resources or from user config directory.

        Returns
        -------
        dict
            Dictionary containing the configuration.

        Raises
        ------
        FileNotFoundError
            Raises error if no configuration found
        """
        config = None
        for file_path in CONFIG_FILE_PATH_LOCATIONS:
            try:
                with open(file_path) as file_object:
                    config = yaml.safe_load(file_object)
                if config:
                    break
            except FileNotFoundError:
                continue
        else:
            raise FileNotFoundError(
                f"No valid config found on either of {CONFIG_FILE_PATH_LOCATIONS} locations"
            )

        return config

    # Wind simulation commands
    def run(
        self,
        path: str = "",
        simulation_task: WindSimulationTask = None,
        extra_params: dict = {},
    ):
        """Run a wind simulation given a path to a configuration or an instance of a WindSimulationTask

        Parameters
        ----------
        path : str, optional
            Path to valid configuration of a wind simulation task, by default ""
        simulation_task : WindSimulationTask, optional
            Instance of a WindSimulationTask, by default None
        extra_params : dict, optional
            Dictionary with extra parameters that can be provided to the simulation, by default {}

        Returns
        -------
        WindSimulationTask
            Instance of launched object
        """
        path = pathlib.Path(path)
        if path.suffix in [".yaml", ".yml"]:
            simulation_task = self.new_wind_simulation_from_yaml(path=path)

        if extra_params.get("thrustless", False):
            for turbine in simulation_task.turbines:
                turbine["thrustless"] = True
            simulation_task.simulation_name += " - Thrustless"
            self.update_wind_simulation(simulation_task)

        # TODO: update simulation_task status to queued to launch it
        wind_simulation_task = self.session.post(
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}/{simulation_task.id}/submit",
            data=json.dumps(simulation_task._get_api_params()),
        )
        try:
            wind_simulation_task.raise_for_status()
        except Exception:
            raise ValueError(wind_simulation_task.json())
        return WindSimulationTask.from_request(wind_simulation_task.json())

    def get_all_wind_simulation(self) -> List[WindSimulationTask]:
        """Get all Wind Simulation accessible by user

        Returns
        -------
        List[WindSimulationTask]
            List of WindSimulationTask
        """
        wind_simulation_tasks_params = self.session.get(
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}"
        )
        try:
            wind_simulation_tasks_params.raise_for_status()
        except Exception:
            raise ValueError(wind_simulation_tasks_params.json())
        # return wind_simulation_tasks_params.json()
        return [
            WindSimulationTask.from_request(params)
            for params in wind_simulation_tasks_params.json()
        ]

    def get_wind_simulation(self, wind_simulation_id: str) -> WindSimulationTask:
        """Get Wind Simulation from id

        Parameters
        ----------
        wind_simulation_id : str
            Id of previous wind simulation

        Returns
        -------
        WindSimulationTask
            Requested WindSimulationTask
        """
        wind_simulation_task = self.session.get(
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}/{wind_simulation_id}"
        )
        try:
            wind_simulation_task.raise_for_status()
        except Exception:
            raise ValueError(wind_simulation_task.json())
        return WindSimulationTask.from_request(wind_simulation_task.json())

    def new_wind_simulation(self, data: dict = {}):
        wind_simulation_task = self.session.post(
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}", data=json.dumps(data)
        )
        try:
            wind_simulation_task.raise_for_status()
        except Exception:
            raise ValueError(wind_simulation_task.json())
        return WindSimulationTask.from_request(wind_simulation_task.json())

    def new_wind_simulation_from_instance(self, data: WindSimulationTask):
        if not isinstance(data, WindSimulationTask):
            raise ValueError("Data parameter should be a WindSimulationTask instance")
        return self.new_wind_simulation(data._get_api_params())

    def new_wind_simulation_from_yaml(self, path: str):
        simulation_task = WindSimulationTask.from_yaml(path=path)
        return self.new_wind_simulation(simulation_task._get_api_params())

    def update_wind_simulation(self, data: WindSimulationTask):
        if not isinstance(data, WindSimulationTask):
            raise ValueError("Data parameter should be a WindSimulationTask instance")

        wind_simulation_id = data.id
        wind_simulation_task = self.session.put(
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}/{wind_simulation_id}",
            data=json.dumps(data._get_api_params()),
        )
        try:
            wind_simulation_task.raise_for_status()
        except Exception:
            raise ValueError(wind_simulation_task.json())
        return WindSimulationTask.from_request(wind_simulation_task.json())

    def delete_wind_simulation(self, wind_simulation_id: str):
        wind_simulation_task = self.session.delete(
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}/{wind_simulation_id}",
        )
        try:
            wind_simulation_task.raise_for_status()
        except Exception:
            raise ValueError(wind_simulation_task.json())

        return WindSimulationTask.from_request(wind_simulation_task.json())

    def download_wind_simulation(
        self,
        wind_simulation_id: str,
        file: str = "results",
        output_dir: str = None,
    ):
        if not output_dir:
            output_dir = os.getcwd()
        if file and file not in VALID_DOWNLOAD_FILES:
            raise ValueError(
                f"File type <{file}> is not in the valid file types <{VALID_DOWNLOAD_FILES}>"
            )

        download_url = (
            f"{self.SERVER_URL}{self.ENDPOINTS_URL}/{wind_simulation_id}/download_url"
        )
        download_url += f"?file_path={file}" if file else ""
        wind_simulation_task_file = self.session.get(download_url)
        wind_simulation_task_file.raise_for_status()
        local_filename = os.path.basename(
            urlparse(wind_simulation_task_file.json()["url"]).path
        )
        print(
            f"Fetch <{file}> data of simulation <{wind_simulation_id}> and store it at: <{local_filename}>"
        )
        file_request = requests.get(wind_simulation_task_file.json()["url"])

        download_write_chunks(f"{output_dir}/{local_filename}", file_request)

    # Turbine models commands
    def add_turbine_model(self, path: str = "", thrustless=False):
        data = yaml.load(open(path), Loader=yaml.FullLoader)
        if thrustless:
            data["name"] += " - Thrustless"
            data["thrust_coefficient"] = [0] * len(data["thrust_coefficient"])

        return self.session.post(
            f"{self.SERVER_URL}/api/aspforge/turbines", data=json.dumps(data)
        )

    def edit_turbine_model(self, turbine_model_name, path: str = ""):
        data = yaml.load(open(path), Loader=yaml.FullLoader)
        return self.session.put(
            f"{self.SERVER_URL}/api/aspforge/turbines/{turbine_model_name}",
            data=json.dumps(data),
        )

    def get_turbine_model(self, turbine_model_name):
        return self.session.get(
            f"{self.SERVER_URL}/api/aspforge/turbines/{turbine_model_name}"
        )

    def delete_turbine_model(self, turbine_model_name):
        return self.session.delete(
            f"{self.SERVER_URL}/api/aspforge/turbines/{turbine_model_name}"
        )
