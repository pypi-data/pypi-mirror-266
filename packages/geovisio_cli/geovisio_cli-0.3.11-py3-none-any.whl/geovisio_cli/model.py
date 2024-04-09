from dataclasses import dataclass, field, fields
from enum import Enum
import os
from typing import List, Optional, Dict, Any, Tuple
from geopic_tag_reader import reader
from . import utils
import tomli  # type: ignore
import tomli_w  # type: ignore
from pathlib import Path
from haversine import Unit, haversine  # type: ignore


@dataclass
class Geovisio:
    url: str
    token: Optional[str] = None


BROKEN_METADATA_STATUS = "broken-metadata"
BROKEN_UPLOAD_STATUS = "broken"
DUPLICATE_STATUS = "duplicate"


@dataclass
class Picture:
    path: Optional[str] = None
    id: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[reader.GeoPicTags] = None
    overridden_metadata: Optional[reader.PartialGeoPicTags] = None

    def toml(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "path": self.path,
            "id": self.id,
            "location": self.location,
            "status": self.status,
        }
        if self.overridden_metadata:
            d["overriden_metadata"] = {}
            for field in fields(self.overridden_metadata):
                v = getattr(self.overridden_metadata, field.name)
                if v:
                    d["overriden_metadata"][field.name] = v
        return utils.removeNoneInDict(d)

    @staticmethod
    def from_toml(data):
        overriden_metadata = None
        if data.get("overriden_metadata"):
            overriden_metadata = reader.PartialGeoPicTags(
                **data.get("overriden_metadata")
            )
        return Picture(
            path=data.get("path"),
            id=data.get("id"),
            location=data.get("location"),
            status=data.get("status"),
            overridden_metadata=overriden_metadata,
        )

    def has_mandatory_metadata(self):
        """To be valid a picture should have a coordinate and a timestamp"""
        if self.metadata is not None:
            return True
        mandatory_fields = ["lon", "lat", "ts"]
        for m in mandatory_fields:
            if getattr(self.overridden_metadata, m) is None:
                return False
        return True

    def update_overriden_metadata(self, new_metadata: reader.PartialGeoPicTags):
        """Update overriden metadata with new value only if there is no existing value"""
        if self.overridden_metadata is None:
            self.overridden_metadata = new_metadata
            return
        for field in fields(self.overridden_metadata):
            old_value = getattr(self.overridden_metadata, field.name)
            if old_value is None:
                setattr(
                    self.overridden_metadata,
                    field.name,
                    getattr(new_metadata, field.name),
                )


@dataclass
class Split:
    prevPic: Picture
    nextPic: Picture
    reason: str


@dataclass
class InteriorOrientation:
    make: str
    model: str
    field_of_view: Optional[int]


class SortMethod(str, Enum):
    filename_asc = "filename-asc"
    filename_desc = "filename-desc"
    time_asc = "time-asc"
    time_desc = "time-desc"


