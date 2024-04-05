# Installation

We provide two main ways of installation,
either directly via `pip` or using the fully packaged installer
that can be found in our [releases](https://github.com/RIMS-Code/RIMSSchemeDrawer/releases).

!!! note "Fully packaged installer"
    As of version `v3`, the fully packaged release is created with
    [`PyApp`](https://ofek.dev/pyapp/latest/).
    This has various advantages for our own workflow,
    however, requires that you have an internet connection when first starting the software.
    `PyApp` will create a virtual environment for you and install the software there,
    however, will need to download all dependencies in the process.

## Installation via `pip`

We highly recommend using [`pipx`](https://pipxproject.github.io/pipx/)
to install the software.
To do so,
simply run the following command in your terminal:

```bash
pipx install rimsschemedrawer[gui]
```

This will install the software and all its dependencies in an isolated environment.
You can then run the software by simply typing `rimsschemedrawer` in your terminal.

## Installation via the fully packaged installer

Download the latest release from [here](https://github.com/RIMS-Code/RIMSSchemeDrawer/releases)
by choosing the appropriate file for your operating system.
After downloading,
simply run the file.

!!! note
    The files are not signed and you might get a warning from your operating system.
