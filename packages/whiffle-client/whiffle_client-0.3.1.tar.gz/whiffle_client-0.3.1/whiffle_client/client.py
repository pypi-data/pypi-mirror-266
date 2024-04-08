#!/usr/bin/env python3

import json
import os
import time

import pkg_resources
import platformdirs
import requests
import yaml
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from yamlinclude import YamlIncludeConstructor

from whiffle_client.io import download_write_chunks

CHUNK_SIZE = 1024 * 1024
CONFIG_FILE_NAME = "whiffle_config.yaml"
CONFIG_FILE_PATH_LOCATIONS = [
    f"{platformdirs.user_config_dir('whiffle')}/{CONFIG_FILE_NAME}",  # app path
    f"{CONFIG_FILE_NAME}",  # workdir path
    pkg_resources.resource_filename(
        "whiffle_client", f"resources/{CONFIG_FILE_NAME}"
    ),  # package resource
]

YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader)


class ServerError(BaseException):
    pass


class NoTokenError(Exception):
    pass


class Client:
    """TODO: Client to launch task"""

    def __init__(self, access_token=None, url=None, session=None):
        """
        Authentication order:
        1. `access_token` passed when creating class.
        2. token in CONFIG_FILE_PATH_LOCATIONS (JSON format)
        """
        if access_token is None:
            config = self.get_config()
            access_token = config["user"]["token"]
        if url is None:
            config = self.get_config()
            url = config["whiffle"]["url"]
        self.url = url
        if session is None:
            retries = 5
            backoff_factor = 0.3
            status_forcelist = (500, 502, 503, 504)
            session = session or requests.Session()
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

        self.session = session
        self.session.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        }

    @staticmethod
    def get_config():
        config = None
        for file_path in CONFIG_FILE_PATH_LOCATIONS:
            try:
                with open(file_path) as file_object:
                    config = yaml.safe_load(file_object)
                if config:
                    break
            except FileNotFoundError:
                continue

        if config is None:
            raise FileNotFoundError(
                f"No valid config found on either of {CONFIG_FILE_PATH_LOCATIONS} locations"
            )

        return config

    @staticmethod
    def set_config(config):
        config_file_path = CONFIG_FILE_PATH_LOCATIONS[0]
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, "w") as file_object:
            yaml.safe_dump(config, file_object)

    def _create_request(self, session, endpoint, data=None, params=None, stream=False):
        res = session(self.url + endpoint, data=data, params=params, stream=stream)
        if res.status_code == 200:
            return res
        else:
            try:
                raise ServerError(
                    "message={}, status_code={}".format(
                        res.json()["message"], res.status_code
                    )
                )
            except json.JSONDecodeError:
                raise Exception("{} cannot be reached".format(self.url))

    def new_task(self, input_params_io):
        data = self._get_params_from_io(input_params_io)
        request_url = "/api/aspforge/tasks"
        res = self._create_request(self.session.post, request_url, data=data).json()
        if "warnings" in res:
            for key, value in res["warnings"].items():
                print(f"Warning - {key}: {value}")
        return res["task_id"]

    @staticmethod
    def _get_params_from_io(input_params_io):
        # Reqular Python dictionary, convert to json
        if type(input_params_io) == dict:
            data = json.dumps(input_params_io).encode("ascii")
        # Either a filename or already json
        elif type(input_params_io) == str:
            _, extension = os.path.splitext(input_params_io)
            if extension.lower() in {".json", ".yaml", ".yml"}:
                with open(input_params_io) as f:
                    if extension == ".json":
                        data = f.read()
                    else:
                        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                        data = json.dumps(yaml_data)
            else:
                # Assume the data is json
                json.loads(input_params_io)  # will raise an exception if not
                data = input_params_io
        else:
            raise TypeError("Only dictionary or a filename are allowed")
        return data

    def _cancel_task(self, task_id):
        res = self._create_request(
            self.session.get, "/api/aspforge/tasks/{}/cancel".format(task_id)
        )
        return res.json()["task_status"]

    def get_status(self, task_id):
        res = self._create_request(
            self.session.get, "/api/aspforge/tasks/{}/status".format(task_id)
        )
        return res.json()["task_status"]

    def get_task(self, task_id):
        res = self._create_request(
            self.session.get, "/api/aspforge/tasks/{}/task".format(task_id)
        )
        return res.json()

    def get_metadata(self, task_id):
        res = self._create_request(
            self.session.get, "/api/aspforge/tasks/{}/metadata".format(task_id)
        )
        return res.json()

    def get_tasks(self):
        res = self._create_request(self.session.get, "/api/aspforge/tasks")
        return res.json()

    def get_available_era5_data(self, lon=None, lat=None):
        params = {}
        if lon != None and lat != None:
            params = {"lon": lon, "lat": lat}
        res = self._create_request(
            self.session.get, "api/aspforge/data_sources/era5an_pl", params=params
        )
        if lon != None and lat != None:
            return res.json()
        return res.json()

    def download(self, task_id, filename=None):
        if filename == None:
            filename = task_id + ".zip"
        res = self._create_request(
            self.session.get,
            "/api/aspforge/tasks/{}/download".format(task_id),
            stream=True,
        )
        download_write_chunks(filename, res)

    def get_progress(self, task_id):
        res = self._create_request(
            self.session.get, "/api/aspforge/tasks/{}/progress".format(task_id)
        )
        return res.json()

    # Follow the progress of a task. By default, take the latest task_id.
    def communicate(self, task_id=None, filename=None):
        if task_id == None:
            task_id = self.get_tasks()[-1]["task_id"]
        print(f"Poll for status of task_id: {task_id}")

        # Output
        if filename is None:
            filename = task_id + ".zip"

        # Initialize poll parameters
        status = self.get_status(task_id)
        while status not in ["successful", "failed"]:
            time.sleep(5)
            status = self.get_status(task_id)
            progress = self.get_progress(task_id)
            print(f"status: {status} {progress}\r", end="", flush=True)
        print()

        if status == "successful":
            print("downloading", filename)
            self.download(task_id, filename)
            print("downloaded", filename)

        print(f"\ntask {task_id} finished with status {status}\n")

    # Create a new task and follow its progress
    def process(self, task_params, filename=None):
        task_id = self.new_task(task_params)
        print("submitted task {}".format(task_id))

        self.communicate(task_id, filename=filename)
        return task_id

    # Cancel a running task
    def cancel(self, task_id=None):
        curr_status = self.get_status(task_id=task_id)
        if curr_status not in ["successful", "failed"]:
            self._cancel_task(task_id)
            print("cancelled task {}".format(task_id))
        else:
            print(f"Task <{task_id}> in status <{curr_status}>. Can not be cancelled.")
