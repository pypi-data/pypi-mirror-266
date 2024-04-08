from dataclasses import dataclass
from haversine import Unit, haversine  # type: ignore
from geovisio_cli import exception
from geovisio_cli.exception import CliException
from geovisio_cli.model import (
    ManySequences,
    Picture,
    Sequence,
    SortMethod,
    Split,
    SEQUENCE_TOML_FILE,
    BROKEN_METADATA_STATUS,
    BROKEN_UPLOAD_STATUS,
)
from geovisio_cli.sequences import external_metadata
from geopic_tag_reader import reader
from rich import print
from rich.progress import track
import logging
import os
from pathlib import Path, PurePath
from typing import List, Optional


@dataclass
class MergeParams:
    maxDistance: Optional[float] = None
    maxRotationAngle: Optional[int] = None

    def is_merge_needed(self):
        # Only check max distance, as max rotation angle is only useful when dist is defined
        return self.maxDistance is not None


@dataclass
class SplitParams:
    maxDistance: Optional[int] = None
    maxTime: Optional[int] = None

    def is_split_needed(self):
        return self.maxDistance is not None or self.maxTime is not None


def _split_pictures_into_sequences(
    pictures: List[Picture],
    path: str,
    splitParams: Optional[SplitParams] = SplitParams(),
    title: Optional[str] = None,
    sort_method: Optional[SortMethod] = None,
) -> ManySequences:
    """Split a list of pictures into multiple lists of pictures (to create sequences)
    based on maximum distance, time and rotation between two pictures.
    Note that this function expect pictures to be sorted and have their metadata set.
    Parameters
    ----------
    pictures : Picture[]
        List of pictures to check, sorted and with metadata defined
    splitParams : SplitParams
        The parameters to define deltas between two pictures
    title : str
        Title to set on resulting sequences
    path : str
        Folder to set on resulting sequences
    sort_method : SortMethod
        Sort method to set on resulting sequences
    Returns
    -------
    ManySequences
        List of pictures splitted into smaller sequences
    """

    stoml = os.path.join(path, SEQUENCE_TOML_FILE)
    ms = ManySequences(toml_file=Path(stoml))

    # No split parameters given -> just return given pictures
    if splitParams is None or not splitParams.is_split_needed():
        ms.sequences = [
            Sequence(
                title=title or "",
                path=path,
                pictures=pictures,
                sort_method=sort_method,
            )
        ]
        return ms

    currentPicList: List[Picture] = []

    for pic in pictures:
        if len(currentPicList) == 0:  # No checks for 1st pic
            currentPicList.append(pic)
        else:
            lastPic = currentPicList[-1]

            # Missing metadata -> skip
            if lastPic.metadata is None or pic.metadata is None:
                currentPicList.append(pic)
                continue

            # Time delta
            timeOutOfDelta = (
                False
                if splitParams.maxTime is None
                else abs(lastPic.metadata.ts - pic.metadata.ts) > splitParams.maxTime
            )

            # Distance delta
            distance = haversine(
                (lastPic.metadata.lat, lastPic.metadata.lon),
                (pic.metadata.lat, pic.metadata.lon),
                unit=Unit.METERS,
            )
            distanceOutOfDelta = (
                False
                if splitParams.maxDistance is None
                else distance > splitParams.maxDistance
            )

            # One of deltas maxed -> create new sequence
            if timeOutOfDelta or distanceOutOfDelta:
                # Mark the reason for split
                picRangeTxt = f"between {PurePath(lastPic.path or '').stem} and {PurePath(pic.path or '').stem}"
                reason = ""
                if timeOutOfDelta:
                    reason = f"Too much time {picRangeTxt} ({round(abs(lastPic.metadata.ts - pic.metadata.ts))} seconds)"
                elif distanceOutOfDelta:
                    reason = (
                        f"Too much distance {picRangeTxt} ({round(distance)} meters)"
                    )

                ms.splits.append(Split(lastPic, pic, reason))
                ms.sequences.append(
                    Sequence(
                        title=title or "",
                        path=path,
                        pictures=currentPicList,
                        sort_method=sort_method,
                    )
                )
                currentPicList = [pic]

            # Otherwise, still in same sequence
            else:
                currentPicList.append(pic)

    ms.sequences.append(
        Sequence(
            title=title or "",
            path=path,
            pictures=currentPicList,
            sort_method=sort_method,
        )
    )

    return ms


def _sort_files(
    pictures: List[Picture], method: Optional[SortMethod] = SortMethod.time_asc
) -> List[Picture]:
    """Sorts pictures according to their file name
    Parameters
    ----------
    pictures : Picture[]
        List of pictures to sort
    method : SortMethod
        Sort logic to adopt (time-asc, time-desc, filename-asc, filename-desc)
    Returns
    -------
    Picture[]
        List of pictures, sorted
    """

    if method is None:
        method = SortMethod.time_asc

    if method not in [item.value for item in SortMethod]:
        raise exception.CliException("Invalid sort strategy: " + str(method))

    # Get the sort logic
    strat, order = method.split("-")

    # Sort based on filename
    if strat == "filename":
        # Check if pictures can be sorted by numeric notation
        hasNonNumber = False
        for p in pictures:
            try:
                int(PurePath(p.path or "").stem)
            except:
                hasNonNumber = True
                break

        def sort_fct(p):
            return (
                PurePath(p.path or "").stem
                if hasNonNumber
                else int(PurePath(p.path or "").stem)
            )

        pictures.sort(key=sort_fct)

    # Sort based on picture ts
    elif strat == "time":
        pictures.sort(key=lambda p: p.metadata.ts if p.metadata is not None else 0)

    if order == "desc":
        pictures.reverse()

    return pictures


