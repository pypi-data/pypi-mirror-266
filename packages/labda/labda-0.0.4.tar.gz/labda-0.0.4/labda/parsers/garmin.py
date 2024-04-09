import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pandas as pd


# TODO:Fix this.
# TODO: Edit so it will return Records object.
def get_value(
    parent: ET.Element, child: str, ns: dict[str, str], name: str | None = None
) -> dict[str, Any]:
    value = parent.find(child, ns)
    name = name or child
    value = value.text if isinstance(value, ET.Element) else None

    return {name: value}


def get_atrib(
    element: ET.Element, atrib: str, name: str | None = None
) -> dict[str, Any]:
    value = element.attrib.get(atrib)
    name = name or atrib

    return {name: value}


def from_gpx(path: str | Path, vendor: str) -> pd.DataFrame:
    if isinstance(path, str):
        path = Path(path)

    tree = ET.parse(path)
    root = tree.getroot()

    match vendor:
        case "garmin":
            df = garmin_gpx(root)
        case _:
            raise ValueError(f"Unsupported vendor: {vendor}.")

    return df


def garmin_gpx(root: ET.Element) -> pd.DataFrame:
    ns = {
        "gpx": "http://www.topografix.com/GPX/1/1",
        "ext": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
    }

    points = []
    for trackpoint in root.findall(".//gpx:trkpt", ns):
        lat = get_atrib(trackpoint, "lat")
        lon = get_atrib(trackpoint, "lon")
        elevation = get_value(trackpoint, "gpx:ele", ns, "elevation")
        datetime = get_value(trackpoint, "gpx:time", ns, "datetime")

        point = {
            **datetime,
            **lat,
            **lon,
            **elevation,
        }

        extensions = trackpoint.find("gpx:extensions", ns)
        if isinstance(extensions, ET.Element):
            hr = get_value(extensions, ".//ext:hr", ns, "hr")
            cad = get_value(extensions, ".//ext:cad", ns, "cad")
            point.update(**hr, **cad)
        else:
            point["hr"] = None
            point["cad"] = None

        points.append(point)

    df = pd.DataFrame.from_records(points)
    df = df.astype(
        {
            "datetime": "datetime64[ns, UTC]",
            "lat": "Float64",
            "lon": "Float64",
            "elevation": "Float64",
            "hr": "Int64",
            "cad": "Int64",
        }  # type: ignore
    )
    df["datetime"] = df["datetime"].dt.tz_localize(None)

    return df
