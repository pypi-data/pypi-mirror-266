import pytest
import os
from geovisio_cli import exception, model
import geovisio_cli.sequences.process.standard
import geovisio_cli.sequences.upload
from .conftest import FIXTURE_DIR
from pathlib import Path
from geopic_tag_reader import reader


def test_SplitParams_is_split_needed():
    sp = geovisio_cli.sequences.process.standard.SplitParams()
    assert not sp.is_split_needed()
    sp = geovisio_cli.sequences.process.standard.SplitParams(maxDistance=1)
    assert sp.is_split_needed()
    sp = geovisio_cli.sequences.process.standard.SplitParams(maxTime=1)
    assert sp.is_split_needed()
    sp = geovisio_cli.sequences.process.standard.SplitParams(maxDistance=1, maxTime=1)
    assert sp.is_split_needed()


@pytest.mark.parametrize(
    ("data", "method", "expected"),
    (
        (["1.jpg", "2.jpg", "3.jpg"], "filename-asc", ["1.jpg", "2.jpg", "3.jpg"]),
        (["3.jpg", "1.jpg", "2.jpg"], "filename-asc", ["1.jpg", "2.jpg", "3.jpg"]),
        (["3.jpg", "1.jpg", "2.jpeg"], "filename-asc", ["1.jpg", "2.jpeg", "3.jpg"]),
        (["10.jpg", "5.jpg", "1.jpg"], "filename-asc", ["1.jpg", "5.jpg", "10.jpg"]),
        (["C.jpg", "A.jpg", "B.jpg"], "filename-asc", ["A.jpg", "B.jpg", "C.jpg"]),
        (
            ["CAM1_001.jpg", "CAM2_002.jpg", "CAM1_002.jpg"],
            "filename-asc",
            ["CAM1_001.jpg", "CAM1_002.jpg", "CAM2_002.jpg"],
        ),
        (["1.jpg", "2.jpg", "3.jpg"], "filename-desc", ["3.jpg", "2.jpg", "1.jpg"]),
        (["3.jpg", "1.jpg", "2.jpg"], "filename-desc", ["3.jpg", "2.jpg", "1.jpg"]),
        (["3.jpg", "1.jpg", "2.jpeg"], "filename-desc", ["3.jpg", "2.jpeg", "1.jpg"]),
        (["10.jpg", "5.jpg", "1.jpg"], "filename-desc", ["10.jpg", "5.jpg", "1.jpg"]),
        (["C.jpg", "A.jpg", "B.jpg"], "filename-desc", ["C.jpg", "B.jpg", "A.jpg"]),
        (
            ["CAM1_001.jpg", "CAM2_002.jpg", "CAM1_002.jpg"],
            "filename-desc",
            ["CAM2_002.jpg", "CAM1_002.jpg", "CAM1_001.jpg"],
        ),
    ),
)
def test_sort_files_names(data, method, expected):
    dataPictures = [model.Picture(path=p) for p in data]
    resPictures = geovisio_cli.sequences.process.standard._sort_files(
        dataPictures, method
    )
    assert expected == [pic.path for pic in resPictures]


@pytest.mark.parametrize(
    ("data", "method", "expected"),
    (
        (
            [["1.jpg", 1], ["2.jpg", 2], ["3.jpg", 3]],
            "time-asc",
            ["1.jpg", "2.jpg", "3.jpg"],
        ),
        (
            [["1.jpg", 2], ["2.jpg", 3], ["3.jpg", 1]],
            "time-asc",
            ["3.jpg", "1.jpg", "2.jpg"],
        ),
        (
            [["1.jpg", 1.01], ["2.jpg", 1.02], ["3.jpg", 1.03]],
            "time-asc",
            ["1.jpg", "2.jpg", "3.jpg"],
        ),
        (
            [["1.jpg", 1], ["2.jpg", 2], ["3.jpg", 3]],
            "time-desc",
            ["3.jpg", "2.jpg", "1.jpg"],
        ),
        (
            [["1.jpg", 2], ["2.jpg", 3], ["3.jpg", 1]],
            "time-desc",
            ["2.jpg", "1.jpg", "3.jpg"],
        ),
        (
            [["1.jpg", 1.01], ["2.jpg", 1.02], ["3.jpg", 1.03]],
            "time-desc",
            ["3.jpg", "2.jpg", "1.jpg"],
        ),
    ),
)
def test_sort_files_time(data, method, expected):
    dataPictures = []
    for p in data:
        name, ts = p
        m = reader.GeoPicTags(
            lon=47.7,
            lat=-1.78,
            ts=ts,
            heading=0,
            type="flat",
            make="Panoramax",
            model="180++",
            focal_length=4,
            crop=None,
        )
        dataPictures.append(model.Picture(path=name, metadata=m))

    resPictures = geovisio_cli.sequences.process.standard._sort_files(
        dataPictures, method
    )
    assert expected == [pic.path for pic in resPictures]


