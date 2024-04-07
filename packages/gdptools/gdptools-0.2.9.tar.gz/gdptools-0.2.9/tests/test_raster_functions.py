"""Tests for raster functions."""

import gc
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import geopandas as gpd
import pandas as pd
import pytest
import rioxarray as rxr
import xarray as xr
from dask.distributed import Client
from dask.distributed import LocalCluster
from pytest import FixtureRequest

from gdptools import ZonalGen
from gdptools.data.user_data import UserTiffData


@contextmanager
def get_dask_client():
    """Get dask cluster."""
    cluster = LocalCluster(n_workers=os.cpu_count())
    client = Client(cluster)
    try:
        yield client
    finally:
        cluster.close()
        client.close()


@pytest.fixture(scope="function")
def get_tiff_slope() -> xr.DataArray:
    """Get tiff slope file."""
    ds = rxr.open_rasterio("./tests/data/rasters/slope/slope.tif")  # type: ignore
    yield ds
    del ds
    gc.collect()


@pytest.fixture(scope="function")
def get_tiff_text() -> xr.DataArray:
    """Get tiff text_prms file."""
    ds = rxr.open_rasterio("./tests/data/rasters/TEXT_PRMS/TEXT_PRMS.tif")  # type: ignore
    yield ds
    del ds
    gc.collect()


@pytest.fixture(scope="function")
def get_gdf() -> gpd.GeoDataFrame:
    """Get gdf file."""
    gdf = gpd.read_file("./tests/data/Oahu.shp")
    yield gdf
    del gdf
    gc.collect()


@pytest.mark.parametrize(
    "vn,xn,yn,bd,bn,crs,cat,ds,gdf,fid",
    [
        (
            "slope",
            "x",
            "y",
            1,
            "band",
            26904,
            False,
            "get_tiff_slope",
            "get_gdf",
            "fid",
        ),
        (
            "TEXT_PRMS",
            "x",
            "y",
            1,
            "band",
            26904,
            True,
            "get_tiff_text",
            "get_gdf",
            "fid",
        ),
    ],
)
def test_cat_tiff_intersection(
    vn: str,
    xn: str,
    yn: str,
    bd: int,
    bn: str,
    crs: Any,
    cat: bool,
    ds: str,
    gdf: str,
    fid: str,
    request: FixtureRequest,
) -> None:
    """Test tiff intersection function."""
    data = UserTiffData(
        var=vn,
        ds=request.getfixturevalue(ds),
        proj_ds=crs,
        x_coord=xn,
        y_coord=yn,
        bname=bn,
        band=bd,
        f_feature=request.getfixturevalue(gdf),
        id_feature=fid,
        proj_feature=crs,
    )
    tmpdir = TemporaryDirectory()
    zonal_gen = ZonalGen(
        user_data=data,
        zonal_engine="serial",
        zonal_writer="csv",
        out_path=tmpdir.name,
        file_prefix="tmpzonal",
    )
    stats = zonal_gen.calculate_zonal(categorical=cat)

    assert isinstance(stats, pd.DataFrame)
    file = Path(tmpdir.name) / "tmpzonal.csv"
    assert file.exists()


@pytest.mark.parametrize(
    "vn,xn,yn,bd,bn,crs,cat,ds,gdf,fid",
    [
        (
            "slope",
            "x",
            "y",
            1,
            "band",
            26904,
            False,
            "get_tiff_slope",
            "get_gdf",
            "fid",
        ),
        (
            "TEXT_PRMS",
            "x",
            "y",
            1,
            "band",
            26904,
            True,
            "get_tiff_text",
            "get_gdf",
            "fid",
        ),
    ],
)
def test_cat_tiff_intersectio_p(
    vn: str,
    xn: str,
    yn: str,
    bd: int,
    bn: str,
    crs: Any,
    cat: bool,
    ds: str,
    gdf: str,
    fid: str,
    request: FixtureRequest,
) -> None:
    """Test tiff intersection function."""
    data = UserTiffData(
        var=vn,
        ds=request.getfixturevalue(ds),
        proj_ds=crs,
        x_coord=xn,
        y_coord=yn,
        bname=bn,
        band=bd,
        f_feature=request.getfixturevalue(gdf),
        id_feature=fid,
        proj_feature=crs,
    )
    tmpdir = TemporaryDirectory()
    zonal_gen = ZonalGen(
        user_data=data,
        zonal_engine="parallel",
        zonal_writer="csv",
        out_path=tmpdir.name,
        file_prefix="tmpzonal",
    )
    stats = zonal_gen.calculate_zonal(categorical=cat)

    assert isinstance(stats, pd.DataFrame)
    file = Path(tmpdir.name) / "tmpzonal.csv"
    assert file.exists()


@pytest.mark.parametrize(
    "vn,xn,yn,bd,bn,crs,cat,ds,gdf,fid",
    [
        (
            "slope",
            "x",
            "y",
            1,
            "band",
            26904,
            False,
            "get_tiff_slope",
            "get_gdf",
            "fid",
        ),
        (
            "TEXT_PRMS",
            "x",
            "y",
            1,
            "band",
            26904,
            True,
            "get_tiff_text",
            "get_gdf",
            "fid",
        ),
    ],
)
def test_cat_tiff_intersectio_d(
    vn: str,
    xn: str,
    yn: str,
    bd: int,
    bn: str,
    crs: Any,
    cat: bool,
    ds: str,
    gdf: str,
    fid: str,
    request: FixtureRequest,
) -> None:
    """Test tiff intersection function."""
    with get_dask_client() as _client:  # noqa

        data = UserTiffData(
            var=vn,
            ds=request.getfixturevalue(ds),
            proj_ds=crs,
            x_coord=xn,
            y_coord=yn,
            bname=bn,
            band=bd,
            f_feature=request.getfixturevalue(gdf),
            id_feature=fid,
            proj_feature=crs,
        )
        tmpdir = TemporaryDirectory()
        zonal_gen = ZonalGen(
            user_data=data,
            zonal_engine="dask",
            zonal_writer="csv",
            out_path=tmpdir.name,
            file_prefix="tmpzonal",
            jobs=4,
        )
        stats = zonal_gen.calculate_zonal(categorical=cat)

        assert isinstance(stats, pd.DataFrame)
        file = Path(tmpdir.name) / "tmpzonal.csv"
        assert file.exists()
