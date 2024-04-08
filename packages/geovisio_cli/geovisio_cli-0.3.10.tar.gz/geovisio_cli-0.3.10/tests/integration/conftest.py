import pytest
import os
from geovisio_cli.model import Geovisio
import requests


@pytest.fixture(scope="session")
def geovisio(pytestconfig):
    """
    If --external-geovisio-url has been given to pytest use an already running geovisio, else spawn a fully configured geovisio for integration tests
    """
    external_geovisio_url = pytestconfig.getoption("--external-geovisio-url")
    if external_geovisio_url:
        yield Geovisio(url=external_geovisio_url)
        return

    from testcontainers import compose

    dco_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "docker-compose-geovisio.yml",
    )
    with compose.DockerCompose(
        ".",
        compose_file_name=dco_file,
        pull=True,
    ) as compose:
        port = compose.get_service_port("geovisio-api", 5000)
        api_url = f"http://api.geovisio.localtest.me:{port}"
        compose.wait_for(api_url)

        yield Geovisio(url=api_url)
        stdout, stderr = compose.get_logs()
        if stderr:
            print("Errors\n:{}".format(stderr))


@pytest.fixture(scope="session")
def user_credential():
    """Credential of a fake created account on keycloak"""
    return ("elysee", "my password")


@pytest.fixture(scope="session")
def geovisio_with_token(geovisio, user_credential):
    token = _get_token(geovisio, user_credential)
    return Geovisio(
        url=geovisio.url,
        token=token,
    )


def _get_token(geovisio, user_credential):
    with requests.session() as s:
        _login(s, geovisio, user_credential)
        tokens = s.get(f"{geovisio.url}/api/users/me/tokens")
        tokens.raise_for_status()
        token_link = next(
            t["href"] for t in tokens.json()[0]["links"] if t["rel"] == "self"
        )
        assert token_link
        jwt_token = s.get(token_link)
        jwt_token.raise_for_status()
        return jwt_token.json()["jwt_token"]


def _login(session, geovisio, user_credential):
    login = session.get(f"{geovisio.url}/api/auth/login")

    url = _get_keycloak_authenticate_form_url(login)

    r = session.post(
        url,
        data={"username": user_credential[0], "password": user_credential[1]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=True,
    )

    # a bit hacky, but since for the moment we only submit a form to keycloak, to know if the login was successful,
    # we need to check that we were redirected to geovisio
    r.raise_for_status()
    assert r.history != 0


def _get_keycloak_authenticate_form_url(response):
    """Little hack to parse keycloak HTML to get the url to the authenticate form"""
    import re

    url = re.search('action="(.*login-actions/authenticate[^"]*)"', response.text)

    assert url, f"impossible to find form action in keycloak response: {response.text}"
    url = url.group(1).replace("&amp;", "&")
    return url


@pytest.fixture(scope="function", autouse=True)
def override_config_home(tmp_path):
    """Set XDG_CONFIG_HOME to temporary directory, so tests newer write a real user config file"""
    old_var = os.environ.get("XDG_CONFIG_HOME")

    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    yield

    if old_var:
        os.environ["XDG_CONFIG_HOME"] = old_var
    else:
        del os.environ["XDG_CONFIG_HOME"]
