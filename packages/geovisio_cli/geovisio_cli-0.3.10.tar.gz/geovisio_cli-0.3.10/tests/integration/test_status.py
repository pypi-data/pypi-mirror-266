import geovisio_cli.model
import pytest
from geovisio_cli.sequences import status
from geovisio_cli import exception
import requests


def test_status_on_unknown_collection(geovisio):
    with pytest.raises(exception.CliException) as e:
        with requests.session() as s:
            status.get_status(
                s,
                geovisio_cli.model.Sequence(
                    location=f"{geovisio.url}/api/collections/some_bad_id"
                ),
            )
    assert e.match(f"Sequence {geovisio.url}/api/collections/some_bad_id not found")
