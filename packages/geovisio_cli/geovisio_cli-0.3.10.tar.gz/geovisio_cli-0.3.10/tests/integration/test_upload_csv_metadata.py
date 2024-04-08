import os
import pytest

import geovisio_cli.sequences.status
import geovisio_cli.sequences.upload
from ..conftest import FIXTURE_DIR
from pathlib import Path
import requests
from geovisio_cli import exception, model
from datetime import timedelta
from geopic_tag_reader.reader import PartialGeoPicTags
from datetime import datetime, timezone


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "metadata_exif.csv"),
)
def test_valid_csv_upload(geovisio_with_token, datafiles):
    # value stored in metadata.csv
    e1_new_lat = 50.5151
    e1_new_lon = 3.265
    e1_new_exif = {
        "Exif.Image.Software": "MS Paint",
        "Exif.Image.Artist": "A 2 years old",
        "Xmp.xmp.Rating": "1",
    }
    e3_new_lat = 50.513433333
    e3_new_lon = 3.265277778
    uploadReports = geovisio_cli.sequences.upload.upload(
        path=Path(datafiles),
        geovisio=geovisio_with_token,
        title="some title",
        pictureUploadTimeout=20,
    )
    assert len(uploadReports) == 1
    assert len(uploadReports[0].uploaded_pictures) == 3
    assert len(uploadReports[0].errors) == 0

    collection = model.Sequence(location=uploadReports[0].location)
    with requests.session() as s:
        geovisio_cli.sequences.status.wait_for_sequence(
            s, collection, timeout=timedelta(minutes=1)
        )
        status = geovisio_cli.sequences.status.get_status(s, collection)
        sequence_info = geovisio_cli.sequences.status.info(s, collection)
    # 3 pictures should have been uploaded
    assert len(status.pictures) == 3

    for i in status.pictures:
        assert i.status == "ready"

    # the collection should also have 3 items
    collection = requests.get(f"{collection.location}/items")
    collection.raise_for_status()

    features = collection.json()["features"]
    assert len(features) == 3

    assert sequence_info.title == "some title"
    assert sequence_info.interior_orientation == [
        model.InteriorOrientation(make="SONY", model="FDR-X1000V", field_of_view=None)
    ]

    # and the send pictures should have the overriden info
    assert features[0]["geometry"]["coordinates"] == [e1_new_lon, e1_new_lat]
    assert features[0]["properties"]["datetime"] == "2018-01-22T02:52:09+00:00"
    assert features[0]["properties"]["exif"]["Exif.Image.Software"] == "MS Paint"
    assert features[0]["properties"]["exif"]["Exif.Image.Artist"] == "A 2 years old"
    assert features[0]["properties"]["exif"]["Xmp.xmp.Rating"] == "1"
    assert features[2]["geometry"]["coordinates"] == [e3_new_lon, e3_new_lat]
    assert features[2]["properties"]["datetime"] == "2018-01-22T02:54:09+00:00"
