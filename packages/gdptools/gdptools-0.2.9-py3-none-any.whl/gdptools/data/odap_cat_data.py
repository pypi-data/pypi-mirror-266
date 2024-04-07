"""OpenDAP Catalog Data classes."""
from __future__ import annotations

from typing import Optional
from typing import Tuple

import numpy as np
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


class CatParams(BaseModel):
    """Class representing elements of Mike Johnsons OpenDAP catalog params.

    https://mikejohnson51.github.io/opendap.catalog/cat_params.json
    """

    id: Optional[str] = None
    URL: str
    grid_id: Optional[int] = -1
    variable: Optional[str] = None
    varname: str
    long_name: Optional[str] = ...  # type: ignore
    T_name: Optional[str] = ...  # type: ignore
    duration: Optional[str] = None
    units: Optional[str] = ...  # type: ignore
    interval: Optional[str] = None
    nT: Optional[int] = 0  # noqa
    tiled: Optional[str] = None
    model: Optional[str] = None
    ensemble: Optional[str] = None
    scenario: Optional[str] = None

    @validator("grid_id", pre=True, always=True)
    def set_grid_id(cls, v: int) -> int:  # noqa:
        """Convert to int."""
        return v

    @validator("nT", pre=True, always=False)
    def set_nt(cls, v: int) -> int:  # noqa:
        """Convert to int."""
        return 0 if np.isnan(v) else v


class CatGrids(BaseModel):
    """Class representing elements of Mike Johnsons OpenDAP catalog grids.

    https://mikejohnson51.github.io/opendap.catalog/cat_grids.json
    """

    grid_id: Optional[int] = None
    X_name: str
    Y_name: str
    X1: Optional[float] = None
    Xn: Optional[float] = None
    Y1: Optional[float] = None
    Yn: Optional[float] = None
    resX: Optional[float] = None  # noqa
    resY: Optional[float] = None  # noqa
    ncols: Optional[int] = None
    nrows: Optional[int] = None
    proj: str
    toptobottom: int
    tile: Optional[str] = None
    grid_id_1: Optional[str] = Field(None, alias="grid.id")

    @validator("toptobottom", pre=True, always=True)
    def get_toptobottom(cls, v: int) -> int:  # noqa:
        """Convert str to int."""
        return v


class CatClimRItem(BaseModel):
    """Mike Johnson's CatClimRItem class.

    Source data from which this is derived comes from:
        'https://mikejohnson51.github.io/climateR-catalogs/catalog.json'
    """

    id: str
    asset: Optional[str] = None
    URL: str
    varname: str
    variable: Optional[str] = None
    description: Optional[str] = None
    units: Optional[str] = None
    model: Optional[str] = None
    ensemble: Optional[str] = None
    scenario: Optional[str] = None
    T_name: Optional[str] = None
    duration: Optional[str] = None
    interval: Optional[str] = None
    nT: Optional[int] = 0  # noqa
    X_name: str  # noqa
    Y_name: str  # noqa
    X1: float
    Xn: float
    Y1: float
    Yn: float
    resX: float  # noqa
    resY: float  # noqa
    ncols: int
    nrows: int
    crs: str
    toptobottom: str
    tiled: Optional[str] = None

    @validator("crs")
    @classmethod
    def _default_crs(cls, val: str) -> str:
        """Sets to a default CRS if none is provided."""
        if val is None or not val:
            return "EPSG:4326"
        return val

    @validator("toptobottom", always=False)
    @classmethod
    def _toptobottom_as_bool(cls, val: str) -> bool:
        """Convert to python boolean type."""
        return val.upper() == "TRUE"  # type: ignore

    @validator("tiled", always=False)
    @classmethod
    def _tiled(cls, val: str) -> str:
        """Must be one of just a few options.  Returns NA if left blank."""
        if val.upper() not in ["", "NA", "T", "XY"]:
            raise ValueError("tiled must be one of ['', 'NA', 'T', 'XY']")
        if val == "":
            return "NA"
        return val.upper()

    class Config:
        """interior class to direct pydantic's behavior."""

        anystr_strip_whitespace = True
        allow_mutations = False


def climr_to_odap(climr: CatClimRItem) -> Tuple[CatParams, CatGrids]:
    """Convert a CatClimRItem to a CatParams and CatGrids object.

    Parameters
    ----------
    climr : CatClimRItem
        The CatClimRItem object to convert.

    Returns
    -------
    CatParams, CatGrids
        The CatParams and CatGrids objects.

    """
    params = CatParams(
        id=climr.id,
        URL=climr.URL,
        grid_id=0,
        variable=climr.variable,
        varname=climr.varname,
        long_name=climr.description,
        T_name=climr.T_name,
        duration=climr.duration,
        units=climr.units,
        interval=climr.interval,
        nT=climr.nT,
        tiled=climr.tiled,
        model=climr.model,
        ensemble=climr.ensemble,
        scenario=climr.scenario,
    )
    grids = CatGrids(
        X_name=climr.X_name,
        Y_name=climr.Y_name,
        X1=climr.X1,
        Xn=climr.Xn,
        Y1=climr.Y1,
        Yn=climr.Yn,
        resX=climr.resX,
        resY=climr.resY,
        ncols=climr.ncols,
        nrows=climr.nrows,
        proj=climr.crs,
        toptobottom=climr.toptobottom,
        tile=climr.tiled,
    )
    return params, grids