def _search_for_pictures(path: Path):
    """
    Collect all the pictures in a directory
    """
    files = []
    for f in path.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in [".jpg", ".jpeg"]:
            continue
        files.append(f)
    return files


def _load_pictures(
    picture_files: List[Path],
    metadata_handler: Optional[external_metadata.MetadataHandler],
) -> List[Picture]:
    """Read a list of pictures and their associated metadata from a list of files."""
    pictures = []
    for f in track(picture_files, description="🔍 Listing pictures..."):
        picture = Picture(path=str(f))

        if metadata_handler:
            picture.overridden_metadata = metadata_handler.get(f)
        try:
            with open(str(f), "rb") as img:
                meta = reader.readPictureMetadata(img.read())
                picture.metadata = meta

        except reader.PartialExifException as e:
            # override picture metadata with the one found in the exif tags
            # if a tag is found in both exif and external metadata, the external ones are used
            picture.update_overriden_metadata(e.tags)
            if not picture.has_mandatory_metadata():
                picture.status = BROKEN_METADATA_STATUS

        except Exception as e:
            logging.warning(f"Picture {str(f)} has invalid metadata: {str(e)}")
            picture.status = BROKEN_METADATA_STATUS

        pictures.append(picture)

    return pictures


def _read_sequences(
    path: Path,
    title: Optional[str] = None,
    sortMethod: Optional[SortMethod] = None,
    splitParams: Optional[SplitParams] = None,
    mergeParams: Optional[MergeParams] = None,
) -> ManySequences:
    if not path.is_dir():
        raise CliException(f"{path} is not a directory, cannot read pictures")

    if title is None:
        title = path.name

    sequences = None
    stoml = os.path.join(path, SEQUENCE_TOML_FILE)

    # Check if a TOML file exists, then use it instead of generating one
    if os.path.isfile(stoml):
        try:
            sequences = ManySequences.read_from_file(Path(stoml))
            print(f"📄 Using metadata from existing config file: {stoml}")

            # Check sort method
            if sortMethod is not None and not sequences.has_same_sort_method(
                sortMethod
            ):
                raise CliException(
                    f'Sort method passed as argument ({sortMethod.value}) is different from the one defined in your metadata file.\nYou may either change --sort-method argument from command-line, or change "sort_method" in your metadata file.'
                )
        except EOFError:
            pass

    # Create sequence from pictures files
    if sequences is None:
        # Identify pictures files
        picture_files = _search_for_pictures(path)
        metadata_handler = external_metadata.find_handler(path)

        # Read pictures metadata (with loader)
        pictures = _load_pictures(picture_files, metadata_handler)

        # Sort, split and create sequences
        pictures = _sort_files(pictures, sortMethod)
        sequences = _split_pictures_into_sequences(
            pictures, str(path), splitParams, title=title, sort_method=sortMethod
        )

        # Look for duplicates
        if mergeParams is not None and mergeParams.is_merge_needed():
            for s in sequences.sequences:
                s.find_duplicates(mergeParams.maxDistance, mergeParams.maxRotationAngle)

    if sequences.is_empty():
        raise CliException(
            "❌ No picture was found in given folder.\nMake sure your folder contains at least one valid JPEG file."
        )

    # Check if at least one picture is valid
    if not sequences.has_valid_pictures():
        raise CliException(
            "❌ All read pictures have invalid metadata.\nPlease check if your pictures are geolocated and have a date defined.\nFor more information: https://gitlab.com/geovisio/api/-/blob/develop/docs/15_Pictures_requirements.md"
        )

    return sequences


def process(
    path: Path,
    title: Optional[str],
    sortMethod: Optional[SortMethod] = None,
    splitParams: Optional[SplitParams] = None,
    mergeParams: Optional[MergeParams] = None,
) -> ManySequences:
    ms = _read_sequences(path, title, sortMethod, splitParams, mergeParams)
    ms.persist()

    if (
        splitParams is not None
        and splitParams.is_split_needed()
        and len(ms.sequences) > 1
    ):
        print(f"\n🗂️  Pictures are split into {len(ms.sequences)} sequences")
        for i in range(len(ms.splits)):
            if i == 0:
                d = (
                    ""
                    if ms.sequences[0].nb_duplicates() == 0
                    else f" including {ms.sequences[0].nb_duplicates()} duplicates"
                )
                print(f"  Sequence 1 ({len(ms.sequences[0].pictures)} pictures{d})")
            print(f"    ✂️ {ms.splits[i].reason}")
            d = (
                ""
                if ms.sequences[i + 1].nb_duplicates() == 0
                else f" including {ms.sequences[i+1].nb_duplicates()} duplicates"
            )
            print(f"  Sequence {i+2} ({len(ms.sequences[i+1].pictures)} pictures{d})")
    else:
        d = (
            ""
            if ms.sequences[0].nb_duplicates() == 0
            else f" including {ms.sequences[0].nb_duplicates()} duplicates"
        )
        print(
            f"\n🗂️  All pictures belong to a single sequence ({len(ms.sequences[0].pictures)} pictures{d})"
        )

    return ms
