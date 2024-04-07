"""Test WghtGen and AggGen classes."""

import gc
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from typing import Any

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pandas as pd
import pytest
import xarray as xr
from pandas.testing import assert_frame_equal

from gdptools import AggGen
from gdptools import InterpGen
from gdptools import ODAPCatData
from gdptools import UserCatData
from gdptools import WeightGen

gm_vars = ["aet", "pet", "PDSI"]


@pytest.fixture
def aet_ma_mean() -> npt.NDArray[np.double]:
    """Test values for masked-mean calculation."""
    return np.asarray(
        [
            [3.1605408],
            [0.0121277],
            [41.983784],
            [68.91504],
            [81.72351],
            [92.60617],
            [48.96107],
            [37.30392],
            [27.883911],
            [64.65818],
            [52.897045],
            [1.6390916],
        ]
    )


@pytest.fixture
def aet_mean() -> npt.NDArray[np.double]:
    """Test values for mean calculation."""
    return np.asarray(
        [
            [3.1551743],
            [0.0121071],
            [41.9124973],
            [68.7980207],
            [81.5847434],
            [92.4489252],
            [48.8779355],
            [37.2405776],
            [27.8365651],
            [64.5483926],
            [52.8072282],
            [1.63630845],
        ]
    )


@pytest.fixture
def aet_nan_mean() -> npt.NDArray[np.double]:
    """Test values for mean calculation."""
    return np.asarray(
        [
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
            [9.969209968386869e36],
        ]
    )


@pytest.fixture(scope="function")
def param_dict(vars: list[str] = gm_vars) -> dict[str, Any]:
    """Return parameter json."""
    cat_params = "https://mikejohnson51.github.io/opendap.catalog/cat_params.json"
    params = pd.read_json(cat_params)
    _id = "terraclim"  # noqa
    var_params = [
        params.query("id == @_id & variable == @_var", local_dict={"_id": _id, "_var": _var}).to_dict(orient="records")[
            0
        ]
        for _var in vars
    ]
    data = dict(zip(vars, var_params))  # noqa B905
    yield data
    del data
    gc.collect()


@pytest.fixture(scope="function")
def grid_dict(vars: list[str] = gm_vars) -> dict[str, Any]:
    """Return grid json."""
    cat_grid = "https://mikejohnson51.github.io/opendap.catalog/cat_grids.json"
    grids = pd.read_json(cat_grid)
    _gridid = 116  # noqa
    var_grid = [
        grids.query("grid_id == @_gridid", local_dict={"_gridid": _gridid, "_var": _var}).to_dict(orient="records")[0]
        for _var in vars
    ]
    data = dict(zip(vars, var_grid))  # noqa B905
    yield data
    del data
    gc.collect()


@pytest.fixture(scope="function")
def gdf() -> gpd.GeoDataFrame:
    """Create xarray dataset."""
    gdf = gpd.read_file("./tests/data/hru_1210_epsg5070.shp")
    yield gdf
    del gdf
    gc.collect()


@pytest.fixture
def poly_idx() -> str:
    """Return poly_idx."""
    return "hru_id_nat"


@pytest.fixture
def wght_gen_proj() -> int:
    """Return wght gen projection."""
    return 6931


def test_odapcatdata_dask_weights_w_intersections(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    from dask.distributed import Client, LocalCluster

    cluster = LocalCluster(n_workers=os.cpu_count())
    client = Client(cluster)  # type: ignore
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="dask",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights(intersections=True)  # noqa: F841

    client.close()  # type: ignore
    del client
    cluster.close()  # type: ignore
    del cluster

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="parallel",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    print(nvals["aet"].values)
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)  # type: ignore

    tmpdir2 = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="serial",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals2 = gen_agg.calculate_agg()
    file = Path(tmpdir2.name) / "test_agg_gen.csv"
    assert file.exists()
    np.testing.assert_allclose(aet_nan_mean, nvals2["aet"].values, rtol=1e-4, verbose=True)


def test_odapcatdata_masked_mean_dask(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    from dask.distributed import Client, LocalCluster

    cluster = LocalCluster(n_workers=os.cpu_count())
    client = Client(cluster)  # type: ignore
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="dask",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights()  # noqa: F841

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="dask",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)
    client.close()  # type: ignore
    del client
    cluster.close()  # type: ignore
    del cluster


def test_odapcatdata_masked_mean_p(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="parallel",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights()  # noqa: F841

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="parallel",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)


def test_odapcatdata_masked_mean_s(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="serial",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights()  # noqa: F841

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="serial",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)


