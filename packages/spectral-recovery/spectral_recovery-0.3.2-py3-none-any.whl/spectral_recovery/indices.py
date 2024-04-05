"""Methods for computing spectral indices.

Most functions are decorated with `compatible_with` and `requires_bands` decorators, 
which check that the input stack is compatible with the function and that the stack
contains the required bands.

Most notably, exports the `compute_indices` function, which computes a stack of
spectral indices from a stack of images and str of index names.

"""

import functools
from typing import List

import xarray as xr
from pandas import Index as pdIndex

import spyndex as spx

from spectral_recovery._utils import maintain_rio_attrs
from spectral_recovery._config import SUPPORTED_DOMAINS


@maintain_rio_attrs
def compute_indices(
    image_stack: xr.DataArray, indices: list[str], constants: dict = {}, **kwargs
):
    """Compute spectral indices using the spyndex package.


    Parameters
    ----------
    image_stack : xr.DataArray
        stack of images.
    indices : list of str
        list of spectral indices to compute
    constants : dict of flt
        constant and value pairs e.g {"L": 0.5}
    kwargs : dict, optional
        Additional kwargs for wrapped spyndex.computeIndex function.

    Returns
    -------jmk,
        xr.DataArray: stack of images with spectral indices stacked along
        the band dimension.

    """
    if _supported_domain(indices):
        params_dict = _build_params_dict(image_stack)
        params_dict = params_dict | constants | kwargs
        index_stack = spx.computeIndex(index=indices, params=params_dict)
        try:
            # rename 'index' dim to 'bands' to match tool's expected dims
            index_stack = index_stack.rename({"index": "band"})
        except ValueError:
            # computeIndex will not return an index dim if only 1 index passed
            index_stack = index_stack.expand_dims(dim={"band": indices})
    return index_stack


def _supported_domain(indices: list[str]):
    """Determine whether indices application domains are supported by tool.

    Parameters
    ----------
    indices : list of str
        list of indices

    Raises
    ------
    ValueError
        If any index has an unsupported application domain.
    """
    for i in indices:
        if spx.indices[i].application_domain not in SUPPORTED_DOMAINS:
            raise ValueError(
                "only application domain 'vegetation' and 'burn' are supported (index"
                f" {i} has application domain '{spx.indices[i].application_domain}')"
            ) from None
    return True


def _build_params_dict(image_stack: xr.DataArray):
    """Build dict of standard names and slices required by computeIndex.

    Slices will be taken along the band dimension of image_stack,
    selecting for each of the standard band/constant names that computeIndex
    accepts. Any name that is not in image_stack will not be included
    in the dictionary.

    Parameters
    ----------
    image_stack : xr.DataArray
        DataArray from which to take slices. Must have a band
        dimension and band coordinates value should be standard names
        for the respective band. For more info, see here:
        https://github.com/awesome-spectral-indices/awesome-spectral-indices

    Returns
    -------
    band_dict : dict
        Dictionary mapping standard names to slice of image_stack.

    """
    standard_names = list(spx.bands)
    params_dict = {}
    for standard in standard_names:
        try:
            band_slice = image_stack.sel(band=standard)
            params_dict[standard] = band_slice
        except KeyError:
            continue

    return params_dict