@pytest.mark.parametrize(
    ("pics", "maxTime", "maxDist"),
    (
        [  # Single sequence
            [
                {
                    "lat": 48.0000001,
                    "lon": -1.7800001,
                    "ts": 1,
                    "heading": 100,
                    "seq": 0,
                },
                {
                    "lat": 48.0000002,
                    "lon": -1.7800002,
                    "ts": 2,
                    "heading": 100,
                    "seq": 0,
                },
            ],
            None,
            None,
        ],
        [  # Time excedeed
            [
                {
                    "lat": 48.0000001,
                    "lon": -1.7800001,
                    "ts": 1,
                    "heading": 100,
                    "seq": 0,
                },
                {
                    "lat": 48.0000002,
                    "lon": -1.7800002,
                    "ts": 500,
                    "heading": 100,
                    "seq": 1,
                },
            ],
            10,
            None,
        ],
        [  # Time excedeed, reverse
            [
                {
                    "lat": 48.0000001,
                    "lon": -1.7800001,
                    "ts": 500,
                    "heading": 100,
                    "seq": 0,
                },
                {
                    "lat": 48.0000002,
                    "lon": -1.7800002,
                    "ts": 1,
                    "heading": 100,
                    "seq": 1,
                },
            ],
            10,
            None,
        ],
        [  # Distance excedeed
            [
                {
                    "lat": 48.0000001,
                    "lon": -1.7800001,
                    "ts": 1,
                    "heading": 100,
                    "seq": 0,
                },
                {
                    "lat": 48.1000000,
                    "lon": -1.7800002,
                    "ts": 2,
                    "heading": 100,
                    "seq": 1,
                },
            ],
            None,
            1,
        ],
        [  # Many sequences
            [
                {
                    "lat": 48.0000001,
                    "lon": -1.7800001,
                    "ts": 1,
                    "heading": 100,
                    "seq": 0,
                },
                {
                    "lat": 48.0000002,
                    "lon": -1.7800002,
                    "ts": 2,
                    "heading": 100,
                    "seq": 0,
                },
                {
                    "lat": 48.0000003,
                    "lon": -1.7800003,
                    "ts": 3,
                    "heading": 100,
                    "seq": 0,
                },
                # Distance excedeed
                {
                    "lat": 48.1000000,
                    "lon": -1.7800001,
                    "ts": 4,
                    "heading": 100,
                    "seq": 1,
                },
                {
                    "lat": 48.1000001,
                    "lon": -1.7800001,
                    "ts": 5,
                    "heading": 100,
                    "seq": 1,
                },
                {
                    "lat": 48.1000002,
                    "lon": -1.7800001,
                    "ts": 6,
                    "heading": 100,
                    "seq": 1,
                },
                # Time excedeed
                {
                    "lat": 48.1000003,
                    "lon": -1.7800001,
                    "ts": 100,
                    "heading": 100,
                    "seq": 2,
                },
                {
                    "lat": 48.1000004,
                    "lon": -1.7800001,
                    "ts": 101,
                    "heading": 100,
                    "seq": 2,
                },
                {
                    "lat": 48.1000005,
                    "lon": -1.7800001,
                    "ts": 102,
                    "heading": 100,
                    "seq": 2,
                },
            ],
            30,
            100,
        ],
    ),
)
def test_split_pictures_into_sequences(pics, maxTime, maxDist):
    sp = geovisio_cli.sequences.process.standard.SplitParams(
        maxDistance=maxDist, maxTime=maxTime
    )
    inputPics = []
    expectedPics = [[]]

    for id, pic in enumerate(pics):
        inputPics.append(
            model.Picture(
                id=f"{id}",
                metadata=reader.GeoPicTags(
                    lat=pic["lat"],
                    lon=pic["lon"],
                    ts=pic["ts"],
                    heading=pic["heading"],
                    type="equirectangular",
                    make=None,
                    model=None,
                    focal_length=None,
                    crop=None,
                ),
            )
        )

        if len(expectedPics) - 1 < pic["seq"]:
            expectedPics.append([])
        expectedPics[pic["seq"]].append(f"{id}")

    res = geovisio_cli.sequences.process.standard._split_pictures_into_sequences(
        inputPics, "some_file.toml", sp
    )
    print("Got     ", [[p.id for p in r.pictures] for r in res.sequences])
    print("Expected", expectedPics)
    assert len(res.sequences) == len(expectedPics)

    for i, resSubSeq in enumerate(res.sequences):
        print("Checking sequence", i)
        assert len(resSubSeq.pictures) == len(expectedPics[i])
        for j, resSubSeqPic in enumerate(resSubSeq.pictures):
            print(" -> Checking pic", j)
            assert resSubSeqPic.id == expectedPics[i][j]


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
)
def test_read_sequences(datafiles):
    # First read : position is based on picture names
    seqs = geovisio_cli.sequences.process.standard._read_sequences(Path(datafiles))
    seqsTomlPath = os.path.join(datafiles, model.SEQUENCE_TOML_FILE)
    seqs.persist()

    assert os.path.isfile(seqsTomlPath)

    # Edit TOML file : position is inverted
    with open(seqsTomlPath, "r+") as seqsToml:
        editedSeqsToml = seqsToml.read()
        editedSeqsToml = (
            editedSeqsToml.replace("position = 1", "position = A")
            .replace("position = 2", "position = 1")
            .replace("position = A", "position = 2")
        )
        seqsToml.seek(0)
        seqsToml.write(editedSeqsToml)
        seqsToml.close()

        # Read sequence 2 : position should match edited TOML
        seqs = geovisio_cli.sequences.process.standard._read_sequences(Path(datafiles))
        seq = seqs.sequences[0]
        assert seq.pictures[0].path.endswith("e2.jpg")
        assert seq.pictures[1].path.endswith("e1.jpg")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "invalid_pic.jpg"),
)
def test_read_sequences_invalid_file(datafiles):
    # Read sequence from files
    seqs = geovisio_cli.sequences.process.standard._read_sequences(Path(datafiles))
    seqs.persist()

    # Check if invalid_pic is marked as broken
    seq2 = model.ManySequences.read_from_file(seqs.toml_file).sequences[0]
    assert len(seq2.pictures) == 4
    assert seq2.pictures[0].status == "broken-metadata"
    assert seq2.pictures[1].status is None
    assert seq2.pictures[2].status is None
    assert seq2.pictures[3].status is None


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
)
def test_read_sequences_sort_method_changed_set2unset(datafiles):
    # Write toml with sort method defined
    seq = geovisio_cli.sequences.process.standard._read_sequences(
        Path(datafiles), sortMethod=model.SortMethod.time_desc
    )
    seqTomlPath = os.path.join(datafiles, model.SEQUENCE_TOML_FILE)
    seq.persist()

    # Read sequence from toml without sort method = should reuse read one
    seq = geovisio_cli.sequences.process.standard._read_sequences(Path(datafiles))
    assert seq.sequences[0].pictures[0].path.endswith("e2.jpg")
    assert seq.sequences[0].pictures[1].path.endswith("e1.jpg")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
)
def test_read_sequences_sort_method_changed_different(datafiles):
    # Write toml with sort method defined
    seq = geovisio_cli.sequences.process.standard._read_sequences(
        Path(datafiles), sortMethod=model.SortMethod.time_desc
    )
    seqTomlPath = os.path.join(datafiles, model.SEQUENCE_TOML_FILE)
    seq.persist()

    # Read sequence from toml without sort method = should reuse read one
    with pytest.raises(exception.CliException) as e:
        seq = geovisio_cli.sequences.process.standard._read_sequences(
            Path(datafiles), sortMethod=model.SortMethod.filename_asc
        )

    assert e.match("Sort method passed as argument")
