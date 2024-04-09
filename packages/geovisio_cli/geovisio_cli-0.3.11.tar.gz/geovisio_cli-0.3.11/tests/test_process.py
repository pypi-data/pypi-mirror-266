import pytest
import os
import shutil
from geovisio_cli.sequences.process import standard
from .conftest import FIXTURE_DIR
from pathlib import Path, PurePath
from geovisio_cli.sequences.external_metadata import MetadataHandler
from geovisio_cli.model import DUPLICATE_STATUS
from geopic_tag_reader.reader import PartialGeoPicTags


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "not_a_pic.md"),
)
def test_upload_with_invalid_file(datafiles):
    ms = standard.process(path=Path(datafiles), title=None)

    assert len(ms.sequences) == 1
    s = ms.sequences[0]
    assert len(s.pictures) == 3
    assert [PurePath(p.path).stem for p in s.pictures] == ["e1", "e2", "e3"]
    assert s.title == Path(datafiles).name


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_load_pictures_without_metadata_handler(datafiles):
    files = [
        datafiles / "e1.jpg",
        datafiles / "e2.jpg",
        datafiles / "e3.jpg",
    ]
    pictures = standard._load_pictures(picture_files=files, metadata_handler=None)

    assert len(pictures) == 3

    assert pictures[0].path == str(datafiles / "e1.jpg")
    assert pictures[0].metadata
    assert pictures[0].metadata.lon == -1.6844680555555556
    assert pictures[0].metadata.lat == 48.15506638888889
    assert pictures[0].metadata.ts == 1666166194.0
    assert pictures[0].metadata.type == "flat"
    assert pictures[0].metadata.make == "SONY"
    assert pictures[0].metadata.model == "FDR-X1000V"

    assert pictures[1].path == str(datafiles / "e2.jpg")
    assert pictures[1].metadata
    assert pictures[1].metadata.lon == -1.684506388888889
    assert pictures[1].metadata.lat == 48.155071388888885
    assert pictures[1].metadata.ts == 1666166196
    assert pictures[1].metadata.type == "flat"
    assert pictures[1].metadata.make == "SONY"
    assert pictures[1].metadata.model == "FDR-X1000V"

    assert pictures[2].path == str(datafiles / "e3.jpg")
    assert pictures[2].metadata
    assert pictures[2].metadata.lon == -1.684546388888889
    assert pictures[2].metadata.lat == 48.155073055555555
    assert pictures[2].metadata.type == "flat"
    assert pictures[2].metadata.model == "FDR-X1000V"
    assert pictures[2].metadata.ts == 1666166198.0
    assert pictures[2].metadata.make == "SONY"