def test_odapcatdata_d(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    from dask.distributed import Client, LocalCluster

    cluster = LocalCluster(n_workers=os.cpu_count())
    client = Client(cluster)  # type: ignore
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="dask",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights()  # noqa: F841

    client.close()  # type: ignore
    del client
    cluster.close()  # type: ignore
    del cluster

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="parallel",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)

    tmpdir2 = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="serial",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen",
    )

    # test_arr = np.asarray(
    #     [
    #         [3.1551743],
    #         [0.0121071],
    #         [41.9124973],
    #         [68.7980207],
    #         [81.5847434],
    #         [92.4489252],
    #         [48.8779355],
    #         [37.2405776],
    #         [27.8365651],
    #         [64.5483926],
    #         [52.8072282],
    #         [1.63630845],
    #     ]
    # )
    _ngdf, nvals2 = gen_agg.calculate_agg()
    file = Path(tmpdir2.name) / "test_agg_gen.csv"
    assert file.exists()
    np.testing.assert_allclose(aet_nan_mean, nvals2["aet"].values, rtol=1e-4, verbose=True)


def test_odapcatdata_parallel_w_intersections(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="parallel",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights(intersections=True)  # noqa: F841

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="parallel",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)

    tmpdir2 = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="parallel",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals2 = gen_agg.calculate_agg()
    file = Path(tmpdir2.name) / "test_agg_gen.csv"
    assert file.exists()
    np.testing.assert_allclose(aet_nan_mean, nvals2["aet"].values, rtol=1e-4, verbose=True)


def test_odapcatdata_p(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="parallel",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights()  # noqa: F841

    tmpdir = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="parallel",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()

    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)

    tmpdir2 = TemporaryDirectory()
    gen_agg = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="parallel",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals2 = gen_agg.calculate_agg()
    file = Path(tmpdir2.name) / "test_agg_gen.csv"
    assert file.exists()
    np.testing.assert_allclose(aet_nan_mean, nvals2["aet"].values, rtol=1e-4, verbose=True)


def test_odapcatdata_serial_with_intersections(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="serial",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights(intersections=True)  # noqa: F841

    tmpdir = TemporaryDirectory()

    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="serial",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)

    tmpdir2 = TemporaryDirectory()
    gen_agg2 = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="serial",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen2",
    )

    _ngdf2, nvals2 = gen_agg2.calculate_agg()
    np.testing.assert_allclose(aet_ma_mean, nvals2["aet"].values, rtol=1e-4, verbose=True)

    tmpdir3 = TemporaryDirectory()
    gen_agg3 = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="serial",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir3.name,
        file_prefix="test_agg_gen3",
    )

    _ngdf3, nvals3 = gen_agg3.calculate_agg()
    np.testing.assert_allclose(aet_nan_mean, nvals3["aet"].values, rtol=1e-4, verbose=True)

    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()
    file2 = Path(tmpdir2.name) / "test_agg_gen2.csv"
    assert file2.exists()
    file3 = Path(tmpdir3.name) / "test_agg_gen3.csv"
    assert file3.exists()


def test_odapcatdata_s(
    param_dict: dict[str, Any],
    grid_dict: dict[str, Any],
    gdf: gpd.GeoDataFrame,
    poly_idx: str,
    wght_gen_proj: Any,
    aet_ma_mean: npt.NDArray[np.double],
    aet_nan_mean: npt.NDArray[np.double],
) -> None:
    """Test ODAPCatData."""
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=gdf,
        id_feature=poly_idx,
        period=["1980-01-01", "1980-12-31"],
    )
    tmpfile = NamedTemporaryFile()

    gen_weights = WeightGen(
        user_data=user_data,
        method="serial",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_proj,
    )

    _wghts = gen_weights.calculate_weights()  # noqa: F841

    tmpdir = TemporaryDirectory()

    gen_agg = AggGen(
        user_data=user_data,
        stat_method="masked_mean",
        agg_engine="serial",
        agg_writer="netcdf",
        weights=tmpfile.name,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen",
    )

    _ngdf, nvals = gen_agg.calculate_agg()
    np.testing.assert_allclose(aet_ma_mean, nvals["aet"].values, rtol=1e-4, verbose=True)

    tmpdir2 = TemporaryDirectory()
    gen_agg2 = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="serial",
        agg_writer="csv",
        weights=tmpfile.name,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen2",
    )

    _ngdf2, nvals2 = gen_agg2.calculate_agg()
    np.testing.assert_allclose(aet_nan_mean, nvals2["aet"].values, rtol=1e-4, verbose=True)

    tmpdir3 = TemporaryDirectory()
    gen_agg3 = AggGen(
        user_data=user_data,
        stat_method="mean",
        agg_engine="serial",
        agg_writer="parquet",
        weights=tmpfile.name,
        out_path=tmpdir3.name,
        file_prefix="test_agg_gen3",
    )

    _ngdf3, nvals3 = gen_agg3.calculate_agg()
    np.testing.assert_allclose(aet_nan_mean, nvals3["aet"].values, rtol=1e-4, verbose=True)

    file = Path(tmpdir.name) / "test_agg_gen.nc"
    assert file.exists()
    file2 = Path(tmpdir2.name) / "test_agg_gen2.csv"
    assert file2.exists()
    file3 = Path(tmpdir3.name) / "test_agg_gen3.parquet.gzip"
    assert file3.exists()

    pq = pd.read_parquet(file3)
    assert isinstance(pq, pd.DataFrame)


