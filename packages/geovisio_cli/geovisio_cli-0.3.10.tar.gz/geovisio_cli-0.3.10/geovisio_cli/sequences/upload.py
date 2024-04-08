from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import requests
from rich import print
from rich.console import Group
from rich.live import Live
from rich.markup import escape
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from geovisio_cli import utils
from geovisio_cli.auth import login
from geovisio_cli.exception import CliException, raise_for_status
from geovisio_cli.model import (
    Geovisio,
    ManySequences,
    Picture,
    SortMethod,
    BROKEN_UPLOAD_STATUS,
    DUPLICATE_STATUS,
)
from geovisio_cli.sequences.process.standard import SplitParams, MergeParams, process
from geovisio_cli.sequences.status import get_status, info, wait_for_sequence


@dataclass
class UploadError:
    position: int
    picture_path: str
    error: Union[str, dict]
    status_code: int


@dataclass
class UploadReport:
    location: str
    uploaded_pictures: List[Picture] = field(default_factory=lambda: [])
    skipped_pictures: List[Picture] = field(default_factory=lambda: [])
    errors: List[UploadError] = field(default_factory=lambda: [])


def _get_overriden_metadata(picture: Picture):
    """
    Convert the overriden metadata into geovisio API parameters
    """
    from datetime import datetime, timezone

    res: Dict[str, Any] = {}
    m = picture.overridden_metadata
    if m is None:
        return res

    if m.lon is not None:
        res["override_longitude"] = m.lon
    if m.lat is not None:
        res["override_latitude"] = m.lat
    if m.ts is not None:
        # date are send as iso 3339 formated datetime (like '2017-07-21T17:32:28Z')
        res["override_capture_time"] = datetime.fromtimestamp(
            m.ts, timezone.utc
        ).isoformat()
    if len(m.exif) > 0:
        for k in m.exif:
            res[f"override_{k}"] = m.exif[k]

    return res


