import pytest
import os
from geovisio_cli import exception, model
import geovisio_cli.sequences.process.standard
import geovisio_cli.sequences.upload
from .conftest import FIXTURE_DIR, MOCK_API_URL
from pathlib import Path
import tomli  # type: ignore
import tomli_w  # type: ignore
import requests
from geopic_tag_reader.reader import PartialGeoPicTags


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "invalid_pic.jpg"),
)
def test_upload_with_no_valid_file(datafiles):
    with pytest.raises(exception.CliException) as e:
        seq = geovisio_cli.sequences.process.standard._read_sequences(Path(datafiles))

    assert e.match("All read pictures have invalid metadata")


def mock_api_post_collection_fail(requests_mock):
    requests_mock.post(
        MOCK_API_URL + "/api/collections",
        exc=requests.exceptions.ConnectTimeout,
    )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_collection_create_failure(requests_mock, datafiles):
    mock_api_post_collection_fail(requests_mock)

    with pytest.raises(exception.CliException) as e:
        geovisio_cli.sequences.upload.upload(
            path=datafiles,
            geovisio=model.Geovisio(url=MOCK_API_URL),
            title="Test",
            alreadyBlurred=True,
            pictureUploadTimeout=20,
        )

    assert str(e.value).startswith("Error while connecting to the API")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_upload_with_invalid_file(requests_mock, datafiles):
    # Put apart third picture
    os.rename(datafiles + "/e2.jpg", datafiles + "/e2.bak")
    os.rename(datafiles + "/e3.jpg", datafiles + "/e3.bak")

    # Mock collection creation
    gvsMock = model.Geovisio(url=MOCK_API_URL)
    seqId = "123456789"
    picId1 = "123"
    picId2 = "456"
    picId3 = "789"
    requests_mock.get(f"{MOCK_API_URL}/api", json={})
    requests_mock.get(f"{MOCK_API_URL}/api/configuration", json={})
    requests_mock.get(
        f"{MOCK_API_URL}/api/collections/{seqId}",
        json={"id": seqId, "title": "whatever"},
    )
    requests_mock.post(
        f"{MOCK_API_URL}/api/collections",
        json={"id": seqId},
        headers={"Location": f"{MOCK_API_URL}/api/collections/{seqId}"},
    )
    requests_mock.post(
        f"{MOCK_API_URL}/api/collections/{seqId}/items",
        json={"type": "Feature", "id": picId1},
        headers={"Location": f"{MOCK_API_URL}/api/collections/{seqId}/items/{picId1}"},
    )
    uploadReports = geovisio_cli.sequences.upload.upload(
        path=Path(datafiles), geovisio=gvsMock, title=None, pictureUploadTimeout=20
    )

    # Check previous pictures are OK
    assert len(uploadReports) == 1
    uploadReport = uploadReports[0]
    assert len(uploadReport.uploaded_pictures) == 1
    assert len(uploadReport.errors) == 0

    # Make other pictures available
    os.rename(datafiles + "/e2.bak", datafiles + "/e2.jpg")
    os.rename(datafiles + "/e3.bak", datafiles + "/e3.jpg")
    with open(datafiles + "/_geovisio.toml", "rb") as f:
        seq = tomli.load(f)
        seq["1"]["pictures"]["e2.jpg"] = {
            "path": str(datafiles) + "/e2.jpg",
            "position": 2,
        }
        seq["1"]["pictures"]["e3.jpg"] = {
            "path": str(datafiles) + "/e3.jpg",
            "position": 3,
        }
        f.close()

    with open(datafiles + "/_geovisio.toml", "wb") as f2:
        tomli_w.dump(seq, f2)
        f2.close()

        # Mock item call to fail
        requests_mock.post(
            f"{MOCK_API_URL}/api/collections/{seqId}/items",
            [
                {
                    "json": {"type": "Feature", "id": picId2},
                    "status_code": 202,
                    "headers": {
                        "Location": f"{MOCK_API_URL}/api/collections/{seqId}/items/{picId2}"
                    },
                },
                {"status_code": 500},
            ],
        )
        uploadReports2 = geovisio_cli.sequences.upload.upload(
            path=Path(datafiles), geovisio=gvsMock, title=None, pictureUploadTimeout=20
        )

        assert len(uploadReports2) == 1
        uploadReport2 = uploadReports2[0]
        assert len(uploadReport2.uploaded_pictures) == 1
        assert len(uploadReport2.errors) == 1


@pytest.mark.parametrize(
    ("picture", "result"),
    (
        (model.Picture(overridden_metadata=None), {}),
        (
            model.Picture(overridden_metadata=PartialGeoPicTags()),
            {},
        ),
        (
            model.Picture(
                overridden_metadata=PartialGeoPicTags(lon=42, model="MAKE")
            ),  # api does not handle overriding model for the moment so it's not in the end result
            {"override_longitude": 42},
        ),
        (
            model.Picture(
                overridden_metadata=PartialGeoPicTags(lat=12, type="flat", ts=424242)
            ),  # api does not handle overriding type for the moment so it's not in the end result
            {
                "override_latitude": 12,
                "override_capture_time": "1970-01-05T21:50:42+00:00",
            },
        ),
        (
            model.Picture(
                overridden_metadata=PartialGeoPicTags(
                    exif={"Exif.Image.Software": "Hugin", "Xmp.xmp.Rating": "5"}
                )
            ),
            {"override_Exif.Image.Software": "Hugin", "override_Xmp.xmp.Rating": "5"},
        ),
    ),
)
def test_get_overriden_metadata(picture, result):
    assert geovisio_cli.sequences.upload._get_overriden_metadata(picture) == result
