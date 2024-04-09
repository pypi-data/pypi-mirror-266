import pytest
import os
from geovisio_cli.sequences.external_metadata import csv_metadata
from geovisio_cli import exception
from .conftest import FIXTURE_DIR
from geopic_tag_reader.reader import PartialGeoPicTags
from pathlib import Path


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "metadata.csv"),
)
def test_CsvMetadataHandler(datafiles):
    mtd = csv_metadata.CsvMetadataHandler(Path(datafiles / "metadata.csv"))
    assert mtd.data == {
        "e1.jpg": PartialGeoPicTags(lat=50.5151, lon=3.265, ts=1516589529.0),
        "e3.jpg": PartialGeoPicTags(lat=50.513433333, lon=3.265277778, ts=1516589649.0),
    }


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "metadata_exif.csv"),
)
def test_CsvMetadataHandler_exif(datafiles):
    mtd = csv_metadata.CsvMetadataHandler(Path(datafiles / "metadata_exif.csv"))
    assert mtd.data == {
        "e1.jpg": PartialGeoPicTags(
            lat=50.5151,
            lon=3.265,
            ts=1516589529.0,
            exif={
                "Exif.Image.Software": "MS Paint",
                "Exif.Image.Artist": "A 2 years old",
                "Xmp.xmp.Rating": "1",
            },
        ),
        "e3.jpg": PartialGeoPicTags(lat=50.513433333, lon=3.265277778, ts=1516589649.0),
    }


def test_bad_lat_CsvMetadataHandler(datafiles):
    p = datafiles / "bad_csv.csv"
    with open(p, "w") as f:
        f.write(
            r"""file,lon,lat,capture_time,field_of_view,heading
e1.jpg,3.265,lat,2018-01-22T02:52:09+00:00,,
"""
        )
    with pytest.raises(exception.CliException) as e:
        csv_metadata.CsvMetadataHandler(Path(p))
    assert (
        str(e.value)
        == "Impossible to parse latitude (could not convert string to float: 'lat')"
    )


def test_empty_file(datafiles):
    p = datafiles / "bad_csv.csv"
    with open(p, "w") as f:
        f.write(r"")
    with pytest.raises(exception.CliException) as e:
        csv_metadata.CsvMetadataHandler(Path(p))
    assert str(e.value) == "Invalid csv file: (Could not determine delimiter)"


def test_missing_column(datafiles):
    p = datafiles / "bad_csv.csv"
    with open(p, "w") as f:
        f.write(
            r"""plop,pouet
12,14
"""
        )
    with pytest.raises(exception.CliException) as e:
        csv_metadata.CsvMetadataHandler(Path(p))
    assert (
        str(e.value) == "Missing mandatory column 'file' to identify the picture's file"
    )


def test_bad_date_CsvMetadataHandler(datafiles):
    p = datafiles / "bad_csv.csv"
    with open(p, "w") as f:
        f.write(
            r"""file,lon,lat,capture_time,field_of_view,heading
e1.jpg,3.265,12,plop,,
"""
        )
    with pytest.raises(exception.CliException) as e:
        csv_metadata.CsvMetadataHandler(Path(p))
    assert (
        str(e.value)
        == "The capture_time was not recognized (should follow the RFC 3339): plop (Invalid isoformat string: 'plop')"
    )


@pytest.mark.parametrize(("delimiter"), ((","), (";"), ("\t")))
def test_tsv_delimiter(datafiles, delimiter):
    """Using a ';' should also be a valid delmiter"""
    p = datafiles / "bad_csv.csv"
    with open(p, "w") as f:
        r = r"""file;lon;lat;capture_time;field_of_view;heading
e1.jpg;3.265;50.5151;2018-01-22T02:52:09+00:00;;
e3.jpg;3.265277778;50.513433333;2018-01-22T02:54:09+00:00;360;15
""".replace(
            ";", delimiter
        )
        f.write(r)
    mtd = csv_metadata.CsvMetadataHandler(Path(p))
    assert mtd.data == {
        "e1.jpg": PartialGeoPicTags(lat=50.5151, lon=3.265, ts=1516589529.0),
        "e3.jpg": PartialGeoPicTags(lat=50.513433333, lon=3.265277778, ts=1516589649.0),
    }