@pytest.fixture(scope="function")
def get_gdf() -> gpd.GeoDataFrame:
    """Create GeoDataFrame."""
    gdf = gpd.read_file("./tests/data/hru_1210_epsg5070.shp")
    yield gdf
    del gdf
    gc.collect()


@pytest.fixture(scope="function")
def get_xarray() -> xr.Dataset:
    """Create xarray Dataset."""
    # return xr.open_dataset("./tests/data/cape_cod_tmax.nc")
    ds = xr.open_mfdataset(
        [
            "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_tmmx_1979_CurrentYear_CONUS.nc",
            "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_tmmn_1979_CurrentYear_CONUS.nc",
        ]
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


data_crs = 4326  # "crs84"
x_coord = "lon"
y_coord = "lat"
t_coord = "day"
sdate = "1979-01-01"
edate = "1979-01-07"
tvar = ["daily_maximum_temperature", "daily_minimum_temperature"]
shp_crs = 5070
shp_poly_idx = "hru_id_nat"
wght_gen_crs = 6931


def test_weightgen_nofile(get_xarray: xr.Dataset, get_gdf: gpd.GeoDataFrame) -> None:
    """Test WeightGen."""
    user_data = UserCatData(
        ds=get_xarray,
        proj_ds=data_crs,
        x_coord=x_coord,
        y_coord=y_coord,
        t_coord=t_coord,
        var=tvar,
        f_feature=get_gdf,
        proj_feature=shp_crs,
        id_feature=shp_poly_idx,
        period=[sdate, edate],
    )

    wghtgen1 = WeightGen(
        user_data=user_data,
        method="serial",
        output_file=None,
        weight_gen_crs=wght_gen_crs,
    )

    wghts1 = wghtgen1.calculate_weights()

    wghtgen2 = WeightGen(
        user_data=user_data,
        method="serial",
        weight_gen_crs=wght_gen_crs,
    )

    wghts2 = wghtgen2.calculate_weights()

    assert_frame_equal(wghts1, wghts2)

    wghtgen3 = WeightGen(
        user_data=user_data,
        method="serial",
        weight_gen_crs=wght_gen_crs,
        output_file="",
    )

    wghts3 = wghtgen3.calculate_weights()
    assert_frame_equal(wghts1, wghts3)


def test_usercatdata(
    get_xarray: xr.Dataset,
    get_gdf: gpd.GeoDataFrame,
    get_file_path: Path,
    get_out_path: Path,
) -> None:
    """Test UserCatData."""
    user_data = UserCatData(
        ds=get_xarray,
        proj_ds=data_crs,
        x_coord=x_coord,
        y_coord=y_coord,
        t_coord=t_coord,
        var=tvar,
        f_feature=get_gdf,
        proj_feature=shp_crs,
        id_feature=shp_poly_idx,
        period=[sdate, edate],
    )

    tmpfile = NamedTemporaryFile()
    weight_gen = WeightGen(
        user_data=user_data,
        method="serial",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_crs,
    )

    wghts = weight_gen.calculate_weights()

    user_data2 = UserCatData(
        ds=get_xarray,
        proj_ds=data_crs,
        x_coord=x_coord,
        y_coord=y_coord,
        t_coord=t_coord,
        var=tvar,
        f_feature=get_gdf,
        proj_feature=shp_crs,
        id_feature=shp_poly_idx,
        period=[sdate, edate],
    )

    weight_gen2 = WeightGen(
        user_data=user_data2,
        method="parallel",
        output_file=tmpfile.name,
        weight_gen_crs=wght_gen_crs,
    )

    _wghts2 = weight_gen2.calculate_weights()  # noqa: F841

    tmpdir = TemporaryDirectory()

    agg_gen = AggGen(
        user_data=user_data2,
        stat_method="mean",
        agg_engine="serial",
        agg_writer="csv",
        weights=_wghts2,
        out_path=tmpdir.name,
        file_prefix="test_agg_gen_2",
    )

    _ngdf, _nvals = agg_gen.calculate_agg()

    user_data3 = UserCatData(
        ds=get_xarray,
        proj_ds=data_crs,
        x_coord=x_coord,
        y_coord=y_coord,
        t_coord=t_coord,
        var=tvar,
        f_feature=get_gdf,
        proj_feature=shp_crs,
        id_feature=shp_poly_idx,
        period=[sdate, edate],
    )
    tmpdir2 = TemporaryDirectory()
    agg_gen = AggGen(
        user_data=user_data3,
        stat_method="masked_mean",
        agg_engine="serial",
        agg_writer="netcdf",
        weights=wghts,
        out_path=tmpdir2.name,
        file_prefix="test_agg_gen_3",
    )

    _ngdf, _nvals = agg_gen.calculate_agg()

    outfile = Path(tmpdir.name) / "test_agg_gen_2.csv"

    assert outfile.exists()


def test_interp_gen1(param_dict: dict[str, Any], grid_dict: dict[str, Any]) -> None:
    """Test InterpGen: uses the linear interpolation method and the actual line points."""
    lines = gpd.read_file("./tests/data/test_lines.json")
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=lines,
        id_feature="Permanent_Identifier",
        period=["1980-10-01", "1980-10-01"],
    )

    interp_object = InterpGen(user_data, pt_spacing=0, stat="all")

    stats, pts = interp_object.calc_interp()
    assert isinstance(stats, pd.DataFrame)
    assert isinstance(pts, gpd.GeoDataFrame)

    stats = stats[
        (stats["date"] == "1980-10-01") & (stats["Permanent_Identifier"] == "154309038") & (stats["varname"] == "aet")
    ]
    assert stats["mean"][0] == pytest.approx(69.00008241663909, 0.001)
    assert stats["median"][0] == pytest.approx(69.15048144396194, 0.001)
    assert stats["std"][0] == pytest.approx(0.27313941052443974, 0.001)
    assert stats["max"][0] == pytest.approx(69.32388703205886, 0.001)
    assert stats["min"][0] == pytest.approx(68.44079220210928, 0.001)

    pts = pts.loc["1980-10-01"][
        (pts.loc["1980-10-01"]["Permanent_Identifier"] == "154309038") & (pts.loc["1980-10-01"]["varname"] == "aet")
    ]

    assert pts.loc[[0]]["values"][0] == pytest.approx(68.44079220210928, 0.001)
    assert pts.loc[[1]]["dist"][1] == pytest.approx(289.32728745613946, 0.001)
    assert pts.loc[[1]]["geometry"][1].coords[0][0] == pytest.approx(-91.35084136864555, 0.001)
    assert pts.loc[[1]]["geometry"][1].coords[0][1] == pytest.approx(41.427423069029714, 0.001)


