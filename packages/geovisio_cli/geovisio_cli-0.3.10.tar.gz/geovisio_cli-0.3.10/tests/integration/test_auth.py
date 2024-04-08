from geovisio_cli.sequences import upload
from geovisio_cli import auth, exception, model
import os
import pytest
from pathlib import Path
from ..conftest import FIXTURE_DIR
from .conftest import _login
import requests


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_auth_with_token(geovisio_with_token, datafiles):
    reports = upload.upload(
        path=Path(datafiles),
        geovisio=geovisio_with_token,
        title="some title",
        pictureUploadTimeout=20,
    )

    assert len(reports) == 1
    assert len(reports[0].uploaded_pictures) == 3
    assert len(reports[0].errors) == 0


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_login(geovisio, datafiles, user_credential, tmp_path):
    assert not os.path.exists(tmp_path / "geovisio" / "config.toml")
    l = auth.create_auth_credentials(geovisio)

    # we call the auth credentials while loggin
    with requests.session() as s:
        _login(s, geovisio, user_credential)
        claim = s.get(l.get_claim_url())
        assert claim.status_code == 200
        assert (
            claim.text == "You are now logged in the CLI, you can upload your pictures"
        )

    assert os.path.exists(tmp_path / "geovisio" / "config.toml")

    # doing a geovisio upload should work without crendentials now
    uploadReports = upload.upload(
        path=Path(datafiles),
        geovisio=geovisio,
        title="some title",
        pictureUploadTimeout=20,
    )
    assert len(uploadReports) == 1
    assert len(uploadReports[0].uploaded_pictures) == 3
    assert len(uploadReports[0].errors) == 0


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_login_without_claim(geovisio, datafiles, tmp_path):
    """Login without claiming the token should result to errors for pictures upload"""
    assert not os.path.exists(tmp_path / "geovisio" / "config.toml")
    l = auth.create_auth_credentials(geovisio)

    # a config file should have been created
    assert os.path.exists(tmp_path / "geovisio" / "config.toml")

    # doing a geovisio upload should not work as the token is not usable yet
    with pytest.raises(
        exception.CliException,
        match="🔁 Computer not authenticated yet, impossible to upload pictures, but you can try again the same upload command after finalizing the login",
    ):
        upload.upload(
            path=Path(datafiles),
            geovisio=geovisio,
            title="some title",
            pictureUploadTimeout=20,
        )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_login_on_invalid_url_path(geovisio_with_token, datafiles):
    with pytest.raises(exception.CliException) as e:
        auth.create_auth_credentials(
            model.Geovisio(url=geovisio_with_token.url + "/some_additional_path")
        )
    msg = str(e.value)
    assert msg.startswith(
        f"""The API URL is not valid.

Note that your URL should be the API root (something like https://geovisio.fr, https://panoramax.ign.fr or any other geovisio instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {geovisio_with_token.url}/some_additional_path/api
[bold]Error:[/bold]"""
    )
