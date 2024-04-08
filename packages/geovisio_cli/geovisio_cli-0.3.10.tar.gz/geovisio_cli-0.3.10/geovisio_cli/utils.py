from geovisio_cli.exception import CliException
from rich import print
import requests
from urllib3.util import Retry
import requests.adapters

REQUESTS_CNX_TIMEOUT = 15.1  # max number of seconds to wait for the connection to establish, cf https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
REQUESTS_TIMEOUT = (REQUESTS_CNX_TIMEOUT, 30)


def test_geovisio_url(session: requests.Session, geovisio: str):
    full_url = f"{geovisio}/api"
    try:
        r = session.get(full_url, timeout=REQUESTS_TIMEOUT)
    except (
        requests.Timeout,
        requests.ConnectionError,
        requests.ConnectTimeout,
        requests.TooManyRedirects,
    ) as e:
        raise CliException(
            f"""The API is not reachable. Please check error and used URL below, and retry later if the URL is correct.

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{e}"""
        )
    except Exception as e:
        raise CliException(
            f"""Error while connecting to the API. Please check error and used URL below

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{e}"""
        )

    if r.status_code == 404:
        raise CliException(
            f"""The API URL is not valid.

Note that your URL should be the API root (something like https://geovisio.fr, https://panoramax.ign.fr or any other geovisio instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{r.text}"""
        )
    if r.status_code > 404:
        raise CliException(
            f"""The API is unavailable for now. Please check given error and retry later.
[bold]Used URL:[/bold] {full_url}
[bold]Error[/bold] (code [cyan]{r.status_code}[/cyan]):
{r.text}"""
        )


def check_if_lastest_version():
    from packaging import version
    import geovisio_cli

    pypi_url = "https://pypi.org/pypi/geovisio_cli"

    try:
        response = requests.get(f"{pypi_url}/json", timeout=REQUESTS_TIMEOUT)
        latest_version = response.json()["info"]["version"]

        if version.parse(latest_version) > version.parse(geovisio_cli.__version__):
            print(
                f"⚠️ A newer geovisio_cli version {latest_version} is available on PyPI (available on {pypi_url}).\nWe highly recommend updating as this tool is still in beta version, and new versions ensure good compatibility with GeoVisio API."
            )
            return False

    except requests.exceptions.Timeout:
        print("Skip check to verify if CLI version is latest (PyPI timeout)")
    except requests.exceptions.RequestException as e:
        print(f"Skip check to verify if CLI version is latest ({e})")

    return True


def removeNoneInDict(val):
    """Removes empty values from dictionnary"""
    return {k: v for k, v in val.items() if v is not None}


def createSessionWithRetry() -> requests.Session:
    """Creates a request session with automatic retry on failure"""
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[502, 503, 504],
        allowed_methods={"GET", "POST"},
    )
    s.mount("https://", requests.adapters.HTTPAdapter(max_retries=retries))
    s.mount("http://", requests.adapters.HTTPAdapter(max_retries=retries))
    return s