def test_interp_gen2(param_dict: dict[str, Any], grid_dict: dict[str, Any]) -> None:
    """Test InterpGen: uses the nearest interpolation method and 100 meter point spacing."""
    lines = gpd.read_file("./tests/data/test_lines.json")
    user_data = ODAPCatData(
        param_dict=param_dict,
        grid_dict=grid_dict,
        f_feature=lines,
        id_feature="Permanent_Identifier",
        period=["1980-10-01", "1980-10-01"],
    )

    interp_object = InterpGen(user_data, pt_spacing=100, interp_method="nearest", stat="all")

    stats, pts = interp_object.calc_interp()
    assert isinstance(stats, pd.DataFrame)
    assert isinstance(pts, gpd.GeoDataFrame)

    stats = stats[
        (stats["date"] == "1980-10-01") & (stats["Permanent_Identifier"] == "154309038") & (stats["varname"] == "aet")
    ]
    assert stats["mean"][0] == pytest.approx(68.774811, 0.001)
    assert stats["median"][0] == pytest.approx(68.700005, 0.001)
    assert stats["std"][0] == pytest.approx(0.360310, 0.001)
    assert stats["max"][0] == pytest.approx(69.599998, 0.001)
    assert stats["min"][0] == pytest.approx(68.400002, 0.001)

    pts = pts.loc["1980-10-01"][
        (pts.loc["1980-10-01"]["Permanent_Identifier"] == "154309038") & (pts.loc["1980-10-01"]["varname"] == "aet")
    ]

    assert pts.loc[[100]]["values"][100] == pytest.approx(68.599998, 0.001)
    assert pts.loc[[100]]["dist"][100] == pytest.approx(10000.0, 0.001)
    assert pts.loc[[100]]["geometry"][100].coords[0][0] == pytest.approx(-91.37240021855973, 0.001)
    assert pts.loc[[100]]["geometry"][100].coords[0][1] == pytest.approx(41.33930149089651, 0.001)