@dataclass
class Sequence:
    title: str = ""
    path: str = ""
    id: Optional[str] = None
    location: Optional[str] = None
    producer: Optional[str] = None
    interior_orientation: List[InteriorOrientation] = field(default_factory=lambda: [])
    pictures: List[Picture] = field(default_factory=lambda: [])
    sort_method: Optional[SortMethod] = None

    def toml(self):
        res = {
            "sequence": utils.removeNoneInDict(
                {
                    "title": self.title,
                    "path": self.path,
                    "id": self.id,
                    "location": self.location,
                    "producer": self.producer,
                    "sort_method": self.sort_method.value
                    if self.sort_method is not None
                    else None,
                }
            ),
            "pictures": {},
        }

        for pos, pic in enumerate(self.pictures, start=1):
            pict = pic.toml()
            pict["position"] = pos
            if pic.path:
                res["pictures"][os.path.basename(pic.path)] = pict

        return res

    @staticmethod
    def from_toml(data):
        s = Sequence()
        s.update_from_toml(data)
        return s

    def update_from_toml(self, data):
        if data.get("sequence"):
            self.title = data["sequence"].get("title", "")
            self.path = data["sequence"].get("path", "")
            self.id = data["sequence"].get("id")
            self.location = data["sequence"].get("location")
            self.producer = data["sequence"].get("producer")
            self.sort_method = (
                SortMethod(data["sequence"]["sort_method"])
                if "sort_method" in data["sequence"]
                else None
            )

        if data.get("pictures"):
            self.pictures = [
                Picture.from_toml(picData)
                for picId, picData in sorted(
                    data["pictures"].items(),
                    key=lambda item: int(item[1].get("position") or -1),
                )
            ]

    def find_duplicates(
        self,
        maxDistance: Optional[float] = None,
        maxRotationAngle: Optional[int] = None,
    ) -> None:
        """Mark pictures too close to each other as duplicates.

        This avoids to upload similar pictures.

        Parameters
        ----------
        maxDistance : float
            The maximum distance to consider two pictures as duplicates (in meters)
        maxRotationAngle : int
            The maximum rotation angle to consider two pictures as duplicated (in degrees)
        """

        if maxDistance is None:
            return None

        lastNonDuplicatedPicId = 0

        for i, currentPic in enumerate(self.pictures):
            if i == 0:
                continue

            prevPic = self.pictures[lastNonDuplicatedPicId]

            if prevPic.metadata is None or currentPic.metadata is None:
                continue

            # Compare distance
            dist = haversine(
                (prevPic.metadata.lat, prevPic.metadata.lon),
                (currentPic.metadata.lat, currentPic.metadata.lon),
                unit=Unit.METERS,
            )

            if maxDistance is not None and dist <= maxDistance:
                # Compare angle (if available on both images)
                if (
                    maxRotationAngle is not None
                    and prevPic.metadata.heading is not None
                    and currentPic.metadata.heading is not None
                ):
                    deltaAngle = abs(
                        currentPic.metadata.heading - prevPic.metadata.heading
                    )

                    if deltaAngle <= maxRotationAngle:
                        currentPic.status = DUPLICATE_STATUS
                    else:
                        lastNonDuplicatedPicId = i
                else:
                    currentPic.status = DUPLICATE_STATUS
            else:
                lastNonDuplicatedPicId = i

    def all_done(self):
        return self.nb_waiting() + self.nb_preparing() == 0

    def nb_ready(self):
        return sum((1 for p in self.pictures if p.status == "ready"))

    def nb_waiting(self):
        return sum((1 for p in self.pictures if p.status == "waiting-for-process"))

    def nb_duplicates(self):
        return sum((1 for p in self.pictures if p.status == DUPLICATE_STATUS))

    def nb_preparing(self):
        return sum(
            (
                1
                for p in self.pictures
                if (p.status and p.status.startswith("preparing"))
            )
        )

    def nb_broken(self):
        return sum((1 for p in self.pictures if p.status == BROKEN_UPLOAD_STATUS))


@dataclass
class ManySequences:
    """ManySequences is a single handler for multiple sequences found in a single folder."""

    toml_file: Path
    sequences: List[Sequence] = field(default_factory=lambda: [])
    splits: List[Split] = field(default_factory=lambda: [])

    def toml(self):
        res = {}
        for i, s in enumerate(self.sequences, start=1):
            res[str(i)] = s.toml()
        return res

    def has_same_sort_method(self, sortMethod):
        if sortMethod is None:
            return True
        else:
            for s in self.sequences:
                if s.sort_method != sortMethod:
                    return False
            return True

    def is_empty(self):
        if len(self.sequences) == 0:
            return True
        return not any((len(s.pictures) != 0 for s in self.sequences))

    def has_valid_pictures(self):
        for s in self.sequences:
            for p in s.pictures:
                if p.status != BROKEN_METADATA_STATUS:
                    return True
        return False

    @classmethod
    def read_from_file(cls, file: Path):
        """Read multiple sequences from a single TOML config file"""

        with open(file, "rb") as f:
            tomlContent = tomli.load(f)
            f.close()

            # Retro-compatibility with old file formats (single-sequence in file)
            if tomlContent.get("sequence") is not None:
                ms = ManySequences(
                    toml_file=file, sequences=[Sequence.from_toml(tomlContent)]
                )
            else:
                ms = ManySequences(
                    toml_file=file,
                    sequences=[
                        Sequence.from_toml(seqData) for seqData in tomlContent.values()
                    ],
                )

            return ms

    def persist(self) -> Path:
        """Writes TOML sequence metadata file"""

        with open(self.toml_file, "wb") as f:
            tomli_w.dump(self.toml(), f)
            f.close()

        return self.toml_file


SEQUENCE_TOML_FILE = "_geovisio.toml"
