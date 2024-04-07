"""Tests for .helper functions."""
import gc
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import pytest
import xarray as xr
from pytest import FixtureRequest

from gdptools.helpers import get_data_subset_climr_catalog
from gdptools.helpers import get_data_subset_odap_catalog


@pytest.fixture(scope="function")
def get_gdf() -> gpd.GeoDataFrame:
    """Create GeoDataFrame."""
    return gpd.read_file("./tests/data/hru_1210_epsg5070.shp")  # type: ignore


@pytest.fixture(scope="function")
def get_xarray() -> xr.Dataset:
    """Create xarray Dataset."""
    # return xr.open_dataset("./data/cape_cod_tmax.nc")
    ds = xr.open_dataset(
        "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_tmmx_1979_CurrentYear_CONUS.nc"
    )
    yield ds
    del ds
    gc.collect()


@pytest.fixture(scope="function")
def get_file_path(tmp_path: Path) -> Path:
    """Get temp file path."""
    return tmp_path / "test.csv"


@pytest.fixture(scope="function")
def get_out_path(tmp_path: Path) -> Path:
    """Get temp file output path."""
    return tmp_path


data_crs = 4326
x_coord = "lon"
y_coord = "lat"
t_coord = "day"
sdate = "1979-01-01"
edate = "1979-01-07"
var = "daily_maximum_temperature"
shp_crs = 5070
shp_poly_idx = "hru_id_nat"
wght_gen_crs = 6931


@pytest.fixture(scope="function")
def climrcat() -> dict[str, dict[str, Any]]:
    """Return climr catalog json."""
    cat = "https://mikejohnson51.github.io/climateR-catalogs/catalog.parquet"
    climr: pd.DataFrame = pd.read_parquet(cat)
    _id = "terraclim"  # noqa
    _varname = "aet"  # noqa
    cat_d: dict[str, Any] = climr.query("id == @_id & varname == @_varname").to_dict("records")[0]
    data = dict(zip([_varname], [cat_d]))  # noqa
    yield data
    del data
    gc.collect()


@pytest.fixture(scope="function")
def catparam() -> dict[str, dict[str, Any]]:
    """Return parameter json."""
    cat_params = "https://mikejohnson51.github.io/opendap.catalog/cat_params.json"
    params = pd.read_json(cat_params)
    _id = "terraclim"  # noqa
    _varname = "aet"  # noqa
    cat_d: dict[str, Any] = params.query("id == @_id & varname == @_varname").to_dict("records")[0]
    data = dict(zip([_varname], [cat_d]))  # noqa
    yield data
    del data
    gc.collect()


@pytest.fixture(scope="function")
def catgrid(catparam) -> dict[str, dict[str, Any]]:  # type: ignore
    """Return grid json."""
    cat_grid = "https://mikejohnson51.github.io/opendap.catalog/cat_grids.json"
    grids = pd.read_json(cat_grid)
    _gridid = catparam.get("aet").get("grid_id")  # noqa
    _varname = "aet"  # noqa
    cat_g: dict[str, Any] = grids.query("grid_id == @_gridid").to_dict("records")[0]
    data = dict(zip([_varname], [cat_g]))  # noqa
    yield data
    del data
    gc.collect()


@pytest.fixture(scope="function")
def get_gdf_world() -> gpd.GeoDataFrame:
    """Get gdf file with country testing."""
    gdf = gpd.read_file("./tests/data/TM_WORLD_BORDERS_SIMPL-0.3/TM_WORLD_BORDERS_SIMPL-0.3.shp")  # type: ignore
    yield gdf
    del gdf
    gc.collect()


@pytest.fixture(scope="function")
def get_begin_date() -> str:
    """Get begin date."""
    return "2005-01-01"


@pytest.fixture(scope="function")
def get_end_date() -> str:
    """Get end date."""
    return "2005-02-01"


@pytest.mark.parametrize(
    "cp,cg,gdf,sd,ed,name",
    [
        (
            "catparam",
            "catgrid",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Chile",
        ),
        (
            "catparam",
            "catgrid",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Netherlands",
        ),
        (
            "catparam",
            "catgrid",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Kenya",
        ),
        (
            "catparam",
            "catgrid",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Samoa",
        ),
        (
            "catparam",
            "catgrid",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Fiji",
        ),
    ],
)
def test_get_data_subset_odap_catalog(
    cp: str, cg: str, gdf: str, sd: str, ed: str, name: str, request: FixtureRequest
) -> None:
    """Test subset catalog."""
    ds = get_data_subset_odap_catalog(
        param_dict=request.getfixturevalue(cp),
        grid_dict=request.getfixturevalue(cg),
        key="aet",
        shp_file=request.getfixturevalue(gdf).query("NAME == @name"),
        begin_date=request.getfixturevalue(sd),
        end_date=request.getfixturevalue(ed),
    )

    assert isinstance(ds, xr.DataArray)


@pytest.mark.parametrize(
    "cat,gdf,sd,ed,name",
    [
        (
            "climrcat",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Chile",
        ),
        (
            "climrcat",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Netherlands",
        ),
        (
            "climrcat",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Kenya",
        ),
        (
            "climrcat",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Samoa",
        ),
        (
            "climrcat",
            "get_gdf_world",
            "get_begin_date",
            "get_end_date",
            "Fiji",
        ),
    ],
)
def test_get_data_subset_climr_catalog(
    cat: str, gdf: str, sd: str, ed: str, name: str, request: FixtureRequest
) -> None:
    """Test subset catalog."""
    ds = get_data_subset_climr_catalog(
        cat_dict=request.getfixturevalue(cat),
        key="aet",
        shp_file=request.getfixturevalue(gdf).query("NAME == @name"),
        begin_date=request.getfixturevalue(sd),
        end_date=request.getfixturevalue(ed),
    )

    assert isinstance(ds, xr.DataArray)
