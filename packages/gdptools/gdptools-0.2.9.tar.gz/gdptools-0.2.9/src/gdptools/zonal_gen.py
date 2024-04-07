"""Calculate zonal methods."""
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Union

import pandas as pd

from gdptools.agg.zonal_engines import ZonalEngineDask
from gdptools.agg.zonal_engines import ZonalEngineParallel
from gdptools.agg.zonal_engines import ZonalEngineSerial
from gdptools.data.user_data import UserData

ZONAL_ENGINES = Literal["serial", "parallel", "dask"]
"""
Literal type alias for the zonal engines.

Options:
- "serial": Perform zonal calculations in a serial manner.
- "parallel": Perform zonal calculations in parallel.
- "dask": Perform zonal calculations using Dask for distributed computing.
"""

ZONAL_WRITERS = Literal["csv"]
"""
Literal type alias for the zonal writers.

Options:
- "csv": Write zonal statistics to a CSV file.
"""


class ZonalGen:
    """Class for aggregating zonal statistics."""

    def __init__(
        self,
        user_data: UserData,
        zonal_engine: ZONAL_ENGINES,
        zonal_writer: ZONAL_WRITERS,
        out_path: str,
        file_prefix: str,
        append_date: bool = False,
        jobs: int = 1,
    ) -> None:
        """__init__ Initialize ZonalGen class.

        _extended_summary_

        Args:
            user_data (UserData): One of :class:`UserTiffData`
            zonal_engine (ZONAL_ENGINES): _description_
            zonal_writer (ZONAL_WRITERS): _description_
            out_path (str): _description_
            file_prefix (str): _description_
            append_date (bool): _description_. Defaults to False.
            jobs (int): _description_. Defaults to 1.

        Raises:
            FileNotFoundError: _description_
            TypeError: _description_
        """
        self._user_data = user_data
        self._zonal_engine = zonal_engine
        self._zonal_writer = zonal_writer
        self._jobs = jobs
        self._out_path = Path(out_path)
        if not self._out_path.exists():
            raise FileNotFoundError(f"Path: {self._out_path} does not exist")
        self._file_prefix = file_prefix
        self._append_date = append_date
        if self._append_date:
            self._fdate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            self._fname = f"{self._fdate}_{self._file_prefix}"
        else:
            self._fname = f"{self._file_prefix}"
        self.agg: Union[ZonalEngineSerial, ZonalEngineParallel, ZonalEngineDask]
        if self._zonal_engine == "serial":
            self.agg = ZonalEngineSerial()
        elif self._zonal_engine == "parallel":
            self.agg = ZonalEngineParallel()
        elif self._zonal_engine == "dask":
            self.agg = ZonalEngineDask()
        else:
            raise TypeError(f"agg_engine: {self._zonal_engine} not in {ZONAL_ENGINES}")

    def calculate_zonal(self, categorical: bool = False) -> pd.DataFrame:
        """calculate_zonal Calculates zonal statistics.

        _extended_summary_

        Args:
            categorical (bool): _description_. Defaults to False.

        Returns:
            pd.DataFrame: _description_
        """
        tstrt = time.perf_counter()
        stats = self.agg.calc_zonal_from_aggdata(user_data=self._user_data, categorical=categorical, jobs=self._jobs)
        if self._zonal_writer == "csv":
            fullpath = self._out_path / f"{self._fname}.csv"
            stats.to_csv(fullpath, sep=",")
        tend = time.perf_counter()
        print(f"Total time for serial zonal stats calculation {tend - tstrt:0.4f} seconds")
        return stats
        # elif self._zonal_writer == "feather":
        #     fullpath = self._out_path / f"{self._fname}"
        #     stats.to_feather(path=fullpath, )


class WeightedZonalGen:
    """Class for aggregating weighted zonal statistics."""

    def __init__(
        self,
        user_data: UserData,
        weight_gen_crs: Any,
        zonal_engine: ZONAL_ENGINES,
        zonal_writer: ZONAL_WRITERS,
        out_path: str,
        file_prefix: str,
        append_date: bool = False,
        jobs: int = 1,
    ) -> None:
        """Initializes a ZonalGen object.

        Args:
            user_data: The user data.
            weight_gen_crs: The weight generation CRS.
            zonal_engine: The zonal engine to use.
            zonal_writer: The zonal writer to use.
            out_path: The output path.
            file_prefix: The file prefix.
            append_date: Whether to append the date to the file name. Defaults to False.
            jobs: The number of jobs to use. Defaults to 1.

        Raises:
            FileNotFoundError: If the output path does not exist.
            TypeError: If the zonal engine is not one of the supported engines.

        Examples:
            >>> zonal_gen = ZonalGen(
                user_data,
                weight_gen_crs,
                ZONAL_ENGINES.PARALLEL,
                ZONAL_WRITERS.CSV,
                "/path/to/output",
                "data",
                append_date=True,
                jobs=4)
        """
        self._user_data = user_data
        self._weight_gen_crs = weight_gen_crs
        self._zonal_engine = zonal_engine
        self._zonal_writer = zonal_writer
        self._jobs = jobs
        self._out_path = Path(out_path)
        if not self._out_path.exists():
            raise FileNotFoundError(f"Path: {self._out_path} does not exist")
        self._file_prefix = file_prefix
        self._append_date = append_date
        if self._append_date:
            self._fdate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            self._fname = f"{self._fdate}_{self._file_prefix}"
        else:
            self._fname = f"{self._file_prefix}"
        self.agg: Union[ZonalEngineSerial, ZonalEngineParallel, ZonalEngineDask]
        if self._zonal_engine == "serial":
            self.agg = ZonalEngineSerial()
        elif self._zonal_engine == "parallel":
            self.agg = ZonalEngineParallel()
        elif self._zonal_engine == "dask":
            self.agg = ZonalEngineDask()
        else:
            raise TypeError(f"agg_engine: {self._zonal_engine} not in {ZONAL_ENGINES}")

    def calculate_weighted_zonal(self, categorical: bool = False) -> pd.DataFrame:
        """calculate_zonal Calculates zonal statistics.

        _extended_summary_

        Args:
            categorical (bool): _description_. Defaults to False.

        Returns:
            pd.DataFrame: _description_
        """
        tstrt = time.perf_counter()
        stats = self.agg.calc_weights_zonal_from_aggdata(
            user_data=self._user_data, crs=self._weight_gen_crs, categorical=categorical, jobs=self._jobs
        )
        if self._zonal_writer == "csv":
            fullpath = self._out_path / f"{self._fname}.csv"
            stats.to_csv(fullpath, sep=",")
        tend = time.perf_counter()
        print(f"Total time for serial zonal stats calculation {tend - tstrt:0.4f} seconds")
        return stats
        # elif self._zonal_writer == "feather":
        #     fullpath = self._out_path / f"{self._fname}"
        #     stats.to_feather(path=fullpath, )
