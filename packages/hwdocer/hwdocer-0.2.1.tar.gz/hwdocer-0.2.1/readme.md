# HWDOCER

The [HardWare DOCumentation buildER][home_link] is a utility that help generating graphical documentations using [drawio][drawio_link] and [wireviz][wireviz_link]

## Install

### Stable version

_Stable_ package are release on [pypi.org][pypi_link] and are installable simply via pip:

```bash
pip install hwdocer
```

You can also clone the specific tags from the [repo][repo_link]

### Development version

_Development version_ are only available on the [repo][repo_link], the suggested process is to add a **git submodule** to your project:

1. Add the submodule  
   simply open a **terminal** in the host repo and execute this:

   ```bash
   git submodule add https://gitlab.com/real-ee/public/hwdocer.git dep/hwdocer
   ```

2. Venv install
   Then you need to [install](https://laurencedv.org/computing/python) the venv, by having [poetry][poetry_link] and [pyenv][pyenv_link].  
   Open a **terminal** then execute this:

   ```bash
   poetry install
   ```

## Usage

### Direct call

If you installed the stable version (via [pypi](#stable-version)) you can call it directly like this:

```bash
hwdocer -vv -i "./" -o "./_build"
```

### Python module call

When installed as a python module, you can invoke it

```bash
poetry run python -m hwdocer -vvvv -i "./doc" -o "./doc/build"
```

> NOTE: Currently all `*.yml` file in the _input search_ will match for **harness** drawing and all `*.drawio` files will match for **diagram** drawing

### Adding source to be built

This tool uses [drawio](#drawio) local software and [wireviz](#wireviz) defined file, use them to creat some source file which you pass as _input_ (**-i** argument) to hwdocer.

#### Drawio

To create diagram and drawing that will be then automatically drawn by this tool, you need to install [drawio][drawio_link] local executable by downloading the installer for your OS (only linux tested)

#### Wireviz

To create wire harness, install [wireviz][wireviz_link], which is a project based on [graphviz][graphviz_link] but aimed to specifically draw wire harnesses.

## Contrib

See the [contribution guideline][contrib_file]

## Changelog

See the [release][release_file] file and [roadmap file][roadmap_file]

## License

This software is released under [GPL3][license_file]

<!-- links -->

[home_link]: https://gitlab.com/realee-laurencedv/hwdocbuilder
[poetry_link]: https://python-poetry.org/docs/
[pyenv_link]: https://github.com/pyenv/pyenv
[drawio_link]: https://github.com/jgraph/drawio-desktop/releases/
[wireviz_link]: https://github.com/wireviz/WireViz
[graphviz_link]: https://graphviz.org/
[pypi_link]: https://pypi.org/project/hwdocer/
[repo_link]: https://gitlab.com/realee-laurencedv/hwdocbuilder

<!-- files -->

[release_file]: doc/release.md
[roadmap_file]: doc/roadmap.md
[contrib_file]: doc/contrib.md
[license_file]: license
