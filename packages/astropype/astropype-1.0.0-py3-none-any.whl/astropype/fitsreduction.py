
import os
import numpy as np
from pathlib import Path
from typing import Any
from scipy import ndimage
from astropy.io import fits
from .decorator import timeit
from multiprocessing import Pool
from .funcs import (
    init_pool,
    subtract_func,
    divide_func,
    rotate_func,
    crop_func,
    overscan_func,
    bin_func,
)


@timeit
def subtractfits(__files: list[Path], __file: Path, prefix: str = "s") -> list[Path]:
    print(f"subtracting {__file} from:")
    kwargs = {"reference_file": __file, "prefix": prefix, "func": subtract_func}
    return init_pool(__files, kwargs)


@timeit
def dividefits(__files: list[Path], __file: Path, prefix: str = "d") -> list[Path]:
    print(f"dividing {__file} from:")
    kwargs = {"reference_file": __file, "prefix": prefix, "func": divide_func}
    return init_pool(__files, kwargs)


@timeit
def rotatefits(__files: list[Path], prefix: str = "r") -> list[Path]:
    print(f"rotating frames ...")
    kwargs = {"prefix": prefix, "func": rotate_func}
    return init_pool(__files, kwargs)


@timeit
def cropfits(__files: list[Path], prefix: str = "c"):
    print(f"cropping overscan region ...")
    kwargs = {"prefix": prefix, "func": crop_func}
    return init_pool(__files, kwargs)


@timeit
def subtract_overscan(__files: list[Path], prefix: str = "o"):
    print(f"subtracting individual overscans ...")
    kwargs = {"prefix": prefix, "func": overscan_func}
    return init_pool(__files, kwargs)

@timeit
def binfits(__files : list[Path], bin_factor : int, bin_method : str = "sum", 
            consider_nans : bool = False, prefix : str = "b"):
    print(f"binning images by a factor of {bin_factor} ...")
    kwargs = {"prefix" : f"{prefix}{bin_factor}", "func" : bin_func, "bin_factor" : bin_factor,
              "bin_method" : bin_method , "consider_nans" : consider_nans}
    return init_pool(__files,kwargs)
    
