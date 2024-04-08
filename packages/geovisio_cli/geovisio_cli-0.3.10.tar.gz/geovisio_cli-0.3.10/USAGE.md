# `geovisio`

GeoVisio command-line client (v0.3.9)

**Usage**:

```console
$ geovisio [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show GeoVisio command-line client version and exit
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `collection-status`: Print the status of a collection.
* `login`: Authenticate into the given instance, and...
* `test-process`: (For testing) Generates a TOML file with...
* `upload`: Processes and sends a given sequence on...

## `geovisio collection-status`

Print the status of a collection.

Either a --location should be provided, with the full location url of the collection
or only the --id combined with the --api-url

**Usage**:

```console
$ geovisio collection-status [OPTIONS]
```

**Options**:

* `--id TEXT`: Id of the collection
* `--api-url TEXT`: GeoVisio endpoint URL
* `--location TEXT`: Full url of the collection
* `--wait / --no-wait`: wait for all pictures to be ready  [default: no-wait]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while uploading. This should not be used, unless if you -really- know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.

## `geovisio login`

Authenticate into the given instance, and save credentials in a configuration file.

This will generate credentials, and ask the user to visit a page to associate those credentials to the user's account.

The credentials will be stored in /home/a_user/.config/geovisio/config.toml

**Usage**:

```console
$ geovisio login [OPTIONS]
```

**Options**:

* `--api-url TEXT`: GeoVisio endpoint URL  [required]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while uploading. This should not be used, unless if you -really- know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.

## `geovisio test-process`

(For testing) Generates a TOML file with metadata used for upload

**Usage**:

```console
$ geovisio test-process [OPTIONS] PATH
```

**Arguments**:

* `PATH`: Local path to your sequence folder  [required]

**Options**:

* `--title TEXT`: Collection title. If not provided, the title will be the directory name.
* `--sort-method [filename-asc|filename-desc|time-asc|time-desc]`: Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.  [default: time-asc]
* `--split-distance INTEGER`: Maximum distance between two pictures to be considered in the same sequence (in meters).  [default: 100]
* `--split-time INTEGER`: Maximum time interval between two pictures to be considered in the same sequence (in seconds).  [default: 60]
* `--duplicate-distance FLOAT`: Maximum distance between two pictures to be considered as duplicates (in meters).  [default: 1]
* `--duplicate-rotation INTEGER`: Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).  [default: 30]
* `--help`: Show this message and exit.

## `geovisio upload`

Processes and sends a given sequence on your GeoVisio API

**Usage**:

```console
$ geovisio upload [OPTIONS] PATH
```

**Arguments**:

* `PATH`: Local path to your sequence folder  [required]

**Options**:

* `--api-url TEXT`: GeoVisio endpoint URL  [required]
* `--wait / --no-wait`: Wait for all pictures to be ready  [default: no-wait]
* `--is-blurred / --is-not-blurred`: Define if sequence is already blurred or not  [default: is-not-blurred]
* `--title TEXT`: Collection title. If not provided, the title will be the directory name.
* `--token TEXT`: GeoVisio token if the geovisio instance needs it.

If none is provided and the geovisio instance requires it, the token will be asked during run.
Note: is is advised to wait for prompt without using this variable.
* `--sort-method [filename-asc|filename-desc|time-asc|time-desc]`: Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.  [default: time-asc]
* `--split-distance INTEGER`: Maximum distance between two pictures to be considered in the same sequence (in meters).  [default: 100]
* `--split-time INTEGER`: Maximum time interval between two pictures to be considered in the same sequence (in seconds).  [default: 60]
* `--duplicate-distance FLOAT`: Maximum distance between two pictures to be considered as duplicates (in meters).  [default: 1]
* `--duplicate-rotation INTEGER`: Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).  [default: 30]
* `--picture-upload-timeout FLOAT`: Timeout time to receive the first byte of the response for each picture upload (in seconds)  [default: 60.0]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while uploading. This should not be used, unless if you -really- know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.
