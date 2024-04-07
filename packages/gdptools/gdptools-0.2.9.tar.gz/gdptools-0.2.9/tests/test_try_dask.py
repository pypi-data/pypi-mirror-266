import geopandas as gpd
import dask_geopandas as dgpd
import pandas as pd
import os
from dask.distributed import Client, LocalCluster
from gdptools import AggGen
from gdptools import ClimRCatData
from gdptools import UserCatData
from gdptools import WeightGen
from typing import Any
from tempfile import NamedTemporaryFile
import numpy as np

gm_vars = ["tmmn", "tmmx", "pr"]

def convert_int64_columns(df):
    """
    Convert all Int64 columns in the DataFrame to object dtype with Python ints.
    Note: This will lose the ability to have NaN values in these columns.
    """
    for col in df.columns:
        # Check for Pandas nullable integer type
        if pd.api.types.is_integer_dtype(df[col]) and pd.api.types.is_extension_array_dtype(df[col]):
            # Convert to Python int, handling NaN values by converting them to None
            df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) else None).astype('object')
    return df

def climr_dict(vars: list[str] = gm_vars) -> dict[str, Any]:
    """Return parameter json."""
    climater_cat = "https://mikejohnson51.github.io/climateR-catalogs/catalog.parquet"
    cat = pd.read_parquet(climater_cat)

    _id = "gridmet"  # noqa
    var_params = [
        cat.query("id == @_id & variable == @_var", local_dict={"_id": _id, "_var": _var}).to_dict(orient="records")[0]
        for _var in vars
    ]
    return dict(zip(vars, var_params))  # noqa B905

def get_gdf() -> gpd.GeoDataFrame:
    """Create GeoDataFrame."""
    gdf = gpd.read_file("./tests/data/DRB/DRB_4326.shp")
    gdf = gdf.convert_dtypes()
    print(gdf.dtypes)
    ngdf = convert_int64_columns(gdf)
    print(ngdf.dtypes)
    return ngdf



def main():
    data_crs = 4326
    x_coord = "lon"
    y_coord = "lat"
    t_coord = "time"
    sdate = "2021-01-01"
    edate = "2021-01-31"
    var = ["Tair"]
    shp_crs = 4326
    shp_poly_idx = "huc12"
    wght_gen_crs = 6931

    cluster = LocalCluster(n_workers=1)
    client = Client(cluster)  # type: ignore

    user_data = ClimRCatData(
        cat_dict=climr_dict(),
        f_feature=get_gdf(),
        id_feature=shp_poly_idx,
        period=[sdate, edate],
    )
    print(user_data)
    tempfile = NamedTemporaryFile()
    wght_gen = WeightGen(
        user_data=user_data,
        method="dask",
        output_file=tempfile.name,  # type: ignore
        weight_gen_crs=wght_gen_crs,
    )
    _wghts = wght_gen.calculate_weights()
    cluster.close()
    client.close()
    
if __name__ == "__main__":
    main()