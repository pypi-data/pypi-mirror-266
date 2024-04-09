from geovisio_cli import utils
import geovisio_cli
import pytest
import requests


@pytest.mark.parametrize(
    ("local_version", "pypi_version", "up_to_date"),
    (
        ("0.1.0", "0.2.0", False),
        ("0.2.0", "0.2.1", False),
        ("0.2.0", "0.2.0", True),
        ("0.3.0", "0.2.0", True),
        ("1.0.0", "0.2.0", True),
    ),
)
def test_check_if_lastest_version(
    requests_mock, local_version, pypi_version, up_to_date
):
    sub_pypi_response = {"info": {"version": pypi_version}}
    geovisio_cli.__version__ = local_version
    requests_mock.get("https://pypi.org/pypi/geovisio_cli/json", json=sub_pypi_response)
    assert utils.check_if_lastest_version() == up_to_date


def test_check_if_lastest_version_skipped(requests_mock):
    requests_mock.get(
        "https://pypi.org/pypi/geovisio_cli/json",
        exc=requests.exceptions.ConnectTimeout,
    )
    assert True
