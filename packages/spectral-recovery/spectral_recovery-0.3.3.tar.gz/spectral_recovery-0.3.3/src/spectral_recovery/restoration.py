"""Restoration Area class and helper methods.

The RestorationArea class coordinates the spectral data, dates,
polygons, and recovery target logic/computation, that is used
to fully define a restoration area. The expectation is for 
RestorationArea instances to be passed to recovery metric
methods, so that each method can have encapsulated access to
relevant restoration site information.

"""

import operator

from typing import Callable, Dict, List, Tuple
from datetime import datetime
from inspect import signature

import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np

from spectral_recovery.targets import MedianTarget, compute_recovery_targets, expected_signature
from spectral_recovery.timeseries import _SatelliteTimeSeries

from spectral_recovery._config import VALID_YEAR


def _str_to_dt(years: str | List[str]):
    if isinstance(years, list):
        years_dt = [0, 0]
        for i, year in enumerate(years):
            years_dt[i] = pd.to_datetime(year)
    else:
        years_dt = pd.to_datetime(years)
    return years_dt


def _npdt_to_year(np_dt: np.datetime64):
    """Convert np.datetime64 to year str"""
    pd_dt = pd.to_datetime(np_dt)
    return str(pd_dt.year)


def _valid_year_format(year_str):
    year_match = VALID_YEAR.match(year_str)
    if not year_match:
        raise ValueError(
            f"Could not parse {year_str} into a year. "
            "Please ensure the year is in the format 'YYYY'."
        )
    return year_str


