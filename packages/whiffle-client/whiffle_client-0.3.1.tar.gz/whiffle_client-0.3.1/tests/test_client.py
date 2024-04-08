import yaml
import json
import subprocess
from click.testing import CliRunner
from whiffle_client import Client
from whiffle_client.entrypoints import whiffle

default_task_path = "whiffle_client/resources/example_generic_params.json"
task_with_yaml_include_path = "whiffle_client/resources/example_yaml_include.yaml"
runner = CliRunner()


def get_default_task():
    with open(default_task_path) as f:
        return json.load(f)


class MockResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


def mock_new_task_response(mocker, warnings={}):
    mocker.patch(
        "whiffle_client.Client._create_request",
        return_value=MockResponse(
            {"task_id": "hash1234", "task_status": "created", "warnings": warnings}
        ),
    )


class TestAPI:
    def test_init_client_with_default_params(self):
        config = Client.get_config()
        client = Client()
        assert client.url == config["whiffle"]["url"]
        assert config["user"]["token"] in client.session.headers["Authorization"]

    def test_init_client_with_given_params(self):
        token = "test_token"
        url = "https://test_url.com"
        client = Client(token, url)

        assert client.url == url
        assert token in client.session.headers["Authorization"]

    def test_new_task_from_dict(self, mocker):
        task = get_default_task()
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(task)
        assert type(task_id) == str

    def test_new_task_from_json(self, mocker):
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(default_task_path)
        assert type(task_id) == str

    def test_new_task_from_yaml(self, mocker, tmp_path):
        task = get_default_task()
        path = f"{tmp_path}/task.yaml"
        with open(path, "w") as f:
            yaml.safe_dump(task, f)
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(path)
        assert type(task_id) == str

    def test_new_task_from_yaml_with_include(self, mocker, tmp_path):
        task = get_default_task()
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(task_with_yaml_include_path)
        assert type(task_id) == str

    def test_new_task_with_warnings(self, mocker, capsys):
        warnings = {"version": "incorrect version"}

        task = get_default_task()
        client = Client()
        mock_new_task_response(mocker, warnings)
        client.new_task(task)
        captured = capsys.readouterr()
        assert "incorrect version" in captured.out


class TestCli:
    def test_list_config(self):
        config = Client.get_config()
        res = runner.invoke(whiffle, ["config", "list"])
        assert yaml.safe_dump(config) in res.output

    def test_edit_config(self):
        token = "test_token"
        res = runner.invoke(whiffle, ["config", "edit", "user.token", token])
        assert token in res.output
        res = runner.invoke(whiffle, ["config", "list"])
        assert token in res.output

    def test_run_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.process")
        runner.invoke(whiffle, ["task", "run", default_task_path])
        mock.assert_called_once()

    def test_task_list(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.get_tasks")
        runner.invoke(whiffle, ["task", "list"])
        mock.assert_called_once()

    def test_download_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.download")
        res = runner.invoke(whiffle, ["task", "download", "123"])
        assert not "Error" in res.output, res.output
        mock.assert_called_once()

    def test_attach_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.communicate")
        runner.invoke(whiffle, ["task", "attach", "123"])
        mock.assert_called_once()

    def test_cancel_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.cancel")
        res = runner.invoke(whiffle, ["task", "cancel", "123"])
        assert not "Error" in res.output, res.output
        mock.assert_called_once()

    def test_version(self):
        git_version = subprocess.check_output(["git", "describe"]).decode()[:5]
        res = runner.invoke(whiffle, ["--version"])
        # res.output = "whiffle-client, version 0.2.9.post1+git.adbca4e1.dirty"
        cli_version = res.output.split(" ")[2][:5]
        assert cli_version == git_version