class SimpleMetadataHandler(MetadataHandler):
    """Helper class to emulate metadata handlers"""

    def __init__(self, metadata) -> None:
        super().__init__()
        self.metadata = metadata

    @staticmethod
    def new_from_file(_):
        pass

    def get(self, file_path):
        return self.metadata.get(file_path)


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_load_pictures_with_metadata_handler(datafiles):
    files = [
        datafiles / "e1.jpg",
        datafiles / "e2.jpg",
        datafiles / "e3.jpg",
    ]

    simple_metadata_handler = SimpleMetadataHandler(
        {
            datafiles / "e1.jpg": PartialGeoPicTags(ts=4242, make="CANON"),
            # no metadata for `e2`, should be a problem
            datafiles / "e3.jpg": PartialGeoPicTags(lon=42),
        }
    )

    pictures = standard._load_pictures(
        picture_files=files, metadata_handler=simple_metadata_handler
    )

    assert len(pictures) == 3

    assert pictures[0].path == str(datafiles / "e1.jpg")
    assert pictures[0].status is None  # None means everything is fine for the moment
    assert pictures[0].metadata
    assert pictures[0].metadata.lon == -1.6844680555555556
    assert pictures[0].metadata.lat == 48.15506638888889
    assert pictures[0].metadata.type == "flat"
    assert pictures[0].metadata.model == "FDR-X1000V"
    assert pictures[0].metadata.ts == 1666166194.0
    assert pictures[0].metadata.make == "SONY"
    assert pictures[0].overridden_metadata
    assert pictures[0].overridden_metadata.ts == 4242
    assert pictures[0].overridden_metadata.make == "CANON"

    assert pictures[1].path == str(datafiles / "e2.jpg")
    assert pictures[0].status is None  # None means everything is fine for the moment
    assert pictures[1].metadata
    assert pictures[1].metadata.lon == -1.684506388888889
    assert pictures[1].metadata.lat == 48.155071388888885
    assert pictures[1].metadata.ts == 1666166196
    assert pictures[1].metadata.type == "flat"
    assert pictures[1].metadata.make == "SONY"
    assert pictures[1].metadata.model == "FDR-X1000V"

    assert pictures[2].path == str(datafiles / "e3.jpg")
    assert pictures[0].status is None  # None means everything is fine for the moment
    assert pictures[2].metadata
    assert pictures[2].metadata.lon == -1.684546388888889
    assert pictures[2].metadata.lat == 48.155073055555555
    assert pictures[2].metadata.type == "flat"
    assert pictures[2].metadata.model == "FDR-X1000V"
    assert pictures[2].metadata.ts == 1666166198.0
    assert pictures[2].metadata.make == "SONY"
    assert pictures[2].overridden_metadata
    assert pictures[2].overridden_metadata.lon == 42


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"),
    os.path.join(FIXTURE_DIR, "e2_without_coord.jpg"),
    os.path.join(FIXTURE_DIR, "e3_without_exif.jpg"),
)
def test_load_pictures_with_metadata_handler_and_partial_exifs(datafiles):
    """
    Loading picture with partial metadata should be no problem if mandatory metadata can be found in external metada
    Here only e3_without_exif.jpg should be in error since it has no exif tags, and only `ts` defined in external metadata
    """
    files = [
        datafiles / "e1_without_exif.jpg",
        datafiles / "e2_without_coord.jpg",
        datafiles / "e3_without_exif.jpg",
    ]

    simple_metadata_handler = SimpleMetadataHandler(
        {
            datafiles
            / "e1_without_exif.jpg": PartialGeoPicTags(
                ts=4242, lon=12, lat=42, make="CANON"
            ),
            datafiles
            / "e2_without_coord.jpg": PartialGeoPicTags(lon=13, lat=43, make="CANON"),
            datafiles / "e3_without_exif.jpg": PartialGeoPicTags(ts=4243),
        }
    )

    pictures = standard._load_pictures(
        picture_files=files, metadata_handler=simple_metadata_handler
    )

    assert len(pictures) == 3

    assert pictures[0].path == str(datafiles / "e1_without_exif.jpg")
    assert pictures[0].metadata is None
    assert pictures[0].status is None  # None means everything is fine for the moment
    assert pictures[0].overridden_metadata
    assert pictures[0].overridden_metadata.ts == 4242
    assert pictures[0].overridden_metadata.lon == 12
    assert pictures[0].overridden_metadata.lat == 42
    assert pictures[0].overridden_metadata.make == "CANON"

    assert pictures[1].path == str(datafiles / "e2_without_coord.jpg")
    assert pictures[1].status is None
    assert pictures[1].metadata is None
    assert pictures[1].overridden_metadata
    # the overridden_metadata also contains exif tags
    assert pictures[1].overridden_metadata.lon == 13
    assert pictures[1].overridden_metadata.lat == 43
    assert pictures[1].overridden_metadata.ts == 1666166196
    assert pictures[1].overridden_metadata.type == "flat"
    assert (
        pictures[1].overridden_metadata.make == "CANON"
    )  # -< both define in exif and external, we use the external value
    assert pictures[1].overridden_metadata.model == "FDR-X1000V"

    assert pictures[2].path == str(datafiles / "e3_without_exif.jpg")
    assert pictures[2].status == "broken-metadata"
    assert pictures[2].overridden_metadata
    assert pictures[2].overridden_metadata.ts == 4243


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_process_with_duplicates(datafiles):
    # Create a duplicate of e1
    shutil.copyfile(datafiles / "e1.jpg", datafiles / "e0.jpg")

    # Process sequence
    sequences = standard.process(
        Path(datafiles),
        "test",
        mergeParams=standard.MergeParams(maxDistance=1, maxRotationAngle=30),
        sortMethod=standard.SortMethod.filename_asc,
    )

    # Check results (second e1 should be marked as duplicate)
    assert len(sequences.sequences) == 1
    s = sequences.sequences[0]
    assert len(s.pictures) == 4

    assert s.pictures[0].status == None
    assert s.pictures[0].path == datafiles / "e0.jpg"
    assert s.pictures[1].status == DUPLICATE_STATUS
    assert s.pictures[1].path == datafiles / "e1.jpg"
    assert s.pictures[2].status == None
    assert s.pictures[2].path == datafiles / "e2.jpg"
    assert s.pictures[3].status == None
    assert s.pictures[3].path == datafiles / "e3.jpg"