class RestorationArea:
    """A Restoration Area (RA).

    A RestorationArea object validates and holds the locations, spectral
    data, dates, and recovery target(s) that define a restoration area.

    Attributes
    -----------
    full_timeseries : xr.DataArray
        A 4D (band, time, y, x) DataArray of images.
    timeseries_start : datetime
        The first year of the timeseries.
    timeseries_end : datetime
        The last year of the timeseries.
    restoration_polygon : GeoDataFrame
        The spatial deliniation of the restoration event. There
        must only be one geometry in the GeoDataframe and it must be
        of type shapely.Polygon or shapely.MultiPolygon.
    disturbance_start : str
        The start year of the disturbance window.
    restoration_start : str
        The start year of the restoration window.
    reference_years : list of str
        List of two strings: the start and end years of the reference
        window, respectively.
    restoration_image_stack : xr.DataArray
        The image stack which fully contains the restoration site.
        Derived (clipped) from full_timeseries. This is the stack used
        by recovery metric methods when computing metrics.
    reference_polygons : GeoDataFrame
        The spatial delinitation of the reference system area(s).
    recovery_target_method : callable
        The method used for computing the recovery target. Default
        is median target method with polygon scale (i.e
        MedianTarget(scale="polygon"))
    recovery_target : xr.DataArray
        The recovery target values.

    """

    def __init__(
        self,
        restoration_polygon: gpd.GeoDataFrame,
        composite_stack: xr.DataArray,
        reference_polygons: gpd.GeoDataFrame = None,
        recovery_target_method: Callable[
            [xr.DataArray, Tuple[datetime]], xr.DataArray
        ] = MedianTarget(scale="polygon"),
    ) -> None:
        """RestorationArea constructor.

        Parameters
        ----------
        restoration_polygon : geopandas.GeoDataFrame
            The polygon and associated dates of the restoration site,
            contained in a GeoDataFrame.

            If reference_polygons is None, 0th column must contain
            disturbance start year, 1st must restoration start year,
            and 3rd and 4th must contain the reference start and end
            years, respectively. If reference_polygons is not None,
            only disturbance and restoration start year must be provided.
        composite_stack : xr.DataArray
            The 4D stack of images to derive recovery metrics from.
            Must have dimensions ["band","time","y","x"] with coordinates.
            The data is expected (but not enforced) to be index values,
            not raw spectral data.
        reference_polygons : geopandas.GeoDataFrame, optional
            The polygon(s) and associated dates of the reference
            system, contained in a GeoDataFrame.

            0th column must contain the reference start year while
            the 1st column must contain the reference end year. If
            reference start and end years are also provided in the
            restoration_polygons DataFrame, the dates defined in
            reference_polygons will supersede.
        recovery_target_method : Callable, optional
            The method to compute recovery target with.

        """
        self.full_timeseries = composite_stack
        self.reference_polygons = reference_polygons
        self.restoration_polygon = restoration_polygon
        self.recovery_target_method = recovery_target_method

        # Eagerly compute the dates by called properties
        # This will force errors to throw early before init is complete
        # NOTE: this is messy; the polygon and dates are controlled in
        # difference properties making seperate calls necessary. Future
        # refactors should consider keeping checks all in one property
        self.disturbance_start
        self.restoration_start
        self.reference_years

    @property
    def full_timeseries(self) -> xr.DataArray:
        return self._full_timeseries

    @full_timeseries.setter
    def full_timeseries(self, t) -> None:
        """full_timeseries setter.

        Checks that the provided timeseries contains the correct
        dims and is an annual timeseries before setting the property.
        Forces lazy (re-)computation of the dependant cached properties,
        restoration_image_stack.

        """
        self._restoration_image_stack = None

        if not t.satts.is_annual_composite:
            raise ValueError(
                "composite_stack is not a valid set of annual composites. Please"
                " ensure there are no missing years and that the DataArray object"
                " contains 'band', 'time', 'y' and 'x' dimensions."
            ) from None
        self._full_timeseries = t

    @property
    def timeseries_end(self) -> np.datetime64:
        """The final year of the timeseries"""

        return _npdt_to_year(np.max(self.full_timeseries["time"].data))

    @property
    def timeseries_start(self) -> np.datetime64:
        """The first year of the timeseries"""
        return _npdt_to_year(np.min(self.full_timeseries["time"].data))

    @property
    def restoration_polygon(self) -> gpd.GeoDataFrame:
        """Restoration site GeoDataFrame

        GeoDataFrame contains a Shapely.Polygon and
        2 or 4 str columns. Polygon defines the area of
        the restoration site while attributes define
        the disturbance start, restoration start, reference
        end, and reference start years respectively.

        """
        return self._restoration_polygon

    @restoration_polygon.setter
    def restoration_polygon(self, rp) -> None:
        """restoration_polygon setter.

        Checks that input is a GeoDataFrame, contains
        only one row/geometry and that the given geom is
        within the bounds of self.full_timeseries. Forces
        lazy (re-)computation of disturbance_start,
        restoration_start, reference years, and recovery_target
        cached properties.

        """
        self._restoration_image_stack = None
        self._recovery_target = None
        # NOTE: this is messy because restoration_polygon now takes
        # the whole DF with the dates (not just poly), which makes
        # the date attributes dependant on it. This attr should
        # be refactored for clarity.
        self._disturbance_start = None
        self._restoration_start = None
        if self._reference_polygons is None:
            self._reference_years = None

        if not isinstance(rp, gpd.GeoDataFrame):
            raise ValueError(
                f"restoration_polygon must be a GeoDataFrame (recieved type {type(rp)})"
            )
        if rp.shape[0] != 1:
            raise ValueError(
                "restoration_polygon instance can only contain one Polygon."
            ) from None
        if not self.full_timeseries.satts.contains_spatial(rp):
            raise ValueError(
                "restoration_polygon is not within the bounds of images"
            ) from None

        self._restoration_polygon = rp

    @property
    def reference_polygons(self) -> gpd.GeoDataFrame:
        """Reference system GeoDataFrame

        GeoDataFrame contains a Shapely.Polygon and
        2 str columns. Polygon defines the areas used in
        the reference system while columns define
        the reference end and start year, respectively.

        """
        return self._reference_polygons

    @reference_polygons.setter
    def reference_polygons(self, refp) -> None:
        """reference_polygons setter.

        If refp is not None, checks that refp is a GeoDataFrame
        and that all geoms are within the bounds of full_timeseries
        property. Immediately recomputes reference_years property.

        Raises
        ------
        TypeError
            - If refp not None and not geopandas.GeoDataFrame.
        ValueError
            - If refp not within spatial bounds of full_timeseries prop.

        """
        self._reference_years = None
        if refp is not None:
            if not isinstance(refp, gpd.GeoDataFrame):
                raise TypeError(
                    "reference_polygons must be a GeoDataFrame (recieved type"
                    f" {type(refp)})"
                )
            if not self.full_timeseries.satts.contains_spatial(refp):
                raise ValueError(
                    "not all reference_polygons within the bounds of images"
                ) from None
        self._reference_polygons = refp

    @property
    def recovery_target_method(self) -> Callable:
        """Method used to compute recovery targets for the RestorationArea"""
        return self._recovery_target_method

    @recovery_target_method.setter
    def recovery_target_method(self, rtm) -> None:
        """recovery_target_method setter.

        Checks that signature of method matches required signature.
        Then checks method type is compatible with the current
        restoration site and reference system (i.e historic or
        reference recovery target set-up). Forces lazy (re-)computation
        of the recovery_target property.

        Raises
        ------
        ValueError
            - If rtm does not have required call signature.
            - If rtm is not compatible with current polygons.

        """
        self._recovery_target = None
        if signature(rtm) != expected_signature:
            raise ValueError(
                "The provided recovery target method must have the expected call"
                f" signature: {expected_signature} (given {signature(rtm)})"
            )
        if self.reference_polygons is not None:
            if isinstance(rtm, MedianTarget):
                if rtm.scale == "pixel":
                    raise TypeError(
                        "Pixel scale median recovery target cannot be used with"
                        " reference polygons, only polygon scale."
                    )
        self._recovery_target_method = rtm

    @property
    def recovery_target(self) -> xr.DataArray:
        """Recovery target of the RestorationArea.

        The recovery targets of the RestorationArray provided in
        an xarray.DataArray. The targets are computed using the
        recovery_target_method and based on either historic conditions
        or a reference system, if provided. See targets module for
        more information.

        """
        if self._recovery_target is None:
            self._recovery_target = compute_recovery_targets(
                timeseries=self.full_timeseries,
                restoration_polygon=self.restoration_polygon,
                reference_start=self.reference_years[0],
                reference_end=self.reference_years[1],
                reference_polygons=self.reference_polygons, 
                func=self.recovery_target_method
            )
        return self._recovery_target

    @property
    def disturbance_start(self) -> str:
        """Start year of the disturbance window.

        A str taken from first column of the restoration_polygon
        geopandas.GeoDataFrame. Represents the start year of the
        disturbance window. Must be within the temporal range of
        the full_timeseries property.

        Raises
        ------
        ValueError
            - If disturbance start year greater than restoration year.
            - If disturbance start year is not within temporal
              range of full_timeseries.

        """
        if self._disturbance_start is None:
            self._disturbance_start = self._get_dist_from_frame()
            if self._disturbance_start >= self.restoration_start:
                raise ValueError(
                    "Disturbance start year cannot be greater than restoration start"
                    f" year (given disturbance_start={self._disturbance_start} and"
                    f" restoration_start={self.restoration_start})"
                )
            if not self.full_timeseries.satts.contains_temporal(
                _str_to_dt(self._disturbance_start)
            ):
                raise ValueError(
                    f"Disturbance start year { self._disturbance_start} not within"
                    " timeseries range of"
                    f" {self.timeseries_start}-{self.timeseries_end}."
                )
        return self._disturbance_start

    @property
    def restoration_start(self) -> str:
        """Start year of the restoration window.

        A str taken from second column of the restoration_polygon
        geopandas.GeoDataFrame. Represents the start year of the
        restoration window. Must be within the temporal range of
        the full_timeseries property.

        Raises
        ------
        ValueError
            - If restoration start year less than disturbance start year.
            - If restoration start year is not within temporal
              range of full_timeseries.

        """
        if self._restoration_start is None:
            self._restoration_start = self._get_rest_from_frame()
            if self._restoration_start <= self.disturbance_start:
                raise ValueError(
                    "Restoration start year cannot be less than disturbance start year"
                    f" (given disturbance_start={self.disturbance_start} and"
                    f" restoration_start={self._restoration_start})"
                )
            if not self.full_timeseries.satts.contains_temporal(
                _str_to_dt(self._restoration_start)
            ):
                raise ValueError(
                    f"Restoration start year { self._restoration_start} not within"
                    " timeseries range of"
                    f" {self.timeseries_start}-{self.timeseries_end}."
                )
        return self._restoration_start

    @property
    def reference_years(self) -> str:
        """Start and end year of the reference window.

        List of 2 str taken from third and fourth column of the
        restoration_polygon geopandas.GeoDataFrame or, if
        reference_polygons is not None, the first and second column
        of the reference_polygons GeoDataFrame. Represents the start
        and end year of the reference window. Must be within temporal
        range of the full_timeseries property.

        Raises
        ------
        ValueError
            - If reference start year greater than reference end year.
            - If range of years between reference start and end year are
              not within temporal range of full_timeseries.

        """
        if self._reference_years is None:
            self._recovery_target = None
            self._reference_years = self._get_ref_from_frame()
            if self._reference_years[0] > self._reference_years[1]:
                raise ValueError(
                    "Reference start year must be less than or equal to end year (but"
                    f" {self._reference_years[0]} > {self._reference_years[1]})"
                )
            if not self.full_timeseries.satts.contains_temporal(
                _str_to_dt(self._reference_years)
            ):
                raise ValueError(
                    f"Reference years { self._reference_years} not within timeseries"
                    f" range of {self.timeseries_start}-{self.timeseries_end}."
                )
        return self._reference_years

    @property
    def restoration_image_stack(self) -> xr.DataArray:
        """Restoration image stack.

        The image stack containing the restoration site.
        Clipped to the bounding box of the restoration polygon.

        """
        if self._restoration_image_stack is None:
            self._restoration_image_stack = self.full_timeseries.rio.clip(
                self.restoration_polygon.geometry.values
            )
        return self._restoration_image_stack

    def _get_dist_from_frame(self):
        """Get and validate disturbance start year from restoration_polygon."""
        rest_dates = pd.DataFrame(self.restoration_polygon.drop(columns="geometry"))
        try:
            disturbance_start = rest_dates.iloc[0, 0]
        except IndexError:
            raise ValueError(
                "Missing disturbance start year. Please ensure the 1st column of the"
                " restoration polygon's  attribute table contains the disturbance"
                " window start year. "
            )
        disturbance_start_str = str(disturbance_start)
        disturbance_start_str = _valid_year_format(disturbance_start_str)
        return disturbance_start_str

    def _get_rest_from_frame(self):
        """Get and validate restoration start year from restoration_polygon."""
        rest_dates = pd.DataFrame(self.restoration_polygon.drop(columns="geometry"))
        try:
            restoration_start = rest_dates.iloc[0, 1]
        except IndexError:
            raise ValueError(
                "Missing restoration start year. Please ensure the 2nd column of the"
                " restoration polygon's  attribute table contains the restoration"
                " window start year. "
            )
        rest_start_str = str(restoration_start)
        rest_start_str = _valid_year_format(rest_start_str)
        return rest_start_str

    def _get_ref_from_frame(self):
        """Get and validate reference years from either restoration_polygon
        or reference_polygons."""
        if self.reference_polygons is not None:
            ref_dates = pd.DataFrame(self.reference_polygons.drop(columns="geometry"))
            try:
                ref_start = ref_dates.iloc[0, 0]
                ref_end = ref_dates.iloc[0, 1]
            except:
                ValueError(
                    "Missing reference years. Reference start and end years must be"
                    " provided in the 1st and 2nd columns of the reference polygon's"
                    " attribute table."
                )
        else:
            ref_dates = pd.DataFrame(self.restoration_polygon.drop(columns="geometry"))
            try:
                ref_start = ref_dates.iloc[0, 2]
                ref_end = ref_dates.iloc[0, 3]
            except IndexError:
                raise ValueError(
                    "Missing reference years. If reference_polygons is None then "
                    " reference years (start and end) must be provided in 3rd and 4th "
                    "columns of the restoration polygon's attribute table."
                )

        ref_start_str = str(ref_start)
        ref_end_str = str(ref_end)
        ref_start_str = _valid_year_format(ref_start_str)
        ref_end_str = _valid_year_format(ref_end_str)

        return [ref_start_str, ref_end_str]
