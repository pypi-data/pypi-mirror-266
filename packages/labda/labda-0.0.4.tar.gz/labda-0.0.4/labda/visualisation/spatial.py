from typing import Any, Dict, Tuple

import geopandas as gpd
import pandas as pd
import pydeck as pdk
from shapely.geometry import Point

from ..utils import convert_to_geodataframe


def get_status(row):
    if row["status"] == "stationary":
        return f"Stationary {row['stationary_id']}"
    elif row["status"] == "transport":
        return f"Trip {row['trip_id']}"
    elif row["status"] == "pause":
        return f"Trip {row['trip_id']} (Pause {row['stationary_id']})"


def get_color(row):
    if row["status"] == "stationary":
        return [255, 0, 0]
    elif row["status"] == "transport":
        return [0, 255, 0]
    elif row["status"] == "pause":
        return [50, 205, 50]


def timeline_layer(
    df: pd.DataFrame, crs: str | None = None
) -> Tuple[pdk.Layer, Dict[str, Any], Point]:
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=crs)  # type: ignore
    center = gdf.geometry.centroid.to_crs(epsg=4326).unary_union.centroid

    gdf["duration"] = gdf["duration"].astype(str)
    gdf["start"] = gdf["start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    gdf["end"] = gdf["end"].dt.strftime("%Y-%m-%d %H:%M:%S")
    gdf["distance"] = gdf["distance"].round(2)
    gdf["status_text"] = gdf.apply(get_status, axis=1)
    gdf["mode"] = gdf["mode"].cat.add_categories(["Stationary"])
    gdf["mode"] = gdf["mode"].fillna("Stationary")
    gdf["color"] = gdf.apply(get_color, axis=1)

    gdf.to_crs(epsg=4326, inplace=True)

    layer = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        get_position="geometry.coordinates",
        get_radius=10,  # Radius is in meters
        get_fill_color="color",
        get_line_color="color",
        get_line_width=7.5,
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": """<strong>Status:</strong> {status_text}<br/>
        <strong>Start:</strong> {start}<br/>
        <strong>End:</strong> {end}<br/>
        <strong>Duration:</strong> {duration}<br/>
        <strong>Distance:</strong> {distance}<br/>
        <strong>Mode:</strong> {mode}<br/>
        """,
    }

    return layer, tooltip, center


def gps_layer(
    df: pd.DataFrame,
    crs: str | None = None,
) -> Tuple[pdk.Layer, Dict[str, Any], Point]:
    gdf = convert_to_geodataframe(df, crs=crs)
    gdf.to_crs(epsg=4326, inplace=True)
    center = gdf.geometry.unary_union.centroid

    gdf["latitude"] = gdf.geometry.y
    gdf["longitude"] = gdf.geometry.x
    gdf.reset_index(inplace=True)
    gdf["datetime"] = gdf["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    layer = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        stroked=False,
        filled=True,
        get_position="geometry.coordinates",
        get_radius=7.5,  # Radius is in meters
        get_fill_color=[255, 0, 0],
        get_line_width=5,
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": """<strong>Datetime:</strong> {datetime}<br/>
        <strong>Latitude:</strong> {latitude}<br/>
        <strong>Longitude:</strong> {longitude}<br/>
        """,
    }

    return layer, tooltip, center


def plot(
    df: pd.DataFrame,
    kind: str,
    *,
    crs: str | None = None,
) -> str:
    match kind:
        case "timeline":
            layer, tooltip, center = timeline_layer(df, crs)
        case "gps":
            layer, tooltip, center = gps_layer(df, crs)
        case _:
            raise ValueError(f"Kind '{kind}' not supported.")

    # Set the viewport location
    view_state = pdk.ViewState(longitude=center.x, latitude=center.y, zoom=10)

    # Render
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)  # type: ignore

    return r.to_html()  # type: ignore
