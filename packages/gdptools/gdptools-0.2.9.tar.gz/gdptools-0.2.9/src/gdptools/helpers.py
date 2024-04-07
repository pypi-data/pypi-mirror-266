"""Primary functions for poly-to-poly area-weighted mapping."""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import xarray as xr

from gdptools.data.odap_cat_data import CatClimRItem
from gdptools.data.odap_cat_data import CatGrids
from gdptools.data.odap_cat_data import CatParams
from gdptools.data.odap_cat_data import climr_to_odap
from gdptools.utils import _check_for_intersection
from gdptools.utils import _get_data_via_catalog
from gdptools.utils import _get_shp_file
from gdptools.utils import _read_shp_file

# from numba import jit

logger = logging.getLogger(__name__)

pd_offset_conv: Dict[str, str] = {
    "years": "Y",
    "months": "M",
    "days": "D",
    "hours": "H",
}


def build_subset(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    tname: str,
    toptobottom: bool,
    date_min: str,
    date_max: Optional[str] = None,
) -> Dict[str, object]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Args:
        bounds (np.ndarray): _description_
        xname (str): _description_
        yname (str): _description_
        tname (str): _description_
        toptobottom (bool): _description_
        date_min (str): _description_
        date_max (Optional[str], optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]
    if not toptobottom:
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


def build_subset_tiff(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    toptobottom: bool,
    bname: str,
    band: int,
) -> Mapping[Any, Any]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Args:
        bounds (npt.NDArray[np.double]): _description_
        xname (str): _description_
        yname (str): _description_
        toptobottom (bool): _description_
        bname (str): _description_
        band (int): _description_

    Returns:
        Dict[str, object]: _description_
    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]

    return (
        {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
            bname: band,
        }
        if toptobottom
        else {
            xname: slice(minx, maxx),
            yname: slice(maxy, miny),
            bname: band,
        }
    )


def build_subset_tiff_da(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    toptobottom: Union[int, bool],
) -> Mapping[Any, Any]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Args:
        bounds (npt.NDArray[np.double]): _description_
        xname (str): _description_
        yname (str): _description_
        toptobottom (bool): _description_

    Returns:
        Dict[str, object]: _description_
    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]

    return (
        {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
        }
        if toptobottom
        else {
            xname: slice(minx, maxx),
            yname: slice(maxy, miny),
        }
    )


def get_data_subset_odap_catalog(
    param_dict: dict[str, dict[str, Any]],
    grid_dict: dict[str, dict[str, Any]],
    key: str,
    shp_file: Union[str, gpd.GeoDataFrame],
    begin_date: str,
    end_date: str,
) -> xr.DataArray:
    """get_data_subset_odap_catalog Get xarray subset data.

    _extended_summary_

    Args:
        param_dict (dict[str, dict[str, Any]]): _description_
        grid_dict (dict[str, dict[str, Any]]): _description_
        key (str): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        begin_date (str): _description_
        end_date (str): _description_

    Returns:
        xr.DataArray: _description_
    """
    cat_params = CatParams(**param_dict[key])
    cat_grid = CatGrids(**grid_dict[key])
    # run check on intersection of shape features and gridded data
    gdf = _read_shp_file(shp_file)
    is_intersect, is_degrees, is_0_360 = _check_for_intersection(cat_params=cat_params, cat_grid=cat_grid, gdf=gdf)

    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf, gdf_bounds = _get_shp_file(shp_file=gdf, cat_grid=cat_grid, is_degrees=is_degrees)

    rotate_ds = bool((not is_intersect) & is_degrees & (is_0_360))
    return _get_data_via_catalog(
        cat_params=cat_params,
        cat_grid=cat_grid,
        bounds=gdf_bounds,
        begin_date=begin_date,
        end_date=end_date,
        rotate_lon=rotate_ds,
    )


def get_data_subset_climr_catalog(
    cat_dict: dict[str, dict[str, Any]],
    key: str,
    shp_file: Union[str, gpd.GeoDataFrame],
    begin_date: str,
    end_date: str,
) -> xr.DataArray:
    """get_data_subset_climr_catalog Get xarray subset data.

    _extended_summary_

    Args:
        cat_dict (dict[str, dict[str, Any]]): _description_
        key (str): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        begin_date (str): _description_
        end_date (str): _description_

    Returns:
        xr.DataArray: _description_
    """
    cat = CatClimRItem(**cat_dict[key])
    # run check on intersection of shape features and gridded data
    cat_params, cat_grid = climr_to_odap(cat)
    gdf = _read_shp_file(shp_file)
    is_intersect, is_degrees, is_0_360 = _check_for_intersection(cat_params=cat_params, cat_grid=cat_grid, gdf=gdf)

    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf, gdf_bounds = _get_shp_file(shp_file=gdf, cat_grid=cat_grid, is_degrees=is_degrees)

    rotate_ds = bool((not is_intersect) & is_degrees & (is_0_360))
    return _get_data_via_catalog(
        cat_params=cat_params,
        cat_grid=cat_grid,
        bounds=gdf_bounds,
        begin_date=begin_date,
        end_date=end_date,
        rotate_lon=rotate_ds,
    )


def get_data_subset_user_catalog(
    cat_dict: dict[str, dict[str, Any]],
    key: str,
    shp_file: Union[str, gpd.GeoDataFrame],
    begin_date: str,
    end_date: str,
) -> xr.DataArray:
    """get_data_subset_climr_catalog Get xarray subset data.

    _extended_summary_

    Args:
        cat_dict (dict[str, dict[str, Any]]): _description_
        key (str): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        begin_date (str): _description_
        end_date (str): _description_

    Returns:
        xr.DataArray: _description_
    """
    cat = CatClimRItem(**cat_dict[key])
    # run check on intersection of shape features and gridded data
    cat_params, cat_grid = climr_to_odap(cat)
    gdf = _read_shp_file(shp_file)
    is_intersect, is_degrees, is_0_360 = _check_for_intersection(cat_params=cat_params, cat_grid=cat_grid, gdf=gdf)

    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf, gdf_bounds = _get_shp_file(shp_file=gdf, cat_grid=cat_grid, is_degrees=is_degrees)

    rotate_ds = bool((not is_intersect) & is_degrees & (is_0_360))
    return _get_data_via_catalog(
        cat_params=cat_params,
        cat_grid=cat_grid,
        bounds=gdf_bounds,
        begin_date=begin_date,
        end_date=end_date,
        rotate_lon=rotate_ds,
    )
