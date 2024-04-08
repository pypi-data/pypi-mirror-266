import click
import yaml

from whiffle_client import Client


@click.group()
@click.version_option(prog_name="whiffle-client")
def whiffle():
    pass


@whiffle.group()
def wind():
    """Wind api commands"""
    ...


@whiffle.group()
def task():
    """Task commands"""
    pass


@whiffle.group()
def config():
    """Edit config"""
    pass


@task.command()
@click.argument("number_of_tasks", default=10)
def list(number_of_tasks):
    """List tasks"""

    number_of_tasks = int(number_of_tasks)
    client = Client()
    tasks = client.get_tasks()
    click.echo(
        "{:33}{:11}{:16} {:16} progress".format(
            "task id", "status", "start time", "finish time"
        )
    )
    for task in tasks[-number_of_tasks:]:
        finished = task["finished"]
        if finished == None:
            task["finished"] = ""
        click.echo(
            "{task_id:33}{task_status:11}{received:17.16}{finished:17.16}{processed_steps}/{total_steps}".format(
                **task
            )
        )


@task.command()
@click.argument("file_path")
def run(file_path) -> str:
    """Run task type given a set of parameters.

    \b
    Parameters
    ----------
    file_path : str
        Path to (json|yaml) file containing parameters

    \b
    Returns
    -------
    str
        Name of the launched task
    """
    click.echo(f"run task with params: file_path={file_path}")
    client = Client()
    return client.process(file_path)


@config.command()
@click.argument("key")
@click.argument("value")
def edit(key, value) -> str:
    """Edit Whiffle configuration file

    \b
    Parameters
    ----------
    key : str
        Dot separated key value (e.g.: user.token)
    value : str
        Value to fill the configuration key with
    """
    config_key = key.split(".")
    config = Client.get_config()

    sub_config = config
    for sub_key in config_key[:-1]:
        if sub_key in sub_config:
            sub_config = sub_config[sub_key]
        else:
            raise KeyError(f"Key {sub_key} does not exist")
    try:
        if config_key[-1] not in sub_config:
            raise KeyError
        sub_config[config_key[-1]] = value
    except KeyError:
        raise KeyError(f"Key {config_key[-1]} does not exist")

    Client.set_config(config=config)
    click.echo(f"{key} changed to {value}")


@config.command()
def list():
    """List configuration values"""

    config = Client.get_config()

    click.echo("Current configuration:\n-----\n")
    click.echo(yaml.safe_dump(config))
    click.echo("-----")


@task.command()
@click.argument("task_id")
def download(task_id):
    """Download task

    \b
    Parameters
    ----------
    task_id : str
    """
    click.echo(f"downloading task output {task_id}")
    client = Client()
    client.download(task_id)


@task.command()
@click.argument("task_id")
def attach(task_id):
    """attach task"""
    click.echo(f"attaching to the task {task_id}")
    client = Client()
    client.communicate(task_id)


@task.command()
@click.argument("task_id")
def cancel(task_id):
    """cancel task"""
    click.echo(f"cancelling task {task_id}")
    client = Client()
    client.cancel(task_id)


# Whiffle wind API commands
