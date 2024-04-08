[![PyPI versions](https://img.shields.io/pypi/pyversions/nettowel.svg)](https://pypi.python.org/pypi/nettowel/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![Downloads](https://pepy.tech/badge/nettowel)](https://pepy.tech/project/nettowel)

# NetTowel
Collection of useful network automation functions 


> ⚠️ `nettowel` is under heavy construction and not production ready. Feedback is highly appreciated.


## Install
It is recommended to install `nettowel` with [pipx](https://pipx.pypa.io/). Therefore you have the dependencies isolated and you can use the `nettowel` or `nt` command.

```bash
pipx install nettowel[full]
```

You can also install it directly from pypi

```bash
pip install nettowel
```

To reduce the dependencies the extra dependencies are grouped

The following groups are available (more details in the pyproject.toml):

- full
- jinja
- ttp
- textfsm
- napalm
- netmiko
- scrapli
- nornir
- pandas
- jsonpatch
- tui

```bash
pip install nettowel[jinja]
pip install nettowel[full]
```

## Install from source

```
git clone ....
cd nettowel
poetry install
poetry run nettowel --help
```


## Help and shell auto-completion

Thanks to the library [typer](https://typer.tiangolo.com/), `nettowel` comes with a nice help and autocompletion install

![help](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/help.png)


## Features

Many features are not implemented yet and many features will come.



### Jinja2

#### render

![jinja rendering 1](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/jinja-render-3.png)

![jinja rendering 2](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/jinja-render-1.png)

#### validate

![jinja validate](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/jinja-validate.png)

#### variables

![jinja variables](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/jinja-variables.png)


### TTP

#### render

![ttp render](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/ttp-render.png)

### Netmiko

#### cli

![netmiko cli](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/netmiko-cli.png)

#### autodetect

![netmiko autodetect](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/netmiko-autodetect.png)

#### device-types

![netmiko device types](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/netmiko-device-types.png)


### RESTCONF

#### get

![restconf get](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/restconf-get.png)

#### patch, delete

![restconf patch delete](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/restconf-patch-delete.png)

#### post, put

![restconf post put](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/restconf-post-put.png)

### ipaddress

#### ip-info

![ip info](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/ip-info.png)

#### network-info

![network info](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/network-info.png)


### YAML

#### load

![yaml load](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/yaml-load.png)

#### dump

![yaml dump](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/yaml-dump.png)


### JSON Patch ([RFC 6902](http://tools.ietf.org/html/rfc6902))

#### create

![JSON Patch create](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/jsonpatch-create.png)

#### apply

![JSON Patch apply](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/jsonpatch-apply.png)


### Help

![Help QRcode](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/nettowel-help.png)


### Settings

A `dotenv` file can be used as a settings file. The file can also be provided with the option `--dotenv`.

![environment settings](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/env-settings.png)


### Piping

![piping](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/piping.png)


### TUI

Using [Trogon](https://github.com/Textualize/trogon) a TUI (Terminal User Interface) can be generated to edit and run the NetTowel command.

![TUI](https://raw.githubusercontent.com/InfrastructureAsCode-ch/nettowel/main/imgs/trogon.png)
