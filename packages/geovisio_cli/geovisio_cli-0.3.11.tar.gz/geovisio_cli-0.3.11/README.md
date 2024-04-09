# ![GeoVisio](https://gitlab.com/geovisio/api/-/raw/develop/images/logo_full.png) ![](https://gitlab.example.com/geovisio/cli/-/badges/release.svg)
__GeoVisio__ is a complete solution for storing and __serving your own 📍📷 geolocated pictures__ (like [StreetView](https://www.google.com/streetview/) / [Mapillary](https://mapillary.com/)).

➡️ __Give it a try__ at [panoramax.ign.fr](https://panoramax.ign.fr/) or [geovisio.fr](https://geovisio.fr/viewer) !

## 📦 Components

GeoVisio is __modular__ and made of several components, each of them standardized and ♻️ replaceable.

![GeoVisio architecture](https://gitlab.com/geovisio/api/-/raw/develop/images/big_picture.png)

All of them are 📖 __open-source__ and available online:

|                               🌐 Server                                 |                      💻 Client                       |
|:-----------------------------------------------------------------------:|:----------------------------------------------------:|
|                 [API](https://gitlab.com/geovisio/api)                  |    [Website](https://gitlab.com/geovisio/website)    |
|            [Blur API](https://gitlab.com/geovisio/blurring)             | [Web viewer](https://gitlab.com/geovisio/web-viewer) |
| [GeoPic Tag Reader](https://gitlab.com/geovisio/geo-picture-tag-reader) |   [Command line](https://gitlab.com/geovisio/cli)    |


# ⌨️ GeoVisio Command-line scripts

This repository only contains __command-line interface (CLI)__.

## Features

This tool allows you to:

- Upload a sequence of pictures on a GeoVisio API

It is under __development__, new features will appear in a near future 😉


## Install

GeoVisio CLI can be installed using two methods:

- From [PyPI](https://pypi.org/project/geovisio_cli/), the Python central package repository
- From packaged binaries, availaible in the [latest release page](https://gitlab.com/geovisio/cli/-/releases/)
- Using this [Git repository](https://gitlab.com/geovisio/cli)

Geovisio CLI is compatible with all Python versions >= 3.8.

### From PyPI

Just launch this command:

```bash
pip install geovisio_cli
```

After this you should be able to use the CLI tool with the name `geovisio`:

```bash
geovisio --help
```

Alternatively, you can use [pipx](https://github.com/pypa/pipx) if you want all the script dependencies to be in a custom virtual env.

You need to [install pipx](https://pypa.github.io/pipx/installation/), then:

```bash
pipx install geovisio_cli
```

### From packaged binaries

Packaged binaries are available for windows and linux on AMD64 architecture. The binaries include python and all needed dependencies, so they should be self sufficient.

They are available in the [latest release](https://gitlab.com/geovisio/cli/-/releases).

#### Windows

On windows, just download the windows executable, open a shell in the download directory (you can do that by typing `cmd` in the explorer opened in the directory).

Then you can just do: 
```powershell
geovisio_cli-win-amd64.exe --help
```

### Linux

Prebuild binary have been built for AMD64. They are build using ubuntu 22.04, so they should work for all newer version. For older version though, there might be libstdc++ incompatibilities, if you encounter the problem, you can update libstdc++ or directly use Pypi.

Download the binary, then in the download directory:
```bash
chmod u+x geovisio_cli-linux-amd64
./geovisio_cli-linux-amd64 --help
```

Optional, you can put this in /usr/local/bin (if it's in your path):
```bash
chmod u+x geovisio_cli-linux-amd64
mv geovisio_cli-linux-amd64 /usr/local/bin/geovisio_cli

geovisio_cli --help
```


Note: on linux, it might be easier to use directly pypi package, combined with `pipx` updates will be easier and there should be less problems with libraries version.

### From Git repository

Download the repository:

```bash
git clone https://gitlab.com/geovisio/cli.git geovisio_cli
cd geovisio_cli/
```

To avoid conflicts, it's considered a good practice to create a _[virtual environment](https://docs.python.org/3/library/venv.html)_ (or virtualenv). To do so, launch the following commands:

```bash
# Create the virtual environment in a folder named "env"
python3 -m venv env

# Launches utilities to make environment available in your Bash
source ./env/bin/activate
```

Then, install the GeoVisio CLI dependencies using pip:

```bash
pip install -e .
```

You can also install the `dev` dependencies if necessary (to have lints, format, tests, ...):

```bash
pip install -e .[dev]
```

Then, you can use the `geovisio` command:
```bash
geovisio --help
```


## Usage

All details of available commands are listed in [USAGE.md](./USAGE.md) documentation.

### Upload pictures

The picture upload command is available under the `upload` subcommand:

```bash
geovisio upload --help
```

If you want to upload pictures from a `my_sequence` directory to a GeoVisio instance (running locally in this example), launch this command:

```bash
geovisio upload --api-url http://localhost:5000/ ./my_sequence
```

You can also add a `--wait` flag to wait for geovisio to process all the pictures.

Note that you can launch again the same command to recover a partial sequence import, for example if only some pictures failed to upload.

#### Authentication

If the GeoVisio API requires a login for the upload, the `upload` command will ask for a login on the instance by visiting a given url with a browser. 

You can also login before hand with the command:

```bash
geovisio login --api-url http://localhost:5000/
```

Both will store the credentials in a configuration file, located either in a [XDG](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) defined directory or in a user specific .config, in a subdirectory `geovisio/config.toml`.

If you do not want to use this, you can also provide a geovisio token with the `--token` parameter.

### External metadata

Picture metadata can also be set using a CSV file. This file should be placed in the same directory as pictures, and can be named as you like, as long as it ends with `.csv`. You can name it `_geovisio.csv` for example.

The CSV file should contain all following columns:

Header | Type  | Mandatory ? | Description
-------|-------|-------------|-----------
file   | str   | Yes         | File name of the picture
lon    | float | No          | WGS84 longitude (for example 55.56 for Réunion Island)
lat    | float | No          | WGS84 latitude (for example -21.14 for Réunion Island)
capture_time|str| No         | Capture time of the picture, in [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) (like `1985-04-12T23:20:50.52Z`). If no timezone is given, considered as local time (and thus the date + position would be used to localize it).
Exif.* | str   | No          | Any EXIF tag, with column name following [Exiv2](https://exiv2.org/metadata.html) scheme (example Exif.Image.Artist). You can create as many columns as necessary.
Xmp.*  | str   | No          | Any XMP tag, with column name following [Exiv2](https://exiv2.org/metadata.html) scheme (example Xmp.digiKam.TagsList). You can create as many columns as necessary.

All metadatas defined in the CSV are optional. If a metadata is not defined in CSV for a given image, GeoVisio CLI will try to read it from picture EXIF metadata.

__Note that__ GeoVisio API [will always need some metadata to be present](https://gitlab.com/geovisio/api/-/blob/develop/docs/15_Pictures_requirements.md) (the GPS coordinates and the capture time), no matter where they are read from.

### Collection status

Prints the status of a collection.

```bash
geovisio collection-status --id <some collection id> --api-url http://localhost:5000
```

You can alternatively give the location of the sequence (its full url) like:

```bash
geovisio collection-status --location http://localhost:5000/api/collections/dae288b2-9e8d-4896-af39-d35ce6bc9d4e
```

You can also add a `--wait` flag to wait for geovisio to process all the pictures.

## Development

### Tests

Tests are run using PyTest. By default, our tests use a [Docker Compose](https://docs.docker.com/compose/) environment (located in `./tests/integration/docker-compose-geovisio.yml`) to set-up a temporary GeoVisio API to run onto. If you have Docker Compose enabled and running on your machine, you can simply run this command to launch tests:

```bash
pytest
```

If you don't have Docker Compose, or want to use an existing GeoVisio test instance (to speed up tests), you can pass the `--external-geovisio-url` option to pytest:

```bash
pytest --external-geovisio-url=http://localhost:5000
```

#### Using with an unsecure geovisio API

The CLI parameter `--disable-cert-check` is available to use with an unsecure geovisio API (or when behind proxies messing with ssl). 

There are no automated test for this, but you can run a geovisio with `flask run --cert=adhoc` to manually test this. 

### Documentation

High-level documentation is handled by [Typer](https://typer.tiangolo.com/). You can update the generated `USAGE.md` file using this command:

```bash
make docs
```

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Note that before opening a pull requests, you may want to check formatting and tests of your changes:

```bash
make ci
```

You can also install git [pre-commit](https://pre-commit.com/) hooks to format code on commit with:

```bash
pip install -e .[dev]
pre-commit install
```

### Make a release

```bash
git checkout main
git pull

make docs ci
vim CHANGELOG.md							# Edit version + links at bottom
vim geovisio_cli/__init__.py	# Edit version

git add *
git commit -m "Release x.x.x"
git tag -a x.x.x -m "Release x.x.x"
git push origin main --tags
```


## 🤗 Special thanks

![Sponsors](https://gitlab.com/geovisio/api/-/raw/develop/images/sponsors.png)

GeoVisio was made possible thanks to a group of ✨ __amazing__ people ✨ :

- __[GéoVélo](https://geovelo.fr/)__ team, for 💶 funding initial development and for 🔍 testing/improving software
- __[Carto Cité](https://cartocite.fr/)__ team (in particular Antoine Riche), for 💶 funding improvements on viewer (map browser, flat pictures support)
- __[La Fabrique des Géocommuns (IGN)](https://www.ign.fr/institut/la-fabrique-des-geocommuns-incubateur-de-communs-lign)__ for offering long-term support and funding the [Panoramax](https://panoramax.fr/) initiative and core team (Camille Salou, Mathilde Ferrey, Christian Quest, Antoine Desbordes, Jean Andreani, Adrien Pavie)
- Many _many_ __wonderful people__ who worked on various parts of GeoVisio or core dependencies we use : 🧙 Stéphane Péneau, 🎚 Albin Calais & Cyrille Giquello, 📷 [Damien Sorel](https://www.strangeplanet.fr/), Pascal Rhod, Nick Whitelegg...
- __[Adrien Pavie](https://pavie.info/)__, for ⚙️ initial development of GeoVisio
- And you all ✨ __GeoVisio users__ for making this project useful !


## ⚖️ License

Copyright (c) GeoVisio team 2022-2023, [released under MIT license](https://gitlab.com/geovisio/cli/-/blob/main/LICENSE).
