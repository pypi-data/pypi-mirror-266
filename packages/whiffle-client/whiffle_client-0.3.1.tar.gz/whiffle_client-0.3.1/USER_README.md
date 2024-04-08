# Whiffle client

## Quickstart

`whiffle-client` can be installed with `pip` as follows:

`pip install whiffle-client` or `pip install "whiffle-client[analysis]"` to include data-analysis packages.

This client allows running atmospheric large-eddy simulations (LES) with Whiffle's GPU-resident model <https://whiffle.nl/>. 
The client requires an access token, which you can configure with the command line interface by executing,

`whiffle config edit user.token <your_token>`

You can create a new task by executing,

`whiffle task run <path_to_the_task_specification.[json|yaml]>`

The client polls the progress of the task until it has finished. The task will run in the background if you abort the client.
You can list the most recent tasks by executing,

`whiffle task list`

If you need an access token or you have any questions, please reach out to <support@whiffle.nl>.


## Command-line interface

### List the configuration

`whiffle config list`

### Change the token in the configuration

`whiffle config edit user.token <your_token>`

NOTE: configuration will be stored on user config directory.
> Unix  systems `~/.config/whiffle/whiffle_config.yaml`

> macOS systems `~/Library/Application Support/whiffle/whiffle_config.yaml`

> Windows systems `%USERPROFILE%\AppData\Local\whiffle\whiffle_config.yaml`

### Run a task

`whiffle task run <path_to_the_task_specification.[json|yaml]>`


### List tasks

`whiffle task list <number of tasks>`

### Download a task

`whiffle task download <task_id>`

### Attach a task

You can monitor the progress of a task and it will be automatically downloaded once the task has been successfully completed. 

`whiffle task attach <task_id>`

### Cancel a task

A task on a non-finished status can be cancelled with the following command: 

`whiffle task cancel <task_id>`

## Task description file formats

Allowed file formats are JSON and YAML. The YAML format supports includes through [pyyaml-include](https://github.com/tanbro/pyyaml-include).

Here is an example of a YAML file with include:

The task.yaml file describes the task and includes the metmasts value from another file
``` 
metmasts: !include example_yaml_include_metmasts.yaml
```

and the example_yaml_include_metmasts.yaml file specifies the metmasts:
```
example_metmast_collection:
  id:
  - metmast0
  - metmast1
  lat:
  - 52.1
  - 52.2
  lon:
  - 3.1
  - 3.2
  z:
  - 10
  - 100
```