def _publish(
    session: requests.Session,
    sequences: ManySequences,
    sequenceId: int,
    geovisio: Geovisio,
    wait: bool,
    alreadyBlurred: bool,
    pictureUploadTimeout: float,
) -> UploadReport:
    sequence = sequences.sequences[sequenceId]

    # Read sequence data
    if sequence.id:
        sequence = info(session, sequence)
        print(
            f'📡 Resuming upload of sequence "{sequence.title}" (part {sequenceId+1}/{len(sequences.sequences)})'
        )
        print(f"  - Folder: {sequence.path}")
        print(f"  - API ID: {sequence.id}")
    else:
        print(
            f'📡 Uploading sequence "{sequence.title}" (part {sequenceId+1}/{len(sequences.sequences)})'
        )
        print(f"  - Folder: {sequence.path}")

    data = {}
    if sequence.title:
        data["title"] = sequence.title

    # List pictures to upload
    picturesToUpload: Dict[int, Picture] = {}
    picturesSkipped: List[Picture] = []
    for i, p in enumerate(sequence.pictures, start=1):
        if p.status == DUPLICATE_STATUS:
            picturesSkipped.append(p)
        elif p.id is None or p.status == BROKEN_UPLOAD_STATUS:
            picturesToUpload[i] = p

    # Create sequence on initial publishing
    if not sequence.id:
        seq = session.post(
            f"{geovisio.url}/api/collections", data=data, timeout=utils.REQUESTS_TIMEOUT
        )
        raise_for_status(seq, "Impossible to query GeoVisio")

        sequence.id = seq.json()["id"]
        sequence.location = seq.headers["Location"]
        sequences.persist()

        print(f"\n  ✅ Created collection {sequence.location}")

    else:
        if len(picturesToUpload) == 0:
            print(
                f"\n  ✅ Everything ({len(sequence.pictures)} picture{'s' if len(sequence.pictures) != 1 else ''}) have already been uploaded, nothing to do"
            )
            assert sequence.location
            return UploadReport(
                location=sequence.location, skipped_pictures=picturesSkipped
            )
        print(
            f"\n  ⏭️ Skipping {len(sequence.pictures) - len(picturesToUpload)} already published pictures"
        )

    if not sequence.location:
        raise CliException("Sequence has no API location defined")

    report = UploadReport(location=sequence.location, skipped_pictures=picturesSkipped)

    uploading_progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        TextColumn("[{task.completed}/{task.total}]"),
    )
    current_pic_progress = Progress(
        TextColumn("  📷 Processing [bold purple]{task.fields[file]}"),
        SpinnerColumn("simpleDots"),
    )
    error_progress = Progress(TextColumn("{task.description}"))

    last_error = Progress(
        TextColumn("🔎 Last error 🔎\n{task.description}"),
    )
    error_panel = Panel(Group(error_progress, last_error), title="Errors")
    uploading_task = uploading_progress.add_task(
        f"  [green]🚀 Uploading pictures...",
        total=len(picturesToUpload),
    )
    current_pic_task = current_pic_progress.add_task("", file="")
    progress_group = Group(
        uploading_progress,
        current_pic_progress,
        error_panel,
    )
    error_task = error_progress.add_task("[green]No errors")
    last_error_task = last_error.add_task("", visible=False)
    with Live(progress_group):
        for i, p in picturesToUpload.items():
            if not p.path:
                raise CliException(f"Missing path for picture {str(p)}")

            uploading_progress.advance(uploading_task)
            current_pic_progress.update(current_pic_task, file=p.path.split("/")[-1])

            post_data = {
                "position": i,
                "isBlurred": "true" if alreadyBlurred else "false",
            }
            post_data.update(_get_overriden_metadata(p))
            try:
                picture_response = session.post(
                    f"{sequence.location}/items",
                    files={"picture": open(p.path, "rb")},
                    data=post_data,
                    timeout=(utils.REQUESTS_CNX_TIMEOUT, pictureUploadTimeout),
                )
            except (requests.Timeout,) as timeout_error:
                raise CliException(
                    f"""Timeout while trying to post picture. Maybe the instance is overloaded? Please contact your instance administrator.

            [bold]Error:[/bold]
            {timeout_error}"""
                )
            except (
                requests.ConnectionError,
                requests.ConnectTimeout,
                requests.TooManyRedirects,
            ) as cnx_error:
                raise CliException(
                    f"""Impossible to reach GeoVisio while trying to post a picture, connection was lost. Please contact your instance administrator.

            [bold]Error:[/bold]
            {cnx_error}"""
                )

            # Picture at given position exists -> mark it as OK
            if picture_response.status_code == 409:
                sequence = get_status(session, sequence)
                sequences.persist()
                report.uploaded_pictures.append(p)

            elif picture_response.status_code >= 400:
                body = picture_response.text

                # Format a better text if JSON details are available
                if picture_response.headers.get("Content-Type") == "application/json":
                    bodyJson = picture_response.json()
                    body = bodyJson.get("message")
                    if "details" in bodyJson and "error" in bodyJson["details"]:
                        body += "\n" + bodyJson["details"]["error"]

                report.errors.append(
                    UploadError(
                        position=i,
                        picture_path=p.path,
                        status_code=picture_response.status_code,
                        error=body,
                    )
                )

                error_progress.update(
                    error_task,
                    description=f"[bold red]{len(report.errors)} errors",
                )
                last_error.update(last_error_task, description=body, visible=True)
                p.status = BROKEN_UPLOAD_STATUS
                sequences.persist()

            else:
                p.location = picture_response.headers["Location"]
                p.id = picture_response.json()["id"]
                p.status = None
                report.uploaded_pictures.append(p)
                sequences.persist()

    if not report.uploaded_pictures:
        print(
            f"  [red]💥 All pictures upload of sequence {sequence.title} failed! 💥[/red]"
        )
    else:
        print(
            f"  🎉 [bold green]{len(report.uploaded_pictures)}[/bold green] pictures uploaded"
        )
    if report.errors:
        print(f"  [bold red]{len(report.errors)}[/bold red] pictures not uploaded:")
        for e in report.errors:
            msg: Union[str, dict] = e.error
            if isinstance(e.error, str):
                spacing = "\n     "
                msg = escape(e.error.replace("\n", spacing))
            print(
                f" - {e.picture_path} (HTTP status [bold]{e.status_code}[/]):{spacing}{msg}"
            )

    if wait:
        wait_for_sequence(session, sequence)
    else:
        print(f"  Note: You can follow the picture processing with the command:")

        print(
            f"    [bold]geovisio collection-status --wait --location {sequence.location}"
        )
    return report


def _login_if_needed(session: requests.Session, geovisio: Geovisio) -> bool:
    # Check if API needs login
    apiConf = session.get(f"{geovisio.url}/api/configuration")
    if apiConf.json().get("auth", {}).get("enabled", False):
        logged_in = login(session, geovisio)
        if not logged_in:
            return False
    return True


def upload(
    path: Path,
    geovisio: Geovisio,
    title: Optional[str],
    pictureUploadTimeout: float,
    wait: bool = False,
    alreadyBlurred: bool = False,
    sortMethod: Optional[SortMethod] = None,
    splitParams: Optional[SplitParams] = None,
    mergeParams: Optional[MergeParams] = None,
    disableCertCheck=False,
) -> List[UploadReport]:
    # early test that the given url is correct
    with utils.createSessionWithRetry() as s:
        if disableCertCheck:
            s.verify = False
        utils.test_geovisio_url(s, geovisio.url)
        # early test login
        if not _login_if_needed(s, geovisio):
            raise CliException(
                "🔁 Computer not authenticated yet, impossible to upload pictures, but you can try again the same upload command after finalizing the login"
            )

        ms = process(path, title, sortMethod, splitParams, mergeParams)
        res = []
        for i in range(len(ms.sequences)):
            print("")  # Do not remove, gives a bit of spacing in output
            res.append(
                _publish(
                    session=s,
                    sequences=ms,
                    sequenceId=i,
                    geovisio=geovisio,
                    wait=wait,
                    alreadyBlurred=alreadyBlurred,
                    pictureUploadTimeout=pictureUploadTimeout,
                )
            )

        return res
