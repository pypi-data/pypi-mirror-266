# python-SysInformer

The python-SysInformer is a system information tool that allows users to retrieve various types of information about their system. It offers functionalities to gather CPU details, memory information, disk space usage, network activity, process status, container information, and system statistics such as OS type, uptime, and hostname.

## Why another system information tool?

Numerous system information tools, like [htop](https://htop.dev/), [glances](https://nicolargo.github.io/glances/), and [neofetch](https://github.com/dylanaraps/neofetch), serve Linux systems. While they're excellent, this tool isn't meant to replace them. Instead, it simplifies retrieving both critical and occasional system details. For instance, to quickly find a host IP, instead of using `ip a` and potentially adding `grep`, you can now utilize `psi run -n`. Similarly, to check container ports, the lengthy `docker ps` command can be swapped for `psi -ct`.

Additionally, this project is my venture to enhance my Python capabilities. While not a developer, I frequently script and automate tasks. I've been using Python for a few months now, but I've never really taken the time to learn the language. I've always just learned what I needed to get the job done. I've been wanting to change that and this project is my first attempt at doing so. I'm sure there are many things that could be done better, but I'm happy with the progress I've made and the knowledge I've gained so far.


## Features

The following gif demonstrates some of the tool's features:

![psi-gif](./images/psi.gif)

## Getting Started

### Prerequisites

The tool requires Python 3.11 or higher. Additionally, the tool is inteneded to be used on Linux systems only. It will work on macOS systems, but may not be able to retrieve all information. The tool is not intended to be used on Windows systems.

## Dependencies

The tool uses the following Python packages:

- distro
- netifaces
- ping3
- psutil
- PyYAML
- tabulate

## Installation

The easiest way to install the tool is with `pip`:

```bash
  pip install python-SysInformer
```

Additionaly, if you have [poetry](https://python-poetry.org/) installed you can install the tool with:

```bash
git clone [this repo]
poetry install

# OR

poetry add python-SysInformer
```

Finally, you can install the tool from source:

```bash
git clone [this repo]
pip install -r requirements.txt
```

## Usage

The tool is intended to be used as a command line tool:

```bash
Usage: psi [OPTIONS] COMMAND [ARGS]...

  System information tool.

Options:
  --help  Show this message and exit.

Commands:
  config  The config command is used to create a default config file.
  run     The run command is the main command for the tool.
```

The most basic usage to retrieve all information is:

```bash
psi run -a
```

If you prefer to only retrieve specific information, you can use the following options:

```bash
Options:
  -a, --all           Show all information
  -s, --system        Show only system information
  -c, --cpu           Show only CPU information
  -m, --memory        Show only memory information
  -d, --disk          Show only disk information
  -n, --network       Show only network and latency information
  -ps, --processes    Show only services information
  -ct, --containers   Show only running container (docker or podman)
                      information
```

## Configuration

You can configure the tool using a YAML file. Currently, the configuration options allow you to specify services and ports to monitor for their operational status, and set targets to ping to measure latency.

A default configuration file can be created using the `psi config --create` command. By default, the configuration file is located at `~/.config/psi/config.yaml`. If you'd like to use a different location, simply provide the path using the `--config-path` e.g. `psi config --create --config-path /some/path/config.yaml`. You can then pass the path to the `psi run` command using the same option.

The config file itself is fairly basic and looks like this:

```yaml
services:
  - name: FTP Server
    port: 21
    host: localhost
  - name: SSH
    port: 22
    host: localhost
  - name: HTTP
    port: 80
    host: localhost
  - name: HTTPS
    port: 443
    host: localhost
  - name: MySQL Server
    port: 3306
    host: localhost
  - name: PostgreSQL Server
    port: 5432
    host: localhost

ping_hosts:
  - google.com
  - timothybryantjr.com
  - github.com
```

**Note:** The tool will still run without a config file, but will not be able to check up or down status for services or ping targets for latency information.

## Acknowledgements

This tool was inspired by [eZ Server Monitor](https://www.ezservermonitor.com/). Specfically, their [eSMsh](https://www.ezservermonitor.com/esm-sh/features) feature which allows users to retrieve system information from the command line via a bash script. In fact, if you want the portability of a bash script, I would recommend using eSMsh. I'm not sure if the script is still being maintained, but it is still available on [Github](https://github.com/shevabam/ezservermonitor-sh). But if you don't mind using Python, and want a little more information, then the python-SysInformer tool could be for you.
