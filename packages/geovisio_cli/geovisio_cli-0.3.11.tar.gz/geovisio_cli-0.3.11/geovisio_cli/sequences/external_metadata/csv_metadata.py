from __future__ import annotations
from geovisio_cli.sequences import external_metadata
from geovisio_cli.sequences.external_metadata import utils
from geovisio_cli.exception import CliException
from pathlib import Path
import csv
from geopic_tag_reader import reader
from typing import Dict, Optional, Tuple


def check(reader: csv.DictReader):
    if not reader.fieldnames or "file" not in reader.fieldnames:
        raise CliException(
            "Missing mandatory column 'file' to identify the picture's file"
        )


class CsvMetadataHandler(external_metadata.MetadataHandler):
    def __init__(self, file_name: Path) -> None:
        super().__init__()
        self.data = self._parse_file(file_name)

    @staticmethod
    def new_from_file(file_name: Path) -> Optional[CsvMetadataHandler]:
        if file_name.suffix != ".csv":
            return None

        return CsvMetadataHandler(file_name)

    def _parse_file(self, file_name: Path) -> Dict[str, reader.PartialGeoPicTags]:
        data = {}
        with open(file_name, "r") as f:
            # use Sniffer to detect the dialect of the file (separator, ...)
            try:
                dialect = csv.Sniffer().sniff(f.read(1024))
            except Exception as e:
                raise CliException(f"Invalid csv file: ({e})")

            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
            check(reader)

            for row in reader:
                val = self.row_to_tag(row)
                if val:
                    pic_name, tag = val
                    data[pic_name] = tag

        return data

    def row_to_tag(self, row) -> Optional[Tuple[str, reader.PartialGeoPicTags]]:
        pic_name = row["file"]

        tags = reader.PartialGeoPicTags()

        tags.lat = utils.check_lat(row.get("lat"))
        tags.lon = utils.check_lon(row.get("lon"))
        tags.ts = utils.parse_capture_time(row.get("capture_time"))

        # Look for Exif/XMP columns
        tags.exif = {}
        for k in row:
            if k.startswith("Exif.") or k.startswith("Xmp."):
                v = row[k]
                if v is not None and len(v.strip()) > 0:
                    tags.exif[k] = row[k]

        return pic_name, tags

    def get(self, file_path: Path) -> Optional[reader.PartialGeoPicTags]:
        file_name = str(file_path.name)

        return self.data.get(str(file_name))
