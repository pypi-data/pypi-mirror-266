"""Ancillary function to support core functions in helper.py."""
from __future__ import annotations

import datetime
import json
import logging
import math
import sys
import time
import warnings
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import geopandas as gpd
import geopandas.sindex
import netCDF4
import numpy as np
import numpy.typing as npt
import pandas as pd
import rioxarray as rxr
import shapely
import xarray as xr
from pyproj import CRS
from shapely import centroid
from shapely import get_coordinates
from shapely.geometry import box
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import split

from gdptools.data.odap_cat_data import CatGrids
from gdptools.data.odap_cat_data import CatParams


logger = logging.getLogger(__name__)


def _get_grid_cell_sindex(grid_cells: gpd.GeoDataFrame) -> geopandas.sindex:
    start = time.perf_counter()
    spatial_index = grid_cells.sindex
    # print(type(spatial_index))
    end = time.perf_counter()
    print(f"Spatial index generations finished in {round(end-start, 2)} second(s)")
    return spatial_index


def _reproject_for_weight_calc(
    target_poly: gpd.GeoDataFrame,
    source_poly: gpd.GeoDataFrame,
    wght_gen_crs: Any,
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    start = time.perf_counter()
    # source_poly.set_crs(grid_in_crs, inplace=True)
    source_poly = source_poly.to_crs(wght_gen_crs)
    target_poly = target_poly.to_crs(wght_gen_crs)
    end = time.perf_counter()
    print(f"Reprojecting to epsg:{wght_gen_crs} finished in {round(end-start, 2)}" " second(s)")
    return target_poly, source_poly


def _check_grid_cell_crs(grid_cells: gpd.GeoDataFrame) -> None:
    if not grid_cells.crs:
        error_string = f"grid_cells don't contain a valid crs: {grid_cells.crs}"
        raise ValueError(error_string)


def _check_feature_crs(poly: gpd.GeoDataFrame) -> None:
    if not poly.crs:
        error_string = f"polygons don't contain a valid crs: {poly.crs}"
        raise ValueError(error_string)


def _check_target_poly_idx(poly: gpd.GeoDataFrame, poly_idx: str) -> None:
    if poly_idx not in poly.columns:
        error_string = f"Error: target_poly_idx ({poly_idx}) is not found in the poly" f" ({poly.columns})"
        raise ValueError(error_string)


def _check_source_poly_idx(poly: gpd.GeoDataFrame, poly_idx: List[str]) -> None:
    for id in poly_idx:
        if id not in poly.columns:
            error_string = f"Error: source_poly_idx ({id}) is not found in the poly" f" ({poly.columns})"
            raise ValueError(error_string)


def _get_print_on(numrows: int) -> int:
    """Return an interval to print progress of run_weights() function.

    Args:
        numrows (int): Number of rows: as in number of polygons

    Returns:
        int: Reasonable interval to print progress statements. Prints at about 10%
    """
    if numrows <= 10:  # pragma: no cover
        print_on = 1
    elif numrows <= 100:
        print_on = 10
    elif numrows <= 1000:
        print_on = 100
    elif numrows <= 10000:
        print_on = 1000
    elif numrows <= 100000:
        print_on = 10000
    else:
        print_on = 50000
    return int(print_on)


def _get_crs(crs_in: Any) -> CRS:
    """Return pyproj.CRS given integer or string.

    Args:
        crs_in (Any): integer: epsg code or pyproj string

    Returns:
        CRS: pyproj.CRS
    """
    # if type(crs_in) == int:
    #     in_crs = CRS.from_epsg(crs_in)
    # elif type(crs_in) == str:
    #     in_crs = CRS.from_proj4(crs_in)
    return CRS.from_user_input(crs_in)


def _get_cells_poly(  # noqa
    xr_a: Union[xr.Dataset, xr.DataArray],
    x: str,
    y: str,
    crs_in: Any,
    verbose: Optional[bool] = False,
) -> gpd.GeoDataFrame:
    """Get cell polygons associated with "nodes" in xarray gridded data.

    Args:
        xr_a (Union[xr.Dataset, xr.DataArray]): _description_
        x (str): _description_
        y (str): _description_
        crs_in (Any): _description_
        verbose (Optional[bool], optional): _description_. Defaults to False.

    Returns:
        gpd.GeoDataFrame: _description_

        grid-cell polygons are calculated as follows:

        1) The polygons surrounding each node, where for each node at
           (i, j) the 4 surrounding polygons tpoly1a, tpoly2a, tpoly3a
           tpoly4a are calculated.

        (i-1, j+1)    (i, j+1)  (i+1, j+1)
            *...........*...........*
            .           .           .
            .           .           .
            . (tpoly3a) . (tpoly2a) .
            .           .           .
            .           .           .
        (i-1, j)      (i, j)    (i+1, j)
            *...........*...........*
            .           .           .
            .           .           .
            . (tpoly4a) . (tpoly1a) .
            .           .           .
            .           .           .
            *...........*...........*
        (i-1, j-1)    (i, j-1)  (i+1, j-1)

        2) The centroid is calculated for each of the 4 polygons
           in step 1, from with the bonding polygon of the node
           is determined.
            *..........*..........*
            .          .          .
            .          .          .
            .    p3----------p2   .
            .    |     .      |   .
            .    |     .      |   .
            *....|.....*......|...*
            .    |     .      |   .
            .    |     .      |   .
            .    p4----------p1   .
            .          .          .
            .          .          .
            *..........*..........*

        The grid-cell polygon surounding the node/vertex at (i, j) is
        [p1, p2, p3, p4, p1]

        This is to account for both rectangular and non-rectangular
        grid geometries.
    """
    tlon = xr_a[x]
    tlat = xr_a[y]
    in_crs = crs_in

    lon, lat = np.meshgrid(tlon, tlat)
    poly = []
    if verbose:
        logger.info("calculating surrounding cell vertices")
    start = time.perf_counter()

    tpoly1a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i, j - 1], lat[i, j - 1]],
                [lon[i + 1, j - 1], lat[i + 1, j - 1]],
                [lon[i + 1, j], lat[i + 1, j]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    tpoly2a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i + 1, j], lat[i + 1, j]],
                [lon[i + 1, j + 1], lat[i + 1, j + 1]],
                [lon[i, j + 1], lat[i, j + 1]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    tpoly3a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i, j + 1], lat[i, j + 1]],
                [lon[i - 1, j + 1], lat[i - 1, j + 1]],
                [lon[i - 1, j], lat[i - 1, j]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    tpoly4a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i - 1, j], lat[i - 1, j]],
                [lon[i - 1, j - 1], lat[i - 1, j - 1]],
                [lon[i, j - 1], lat[i, j - 1]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    end = time.perf_counter()
    if verbose:
        logger.info("finished calculating surrounding cell vertices in" f" {round(end-start, 2)} second(s)")

    # print(len(lon_n), len(lat_n), type(lon_n), np.shape(lon_n))
    numcells = len(tpoly1a)
    index = np.array(range(numcells))
    i_index = np.empty(numcells)
    j_index = np.empty(numcells)
    count = 0
    for i in range(1, lon.shape[0] - 1):
        for j in range(1, lon.shape[1] - 1):
            i_index[count] = i
            j_index[count] = j
            count += 1

    if verbose:
        logger.info("calculating centroids")

    start = time.perf_counter()
    # tpoly1 = [Polygon(tpoly1a)]
    p1 = get_coordinates(centroid(tpoly1a))

    # tpoly2 = [Polygon(tpoly2a)]
    p2 = get_coordinates(centroid(tpoly2a))

    # tpoly3 = [Polygon(tpoly3a)]
    p3 = get_coordinates(centroid(tpoly3a))

    # tpoly4 = [Polygon(tpoly4a)]
    p4 = get_coordinates(centroid(tpoly4a))
    end = time.perf_counter()

    if verbose:
        logger.info("finished calculating surrounding cell vertices " f" in {round(end-start, 2)} second(s)")
    lon_point_list = [[p1[i][0], p2[i][0], p3[i][0], p4[i][0]] for i in range(numcells)]
    lat_point_list = [[p1[i][1], p2[i][1], p3[i][1], p4[i][1]] for i in range(numcells)]
    poly = [Polygon(zip(lon_point_list[i], lat_point_list[i])) for i in range(numcells)]  # noqa B905
    df = pd.DataFrame({"i_index": i_index, "j_index": j_index})
    return gpd.GeoDataFrame(df, index=index, geometry=poly, crs=in_crs)


def _build_subset_cat(
    cat_params: CatParams,
    cat_grid: CatGrids,
    bounds: Tuple[np.double, np.double, np.double, np.double],
    date_min: str,
    date_max: Optional[str] = None,
) -> Dict[Any, Any]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Args:
        cat_params (CatParams): _description_
        cat_grid (CatGrids): _description_
        bounds (npt.NDArray[np.double]): _description_
        date_min (str): _description_
        date_max (str, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    xname = cat_grid.X_name
    yname = cat_grid.Y_name
    # print(type(xname), type(yname))
    tname = cat_params.T_name
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]
    gridorder = bool(cat_grid.toptobottom)
    if not gridorder:
        return (
            {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: date_min,
            }
            if date_max is None
            else {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: slice(date_min, date_max),
            }
        )

    elif date_max is None:
        return {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
            tname: date_min,
        }

    else:
        return {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
            tname: slice(date_min, date_max),
        }


def _read_shp_file(shp_file: Union[str, Path, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Read shapefile.

    Args:
        shp_file (Union[str, gpd.GeoDataFrame]): _description_

    Returns:
        gpd.GeoDataFrame: _description_
    """
    if isinstance(shp_file, gpd.GeoDataFrame):
        return shp_file.reset_index()
    gdf = gpd.read_file(shp_file)
    return gdf.reset_index()


def _get_shp_file(
    shp_file: gpd.GeoDataFrame, cat_grid: CatGrids, is_degrees: bool
) -> Tuple[gpd.GeoDataFrame, Tuple[np.double, np.double, np.double, np.double]]:
    """Return GeoDataFrame and bounds of shapefile.

    Args:
        shp_file (gpd.GeoDataFrame): _description_
        cat_grid (CatGrids): _description_
        is_degrees (bool): _description_

    Returns:
        Union[gpd.GeoDataFrame, npt.NDArray[np.double]]: _description_
    """
    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf = shp_file.to_crs(cat_grid.proj)
    # buffer polygons bounding box by twice max resolution of grid
    bbox = box(*gdf.total_bounds)
    # if
    gdf_bounds = bbox.buffer(2.0 * max(cat_grid.resX, cat_grid.resY)).bounds  # type: ignore
    if is_degrees and (gdf_bounds[0] < -180.0) & (gdf_bounds[2] > 180.0):
        newxmax = 180.0 - (abs(gdf_bounds[0]) - 180.0)
        newxmin = -180.0 + (abs(gdf_bounds[2]) - 180.0)
        gdf_bounds = (newxmin, gdf_bounds[1], newxmax, gdf_bounds[3])
        print("Warning: The feature data crosses the anitmeridian.")

    # TODO: need to rethink buffer - leaving it out for now
    # gdf_bounds = gdf.total_bounds.buffer(2.0*buffer)
    return gdf, gdf_bounds


def _is_degrees_nc(ds: xr.Dataset, x_name: str, y_name: str) -> bool:
    """Test if "degree" or "degrees" is present in the units attribute of both X and Y coordinates.

    Args:
        ds (xr.Dataset): The dataset.
        x_name (str): The name of the X coordinate.
        y_name (str): The name of the Y coordinate.

    Returns:
        bool: True if "degree" or "degrees" is present in the units attribute of both X and Y coordinates,
            False otherwise.

    Raises:
        ValueError: If the units attribute is missing from either X or Y coordinate.
    """
    try:
        x_units = ds[x_name].attrs["units"]
        y_units = ds[y_name].attrs["units"]
        if "degree" in x_units.lower() or "degree" in y_units.lower():
            return True
        return False
    except KeyError as e:
        raise ValueError(
            f"Both {x_name} and {y_name} coordinates must have units attribute. Add units to coordinates of the dataset"
        ) from e


def _is_degrees(ds: xr.Dataset, cat_grid: CatGrids) -> bool:
    """Test if degrees in attributes on longitude.

    Args:
        ds (xr.Dataset): The dataset.
        cat_grid (CatGrids): The CatGrids.

    Returns:
        bool: True if "degree" or "degrees" is in the units attribute of both X and Y coordinates, False otherwise.

    Raises:
        ValueError: If the "units" attribute is missing from either X or Y coordinate.
    """
    try:
        x_units = ds[cat_grid.X_name].attrs["units"]
        y_units = ds[cat_grid.Y_name].attrs["units"]
        if "degree" in x_units.lower() or "degree" in y_units.lower():
            return True
        return False
    except KeyError as e:
        raise ValueError(
            f"Both {ds[cat_grid.X_name]} and {ds[cat_grid.Y_name]} coordinates must have units attribute."
        ) from e


def _is_lon_0_360(vals: npt.NDArray[np.double]) -> bool:
    """Test if longitude spans 0-360.

    Args:
        vals (npt.NDArray[np.double]): _description_

    Returns:
        bool: _description_
    """
    result = False
    if (vals[0] > 180.0) & (np.min(vals) > 0.0):
        result = True  # False
    elif (np.max(vals) > 180.0) & (np.min(vals) > 180.0):
        result = True  # False
    elif np.max(vals) > 180.0:
        result = True

    return result


def _get_shp_bounds_w_buffer(
    gdf: gpd.GeoDataFrame,
    ds: Union[xr.DataArray, xr.Dataset],
    crs: Any,
    lon: str,
    lat: str,
) -> npt.NDArray[np.double]:
    """_get_shp_bounds_w_buffer Return bounding box based on 2 * max(ds.dx, ds.dy).

    _extended_summary_

    Args:
        gdf (gpd.GeoDataFrame): _description_
        ds (Union[xr.DataArray, xr.Dataset]): _description_
        crs (Any): _description_
        lon (str): _description_
        lat (str): _description_

    Raises:
        ValueError: _description_

    Returns:
        npt.NDArray[np.double]: _description_
    """
    bbox = box(*gdf.to_crs(crs).total_bounds)
    if bbox.area == np.nan:
        raise ValueError(f"unable to reproject f_feature's projection {gdf.crs} to proj_ds{crs}")
    return np.asarray(
        bbox.buffer(2 * max(max(np.diff(ds[lat].values)), max(np.diff(ds[lon].values)))).bounds  # type: ignore
    )


def _check_for_intersection(
    cat_params: CatParams,
    cat_grid: CatGrids,
    gdf: gpd.GeoDataFrame,
) -> Tuple[bool, bool, bool]:
    """Check broadly for intersection between features and grid.

    Args:
        cat_params (CatParams): _description_
        cat_grid (CatGrids): _description_
        gdf (gpd.GeoDataFrame): _description_

    Returns:
        Tuple[bool, bool, bool]: _description_
    """
    is_degrees = False
    is_intersect = True
    is_0_360 = False
    ds_url = cat_params.URL
    ds = xr.open_dataset(ds_url + "#fillmismatch", decode_coords=True, chunks={})
    xvals = ds[cat_grid.X_name]
    yvals = ds[cat_grid.Y_name]
    minx = xvals.values.min()
    maxx = xvals.values.max()
    miny = yvals.values.min()
    maxy = yvals.values.max()
    ds_bbox = box(minx, miny, maxx, maxy)
    bounds = _get_shp_bounds_w_buffer(
        gdf,
        ds,
        cat_grid.proj,
        cat_grid.X_name,
        cat_grid.Y_name,
    )
    is_degrees = _is_degrees(ds=ds, cat_grid=cat_grid)
    if is_degrees & (not ds_bbox.intersects(box(*np.asarray(bounds).tolist()))):
        is_intersect = False
        is_0_360 = _is_lon_0_360(xvals.values)
        if is_0_360:
            warning_string = (
                "0-360 longitude crossing the international date line encountered.\n"
                "Longitude coordinates will be 0-360 in output."
            )
            warnings.warn(warning_string, stacklevel=2)

    return is_intersect, is_degrees, is_0_360


def _check_for_intersection_nc(
    ds: xr.Dataset,
    x_name: str,
    y_name: str,
    proj: Any,
    gdf: gpd.GeoDataFrame,
) -> Tuple[bool, bool, bool]:
    """Check broadly for intersection between features and grid.

    Args:
        ds (xr.Dataset): _description_
        x_name (str): _description_
        y_name (str): _description_
        proj (Any): _description_
        gdf (gpd.GeoDataFrame): _description_

    Returns:
        Tuple[bool, bool, bool]: _description_
    """
    is_degrees = False
    is_intersect = True
    is_0_360 = False

    xvals = ds[x_name]
    yvals = ds[y_name]
    minx = xvals.values.min()
    maxx = xvals.values.max()
    miny = yvals.values.min()
    maxy = yvals.values.max()
    ds_bbox = box(minx, miny, maxx, maxy)
    bounds = _get_shp_bounds_w_buffer(
        gdf,
        ds,
        proj,
        x_name,
        y_name,
    )
    is_degrees = _is_degrees_nc(ds=ds, x_name=x_name, y_name=y_name)
    if is_degrees & (not ds_bbox.intersects(box(*np.asarray(bounds).tolist()))):
        is_intersect = False
        is_0_360 = _is_lon_0_360(xvals.values)
        if is_0_360:
            warning_string = (
                "0-360 longitude crossing the international date line encountered.\n"
                "Longitude coordinates will be 0-360 in output."
            )
            warnings.warn(warning_string, stacklevel=2)

    return is_intersect, is_degrees, is_0_360


def _get_data_via_catalog(
    cat_params: CatParams,
    cat_grid: CatGrids,
    bounds: Tuple[np.double, np.double, np.double, np.double],
    begin_date: str,
    end_date: Optional[str] = None,
    rotate_lon: Optional[bool] = False,
) -> xr.DataArray:
    """Get xarray spatial and temporal subset.

    Args:
        cat_params (CatParams): _description_
        cat_grid (CatGrids): _description_
        bounds (Tuple[np.double, np.double, np.double, np.double]): _description_
        begin_date (str): _description_
        end_date (Optional[str], optional): _description_. Defaults to None.
        rotate_lon (Optional[bool], optional): _description_. Defaults to False.

    Returns:
        xr.DataArray: _description_
    """
    ds_url = cat_params.URL
    ds = xr.open_dataset(ds_url + "#fillmismatch", decode_coords=True, chunks={})
    if rotate_lon:
        lon = cat_grid.X_name
        ds.coords[lon] = (ds.coords["lon"] + 180) % 360 - 180
        ds = ds.sortby(ds[lon])

    # get grid data subset to polygons buffered bounding box
    ss_dict = _build_subset_cat(cat_params, cat_grid, bounds, begin_date, end_date)
    # gridMET requires the '#fillmismatch' see:
    # https://discourse.oceanobservatories.org/
    # t/
    # accessing-data-on-thredds-opendap-via-python-netcdf4-or-xarray
    # -dealing-with-fillvalue-type-mismatch-error/61

    varname = cat_params.varname
    return ds[varname].sel(**ss_dict)


def _get_weight_df(wght_file: Union[str, pd.DataFrame], poly_idx: str) -> pd.DataFrame:
    if isinstance(wght_file, pd.DataFrame):
        # wghts = wght_file.copy()
        wghts = wght_file.astype({"i": int, "j": int, "wght": float, poly_idx: str})
    elif isinstance(wght_file, str):
        wghts = pd.read_csv(wght_file, dtype={"i": int, "j": int, "wght": float, poly_idx: str})
    else:
        sys.exit("wght_file must be one of string or pandas.DataFrame")
    return wghts


def _date_range(p_start: str, p_end: str, intv: int) -> Iterator[str]:
    """Return a date range.

    Args:
        p_start (str): _description_
        p_end (str): _description_
        intv (int): _description_

    Yields:
        Iterator[str]: _description_
    """
    start = datetime.strptime(p_start, "%Y-%m-%d")
    end = datetime.strptime(p_end, "%Y-%m-%d")
    diff = (end - start) / intv
    for i in range(intv):
        yield (start + diff * i).strftime("%Y-%m-%d")
    yield end.strftime("%Y-%m-%d")


def _get_catalog_time_increment(param: dict) -> Tuple[int, str]:  # type: ignore
    interval = str(param.get("interval")).split(" ")
    return int(interval[0]), str(interval[1])


def _get_dataframe(object: Union[str, pd.DataFrame]) -> pd.DataFrame:
    if isinstance(object, str):
        return pd.DataFrame.from_dict(json.loads(object))
    else:
        return object


# this function is copied from here:
# https://github.com/gboeing/osmnx/blob/main/osmnx/utils_geo.py
# if it turns out to be helpful in speedin up intersections then I'll import it via
# the package - for now copied in here for development testing.
def _quadrat_cut_geometry(
    geometry: Union[shapely.geometry.Polygon, shapely.geometry.MultiPolygon],
    quadrat_width: float,
    min_num: Optional[int] = 3,
) -> shapely.geometry.MultiPolygon:
    """Split a Polygon or MultiPolygon up into sub-polygons of a specified size.

    Args:
        geometry (Union[shapely.geometry.Polygon, shapely.geometry.MultiPolygon]): _description_
        quadrat_width (float): _description_
        min_num (Optional[int], optional): _description_. Defaults to 3.

    Returns:
        shapely.geometry.MultiPolygon: _description_
    """
    # create n evenly spaced points between the min and max x and y bounds
    west, south, east, north = geometry.bounds
    x_num = int(np.ceil((east - west) / quadrat_width) + 1)
    y_num = int(np.ceil((north - south) / quadrat_width) + 1)
    x_points = np.linspace(west, east, num=np.max(x_num, min_num))
    y_points = np.linspace(south, north, num=np.max(y_num, min_num))

    # create a quadrat grid of lines at each of the evenly spaced points
    vertical_lines = [LineString([(x, y_points[0]), (x, y_points[-1])]) for x in x_points]
    horizont_lines = [LineString([(x_points[0], y), (x_points[-1], y)]) for y in y_points]
    lines = vertical_lines + horizont_lines

    # recursively split the geometry by each quadrat line
    geometries = [geometry]

    for line in lines:
        # split polygon by line if they intersect, otherwise just keep it
        split_geoms = [split(g, line).geoms if g.intersects(line) else [g] for g in geometries]
        # now flatten the list and process these split geoms on the next line in
        # the list of lines
        geometries = [g for g_list in split_geoms for g in g_list]

    return MultiPolygon(geometries)


def _get_default_val(native_dtype: np.dtype):  # type: ignore
    """Get default fill value based on gridded data dtype.

    Args:
        native_dtype (np.dtype): _description_

    Raises:
        TypeError: _description_

    Returns:
        _type_: _description_
    """
    if native_dtype.kind == "i":
        dfval = netCDF4.default_fillvals["i8"]
    elif native_dtype.kind == "f":
        dfval = netCDF4.default_fillvals["f8"]
    else:
        raise TypeError(
            "gdptools currently only supports int and float types." f"The value type here is {native_dtype}"
        )

    return dfval


def _get_interp_array(
    n_geo: int,
    nts: int,
    native_dtype: Union[np.dtype[np.double], np.dtype[np.int_]],
    default_val: Any,
) -> Union[npt.NDArray[np.int_], npt.NDArray[np.double]]:
    """Get array for interpolation based on the dtype of the gridded data.

    _extended_summary_

    Args:
        n_geo (int): _description_
        nts (int): _description_
        native_dtype (np.dtype): _description_
        default_val (Any): _description_

    Raises:
        TypeError: _description_

    Returns:
        Union[npt.NDArray[np.int_], npt.NDArray[np.double]]: _description_
    """
    if native_dtype.kind == "i":
        # val_interp = np.empty((nts, n_geo), dtype=np.dtype("int64"))
        val_interp = np.full((nts, n_geo), dtype=np.dtype("int64"), fill_value=default_val)
    elif native_dtype.kind == "f":
        # val_interp = np.empty((nts, n_geo), dtype=np.dtype("float64"))
        val_interp = np.full((nts, n_geo), dtype=np.dtype("float64"), fill_value=default_val)
    else:
        raise TypeError(
            "gdptools currently only supports int and float types." f"The value type here is {native_dtype}"
        )

    return val_interp


def _get_top_to_bottom(data: Union[xr.Dataset, xr.DataArray], y_coord: str) -> bool:
    """Get orientation of y-coordinate data in xarray Dataset.

    Args:
        data (xr.Dataset): _description_
        y_coord (str): _description_

    Returns:
        bool: _description_
    """
    yy = data.coords[y_coord].values
    return yy[0] <= yy[-1]


def _get_xr_dataset(ds: Union[str, xr.Dataset]) -> xr.Dataset:
    """Get xarray.Dataset."""
    if isinstance(ds, str):
        return xr.open_dataset(ds + "#fillmismatch", decode_coords=True, chunks={})
    if isinstance(ds, Path):
        return xr.open_dataset(ds, decode_coords=True, chunks={})
    elif isinstance(ds, xr.Dataset):
        return ds
    elif isinstance(ds, xr.DataArray):
        raise TypeError("Expected xarray.Dataset, not xarray.DataArray")
    else:
        raise TypeError("Invalid xarray dataset, must be a URL or xarray Dataset")


def _get_rxr_dataset(ds: Union[str, xr.DataArray, xr.Dataset]) -> Union[xr.DataArray, xr.Dataset]:
    """Get xarray.Dataset."""
    if isinstance(ds, (xr.Dataset, xr.DataArray)):
        return ds
    elif isinstance(ds, str):
        try:
            # Attempt to open the dataset
            return rxr.open_rasterio(ds)
        except Exception as e:
            # Return a useful error message
            return f"Failed to open dataset from '{ds}'. Error: {e}"
    else:
        # Handle cases where ds is neither a Dataset/DataArray nor a string
        return f"Unsupported type for ds: {type(ds)}. Expected str, xr.DataArray, or xr.Dataset."


def _interpolate_sample_points(
    geom: gpd.GeoSeries, spacing: Union[float, int], calc_crs: Any, crs: Any
) -> Tuple[list[float], list[float], list[float]]:
    """Interpolated points at equal distances along a line.

    Return the interpolated points and their distances from the initial point.

    Args:
        geom (GeoSeries): Line geometry to pull sample points from
        spacing (float): The distance in meters between the sample points
        calc_crs(Any): Coordinate system to calculate interpolated points and distance.
        crs (Any): Coordinate system to return the points in. EPSG code or Proj 4
            string.

    Returns:
        x (Numpy Array): Array of x coordinates of the sample points
        y (Numpy Array): Array of y coordinates of the sample points
        dist (Numpy Array): Array of distances from the first point to each of the
            sample points
    """
    # equidistant_crs = "+proj=eqdc +lat_0=39 +lon_0=-96 +lat_1=33 \
    #     +lat_2=45 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs +type=crs"
    # rp_geom: gpd.GeoSeries = geom.to_crs(equidistant_crs)
    rp_geom: gpd.GeoSeries = geom.to_crs(calc_crs)
    # Get line length
    length = rp_geom.length.values[0]
    # Calculate the number of sample points
    num_points = int(length / spacing) + 1
    # Create empty numpy arrays for x,y coords
    x = np.zeros(num_points, dtype=np.double)
    y = np.zeros(num_points, dtype=np.double)
    dist = np.zeros(num_points, dtype=np.double)
    # Find sample points on line  # from nldi_xstools.PathGen
    d = 0.0
    index = 0
    while d < length:
        point = rp_geom.interpolate(d)
        # Project to grid crs
        point = point.to_crs(crs)
        # x[index] = point.x
        # y[index] = point.y
        # fix for FutureWarning
        x[index] = float(point.iloc[0].x)
        y[index] = float(point.iloc[0].y)
        dist[index] = d
        d += spacing
        index += 1

    return x, y, dist


def _get_line_vertices(geom: gpd.GeoDataFrame, calc_crs: Any, crs: Any) -> Tuple[list[float], list[float], list[float]]:
    """Return the vertices and the distance inbetween of a line in a GeoDataFrame.

    Args:
        geom (GeoDataFrame): A GeoDataFrame with a single line geometry
        calc_crs(Any): Coordinate system to calculate vertex distance.
        crs (Any): Coordinate system to return the points in. EPSG code or Proj 4 string.

    Returns:
        Tuple[list[float], list[float], list[float]]: Three list containing the x coords,
            y coords and distance in meters from the first vertex to each vertex
    """
    # project to equidistant crs to calculate distance between vertices
    rp_geom: gpd.GeoSeries = geom.to_crs(calc_crs).reset_index()
    if type(rp_geom.geometry[0]) is LineString:
        x, y = rp_geom.geometry[0].coords.xy
    else:  # If it is a multilinestring:
        x, y = rp_geom.geometry[0].geoms[0].coords.xy
    x = list(x)
    y = list(y)

    # cal distance between the first vertex and each vertex
    for i in range(len(x)):
        if i == 0:
            dist = [0.0]
        else:
            d = dist[i - 1] + math.dist([x[i - 1], y[i - 1]], [x[i], y[i]])
            dist.append(d)

    # Project line to grid crs and export vertex coords
    rp_geom: gpd.GeoSeries = geom.to_crs(crs).reset_index()
    if type(rp_geom.geometry[0]) is LineString:
        x, y = rp_geom.geometry[0].coords.xy
    else:  # If it is a multilinestring:
        x, y = rp_geom.geometry[0].geoms[0].coords.xy
    x = list(x)
    y = list(y)

    return x, y, dist


def _cal_point_stats(
    data_array: xr.DataArray,
    stat: str,
    userdata_type: str,
    skipna: Union[bool, None] = None,
) -> dict[Any]:
    """Calculate the specified stats from a geodataframe of points.

    Args:
        data_array: (xr.DataArray): Xarray DataArray of values pulled from
            a gridded dataset at interpolated points
        stat (str): A string indicating which statistics to calculated.
            Options: all, mean, median, std, min, max
        userdata_type (str): A string indicating the type of the User Data Class. Options
            are 'UserCatData', 'ClimRCatData', 'UserTiffData' and 'ODAPCatData'.
        skipna (bool or None): Optional; If True, skip nodata values in the gridded
            data for the calculations of statistics. By default, only skips missing
            values for float dtypes.

    Returns:
        dict: A dictionary of statistical values
    """
    out_vals: dict[Any] = {}

    # Calculate the stats
    if userdata_type != "UserTiffData":
        userdata_type = "other"

    if stat == "all":
        stat = ["mean", "median", "std", "min", "max"]
    else:
        stat = [stat]

    options = {
        "UserTiffData": {
            "mean": data_array.mean(dim=["pt"], skipna=skipna).values,
            "median": data_array.median(dim=["pt"], skipna=skipna).values,
            "std": data_array.std(dim=["pt"], skipna=skipna).values,
            "min": data_array.min(dim=["pt"], skipna=skipna).values,
            "max": data_array.max(dim=["pt"], skipna=skipna).values,
        },
        "other": {
            "mean": data_array.mean(dim=["pt"], skipna=skipna),
            "median": data_array.median(dim=["pt"], skipna=skipna),
            "std": data_array.std(dim=["pt"], skipna=skipna),
            "min": data_array.min(dim=["pt"], skipna=skipna),
            "max": data_array.max(dim=["pt"], skipna=skipna),
        },
    }

    for i in stat:
        out_vals[i] = options[userdata_type][i]

    return out_vals


def _buffer_line(
    geometry: gpd.GeoSeries,
    buffer: Union[float, int],
    proj_feature: CRS,
    calc_crs: Any,
) -> gpd.GeoSeries:
    """Buffer a line segment.

    The line gets reprojected to an AEA projection, so that the buffer can be
    submitted in meters. Then the buffered geometry it reprojected back to
    a user specified crs.

    Args:
        geometry (GeoSeries): Geometry of the query line
        buffer (float): Value in meters of the diameter of the buffer
        proj_feature (CRS): Coordinate system of the returned buffer geometry
        calc_crs: Coordinate system in which to perform the statistical calculations

    Returns:
        new_geometry (GeoSeries): Geometry of the buffer
    """
    return geometry.to_crs(calc_crs).buffer(buffer).to_crs(proj_feature)


def _dataframe_to_geodataframe(df: pd.DataFrame, crs: str) -> gpd.GeoDataFrame:
    """Convert pandas Dataframe to Geodataframe."""
    geometry = [Point(xy) for xy in zip(df.x, df.y)]  # noqa: B905
    try:
        df = df.drop(["x", "y", "crs"], axis=1)
    except KeyError:
        df = df.drop(["x", "y"], axis=1)

    return gpd.GeoDataFrame(df, geometry=geometry, crs=crs)


def _process_period(period: List[Optional[Union[str, pd.Timestamp, datetime.datetime]]]) -> List[str]:
    """Process the period list and convert elements to pd.Timestamp.

    Args:
        period: A list of elements representing a time period. Each element can be a string,
            pd.Timestamp, datetime.datetime, or None.

    Returns:
        List[pd.Timestamp]: A list of pd.Timestamp objects representing the processed period.

    Raises:
        ValueError: If period is not a list or if it does not contain 1 or 2 elements.
        ValueError: If the elements of period are not of the expected types.

    Examples:
        >>> _process_period(['2022-01-01', '2022-01-31'])
        [Timestamp('2022-01-01 00:00:00'), Timestamp('2022-01-31 00:00:00')]
    """
    # Check if period is a list
    if not isinstance(period, list):
        raise ValueError("period must be a list")

    # Check if the list contains 1 or 2 elements
    if len(period) not in [1, 2]:
        raise ValueError("period must contain 1 or 2 elements")

    # Convert strings to datetime and validate elements
    result = []
    for element in period:
        if isinstance(element, str):
            result.append(element)
        elif isinstance(element, datetime.datetime):
            result.append(element.isoformat())
        elif isinstance(element, pd.Timestamp) or element is None:
            result.append(element.isoformat())
        else:
            raise ValueError("Elements of period must be string, pd.Timestamp, datetime.datetime, or None")

    return result
