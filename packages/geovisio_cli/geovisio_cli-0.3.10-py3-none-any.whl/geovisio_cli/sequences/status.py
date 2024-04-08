from datetime import timedelta
from time import sleep
from typing import Optional
from rich import print
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from geovisio_cli import utils
from geovisio_cli.exception import CliException
from geovisio_cli.model import InteriorOrientation, Picture, Sequence


import requests


def get_status(session: requests.Session, sequence: Sequence) -> Sequence:
    s = session.get(
        f"{sequence.location}/geovisio_status", timeout=utils.REQUESTS_TIMEOUT
    )
    if s.status_code == 404:
        raise CliException(f"Sequence {sequence.location} not found")
    if s.status_code >= 400:
        raise CliException(
            f"Impossible to get sequence {sequence.location} status: {s.text}"
        )
    r = s.json()

    if len(sequence.pictures) == 0:
        sequence.pictures = [
            Picture(id=p["id"], status=p["status"]) for p in r["items"]
        ]
    else:
        for i, p in enumerate(r["items"]):
            sequence.pictures[i].id = p["id"]
            sequence.pictures[i].status = p["status"]

    return sequence


def info(session: requests.Session, sequence: Sequence) -> Sequence:
    if not sequence.location:
        raise CliException(f"Sequence has no location set")

    s = session.get(sequence.location, timeout=utils.REQUESTS_TIMEOUT, verify=False)
    if s.status_code == 404:
        raise CliException(f"Sequence {sequence.location} not found")
    if s.status_code >= 400:
        raise CliException(
            f"Impossible to get sequence {sequence.location} status: {s.text}"
        )
    r = s.json()
    producer = next(
        (p["name"] for p in r.get("providers", []) if "producer" in p["roles"]), None
    )
    summary = r.get("summaries", {}).get("pers:interior_orientation", [])

    sequence.id = r["id"]
    sequence.title = r["title"]
    sequence.producer = producer
    sequence.interior_orientation = [
        InteriorOrientation(
            make=s.get("make"),
            model=s.get("model"),
            field_of_view=s.get("field_of_view"),
        )
        for s in summary
    ]

    return sequence


def _print_final_sequence_status(sequence: Sequence):
    nb_broken = sequence.nb_broken()
    nb_ready = sequence.nb_ready()
    if nb_ready == 0:
        print(f"[red]💥 No picture processed")
        return
    s = f"✅ {nb_ready} pictures processed"
    if nb_broken:
        s += f"([red]{nb_broken}[/red] cannot be processed)"
    print(s)


def wait_for_sequence(
    session: requests.Session, sequence: Sequence, timeout: Optional[timedelta] = None
):
    seq_status = get_status(session, sequence)
    if seq_status.all_done():
        _print_final_sequence_status(seq_status)
        return

    print("🔭 Waiting for pictures to be processed by geovisio")
    status_progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        MofNCompleteColumn(),
        "•",
        TextColumn("{task.fields[processing]}"),
    )
    processing_task = status_progress.add_task(
        f"[green]⏳ Processing ...",
        total=1,
        processing="",
    )
    progress_group = Group(
        status_progress,
    )
    waiting_time = timedelta(seconds=2)
    elapsed = timedelta(0)

    with Live(progress_group):
        while True:
            # TODO: display some stats about those errors

            nb_preparing = seq_status.nb_preparing()
            nb_waiting = seq_status.nb_waiting()
            processing = f"{nb_preparing} picture{('s' if nb_preparing != 0 else '')} currently processed"
            status_progress.update(
                processing_task,
                total=len(seq_status.pictures),
                completed=seq_status.nb_ready(),
                processing=processing,
            )

            if nb_waiting + nb_preparing == 0:
                break

            elapsed += waiting_time
            if timeout is not None and elapsed > timeout:
                raise CliException(f"❌ Sequence not ready after {elapsed}, stoping")

            sleep(waiting_time.total_seconds())
            seq_status = get_status(session, sequence)

    _print_final_sequence_status(seq_status)


def display_sequence_status(session: requests.Session, sequence: Sequence):
    seq_status = get_status(session, sequence)
    seq_info = info(session, sequence)

    s = f"Sequence [bold]{seq_info.title}[/bold]"
    if seq_info.producer is not None:
        s += f" produced by [bold]{seq_info.producer}[/bold]"
    s += " taken with"
    for i in seq_info.interior_orientation:
        s += f" [bold]{i.make} {i.model}[/bold]"
        if i.field_of_view:
            s += f" ({i.field_of_view}°)"

    print(s)
    table = Table()

    table.add_column("Total")
    table.add_column("Ready", style="green")
    table.add_column("Waiting", style="magenta")
    table.add_column("Preparing", style="magenta")
    table.add_column("Broken", style="red")

    table.add_row(
        f"{len(seq_status.pictures)}",
        f"{seq_status.nb_ready()}",
        f"{seq_status.nb_waiting()}",
        f"{seq_status.nb_preparing()}",
        f"{seq_status.nb_broken()}",
    )
    print(table)
