# -*- coding: utf-8 -*-
"""

    mslib.mswms.mss_plot_driver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver classes to create plots from ECMWF NetCDF data.

    This file is part of MSS.

    :copyright: Copyright 2008-2014 Deutsches Zentrum fuer Luft- und Raumfahrt e.V.
    :copyright: Copyright 2011-2014 Marc Rautenhaus (mr)
    :copyright: Copyright 2016-2024 by the MSS team, see AUTHORS.
    :license: APACHE-2.0, see LICENSE for details.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from datetime import datetime

import os
from abc import ABCMeta, abstractmethod

import numpy as np

from mslib.utils import netCDF4tools, LOGGER
import mslib.utils.coordinate as coordinate
from mslib.utils.units import convert_to, units


class MSSPlotDriver(metaclass=ABCMeta):
    """
    Abstract super class for implementing driver classes that provide
    access to the MSS data server.

    The idea of a driver class is to encapsulate all methods related to
    loading data fields into memory. A driver can control objects from
    plotting classes that provide (a) a list of required variables and
    (b) a plotting method that only accepts data fields already loaded into
    memory.

    MSSPlotDriver implements methods that determine, given a list of required
    variables from a plotting instance <plot_object> and a forecast time
    specified by initialisation and valid time, the corresponding data files.
    The files are opened and the NetCDF variable objects are determined.

    Classes that derive from this class need to implement the two methods
    set_plot_parameters() and plot().
    """

    def __init__(self, data_access_object):
        """
        Requires an instance of a data access object from the MSS
        configuration (i.e. an NWPDataAccess instance).
        """
        self.data_access = data_access_object
        self.dataset = None
        self.plot_object = None
        self.filenames = []

    def __del__(self):
        """
        Closes the open NetCDF dataset, if existing.
        """
        if self.dataset is not None:
            self.dataset.close()

    def _set_time(self, init_time, fc_time):
        """
        Open the dataset that corresponds to a forecast field specified
        by an initialisation and a valid time.

        This method
          determines the files that correspond to an init time and forecast step
          checks if an open NetCDF dataset exists
            if yes, checks whether it contains the requested valid time
              if not, closes the dataset and opens the corresponding one
          loads dimension data if required.
        """
        if len(self.plot_object.required_datafields) == 0:
            LOGGER.debug("no datasets required.")
            self.dataset = None
            self.filenames = []
            self.init_time = None
            self.fc_time = None
            self.times = np.array([])
            self.lat_data = np.array([])
            self.lon_data = np.array([])
            self.lat_order = 1
            self.vert_data = None
            self.vert_order = None
            self.vert_units = None
            return

        if self.uses_inittime_dimension():
            LOGGER.debug("\trequested initialisation time %s", init_time)
            if fc_time < init_time:
                msg = "Forecast valid time cannot be earlier than " \
                      "initialisation time."
                LOGGER.error(msg)
                raise ValueError(msg)
        self.fc_time = fc_time
        LOGGER.debug("\trequested forecast valid time %s", fc_time)

        # Check if a dataset is open and if it contains the requested times.
        # (a dataset will only be open if the used layer has not changed,
        # i.e. the required variables have not changed as well).
        if (self.dataset is not None) and (self.init_time == init_time) and (fc_time in self.times):
            LOGGER.debug("\tinit time correct and forecast valid time contained (%s).", fc_time)
            if not self.data_access.is_reload_required(self.filenames):
                return
            LOGGER.debug("need to re-open input files.")
            self.dataset.close()
            self.dataset = None

        # Determine the input files from the required variables and the
        # requested time:

        # Create the names of the files containing the required parameters.
        self.filenames = []
        for vartype, var, _ in self.plot_object.required_datafields:
            filename = self.data_access.get_filename(
                var, vartype, init_time, fc_time, fullpath=True)
            if filename not in self.filenames:
                self.filenames.append(filename)
            LOGGER.debug("\tvariable '%s' requires input file '%s'",
                          var, os.path.basename(filename))

        if len(self.filenames) == 0:
            raise ValueError("no files found that correspond to the specified "
                             "datafields. Aborting..")

        self.init_time = init_time

        # Open NetCDF files as one dataset with common dimensions.
        LOGGER.debug("opening datasets.")
        dsKWargs = self.data_access.mfDatasetArgs()
        dataset = netCDF4tools.MFDatasetCommonDims(self.filenames, **dsKWargs)

        # Load and check time dimension. self.dataset will remain None
        # if an Exception is raised here.
        timename, timevar = netCDF4tools.identify_CF_time(dataset)

        times = netCDF4tools.num2date(timevar[:], timevar.units)
        # removed after discussion, see
        # https://mss-devel.slack.com/archives/emerge/p1486658769000007
        # if init_time != netCDF4tools.num2date(0, timevar.units):
        #     dataset.close()
        #     raise ValueError("wrong initialisation time in input")

        if fc_time not in times:
            msg = f"Forecast valid time '{fc_time}' is not available."
            LOGGER.error(msg)
            dataset.close()
            raise ValueError(msg)

        # Load lat/lon dimensions.
        try:
            lat_data, lon_data, lat_order = netCDF4tools.get_latlon_data(dataset)
        except Exception as ex:
            LOGGER.error("ERROR: %s %s", type(ex), ex)
            dataset.close()
            raise

        _, vert_data, vert_orientation, vert_units, _ = netCDF4tools.identify_vertical_axis(dataset)
        self.vert_data = vert_data[:] if vert_data is not None else None
        self.vert_order = vert_orientation
        self.vert_units = vert_units

        self.dataset = dataset
        self.times = times
        self.lat_data = lat_data
        self.lon_data = lon_data
        self.lat_order = lat_order

        # Identify the variable objects from the NetCDF file that correspond
        # to the data fields required by the plot object.
        self._find_data_vars()

    def _find_data_vars(self):
        """
        Find NetCDF variables of required data fields.

        A dictionary data_vars is created. Its keys are the CF standard names
        of the variables provided by the plot object. The values are pointers
        to the NetCDF variable objects.

        <data_vars> can be accessed as <self.data_vars>.
        """
        self.data_vars = {}
        self.data_units = {}
        for df_type, df_name, _ in self.plot_object.required_datafields:
            varname, var = netCDF4tools.identify_variable(self.dataset, df_name, check=True)
            LOGGER.debug("\tidentified variable <%s> for field <%s>", varname, df_name)
            self.data_vars[df_name] = var
            self.data_units[df_name] = getattr(var, "units", None)

    def have_data(self, plot_object, init_time, valid_time):
        """
        Checks if this driver has the required data to do the plot

        This inquires the contained data access class if data is available for
        all required data fields for the specified times.
        """
        return all(
            self.data_access.have_data(var, vartype, init_time, valid_time)
            for vartype, var in plot_object.required_datafields)

    @abstractmethod
    def set_plot_parameters(self, plot_object, init_time=None, valid_time=None,
                            style=None, bbox=None, figsize=(800, 600),
                            noframe=False, require_reload=False, transparent=False,
                            mime_type="image/png"):
        """
        Set parameters controlling the plot.

        Parameters not passed as arguments are reset to standard values.

        THIS METHOD NEEDS TO BE REIMPLEMENTED IN ANY CLASS DERIVING FROM
        MSSPlotDriver!

        Derived methods need to call the super method before all other
        statements.
        """
        LOGGER.debug("using plot object '%s'", plot_object.name)
        LOGGER.debug("\tfigure size %s in pixels", figsize)

        # If the plot object has been changed, the dataset needs to be reloaded
        # (the required variables could have changed).
        if self.plot_object is not None:
            require_reload = require_reload or (self.plot_object != plot_object)
        if require_reload and self.dataset is not None:
            self.dataset.close()
            self.dataset = None

        self.plot_object = plot_object
        self.figsize = figsize
        self.noframe = noframe
        self.style = style
        self.bbox = bbox
        self.transparent = transparent
        self.mime_type = mime_type

        self._set_time(init_time, valid_time)

    @abstractmethod
    def update_plot_parameters(self, plot_object=None, figsize=None, style=None,
                               bbox=None, init_time=None, valid_time=None,
                               noframe=None, transparent=None, mime_type=None):
        """
        Update parameters controlling the plot.

        Similar to set_plot_parameters(), but keeps all parameters already
        set except the ones that are specified.

        THIS METHOD NEEDS TO BE REIMPLEMENTED IN ANY CLASS DERIVING FROM
        MSSPlotDriver!

        Derived methods need to call the super method before all other
        statements.
        """
        plot_object = plot_object if plot_object is not None else self.plot_object
        figsize = figsize if figsize is not None else self.figsize
        noframe = noframe if noframe is not None else self.noframe
        init_time = init_time if init_time is not None else self.init_time
        valid_time = valid_time if valid_time is not None else self.fc_time
        style = style if style is not None else self.style
        bbox = bbox if bbox is not None else self.bbox
        transparent = transparent if transparent is not None else self.transparent
        mime_type = mime_type if mime_type is not None else self.mime_type
        # Explicitly call MSSPlotDriver's set_plot_parameters(). A "self.--"
        # call would call the derived class's method and thus reset
        # parameters specific to the derived class.
        MSSPlotDriver.set_plot_parameters(self, plot_object,
                                          init_time=init_time,
                                          valid_time=valid_time,
                                          figsize=figsize,
                                          style=style,
                                          bbox=bbox,
                                          noframe=noframe,
                                          transparent=transparent,
                                          mime_type=mime_type)

    @abstractmethod
    def plot(self):
        """
        Plot the figure (i.e. load the data fields and call the
        corresponding plotting routines of the plot object).

        THIS METHOD NEEDS TO BE REIMPLEMENTED IN ANY CLASS DERIVING FROM
        MSSPlotDriver!
        """
        pass

    def get_init_times(self):
        """
        Returns a list of available forecast init times (base times).
        """
        return self.data_access.get_init_times()

    def get_elevations(self, vert_type):
        """
        See ECMWFDataAccess.get_elevations().
        """
        return self.data_access.get_elevations(vert_type)

    def get_elevation_units(self, vert_type):
        """
        See ECMWFDataAccess.get_elevation().
        """
        return self.data_access.get_elevation_units(vert_type)

    def get_all_valid_times(self, variable, vartype):
        """
        See ECMWFDataAccess.get_all_valid_times().
        """
        return self.data_access.get_all_valid_times(variable, vartype)

    def get_valid_times(self, variable, vartype, init_time):
        """
        See ECMWFDataAccess.get_valid_times().
        """
        return self.data_access.get_valid_times(variable, vartype, init_time)

    def uses_inittime_dimension(self):
        """
        Returns whether this driver uses the WMS inittime dimensions.
        """
        return self.data_access.uses_inittime_dimension()

    def uses_validtime_dimension(self):
        """
        Returns whether this layer uses the WMS time dimensions.
        """
        return self.data_access.uses_validtime_dimension()


class VerticalSectionDriver(MSSPlotDriver):
    """
    The vertical section driver is responsible for loading the data that
    is to be plotted and for calling the plotting routines (that have
    to be registered).
    """

    def set_plot_parameters(self, plot_object=None, vsec_path=None,
                            vsec_numpoints=101, vsec_path_connection='linear',
                            vsec_numlabels=10,
                            init_time=None, valid_time=None, style=None,
                            bbox=None, figsize=(800, 600), noframe=False, draw_verticals=False,
                            show=False, transparent=False,
                            mime_type="image/png"):
        """
        """
        MSSPlotDriver.set_plot_parameters(self, plot_object,
                                          init_time=init_time,
                                          valid_time=valid_time,
                                          style=style,
                                          bbox=bbox,
                                          figsize=figsize, noframe=noframe,
                                          transparent=transparent,
                                          mime_type=mime_type)
        self._set_vertical_section_path(vsec_path, vsec_numpoints,
                                        vsec_path_connection)
        self.show = show
        self.vsec_numlabels = vsec_numlabels
        self.draw_verticals = draw_verticals

    def update_plot_parameters(self, plot_object=None, vsec_path=None,
                               vsec_numpoints=None, vsec_path_connection=None,
                               vsec_numlabels=None,
                               init_time=None, valid_time=None, style=None,
                               bbox=None, figsize=None, noframe=None, draw_verticals=None, show=None,
                               transparent=None, mime_type=None):
        """
        """
        plot_object = plot_object if plot_object is not None else self.plot_object
        figsize = figsize if figsize is not None else self.figsize
        noframe = noframe if noframe is not None else self.noframe
        draw_verticals = draw_verticals if draw_verticals else self.draw_verticals
        init_time = init_time if init_time is not None else self.init_time
        valid_time = valid_time if valid_time is not None else self.fc_time
        style = style if style is not None else self.style
        bbox = bbox if bbox is not None else self.bbox
        vsec_path = vsec_path if vsec_path is not None else self.vsec_path
        vsec_numpoints = vsec_numpoints if vsec_numpoints is not None else self.vsec_numpoints
        vsec_numlabels = vsec_numlabels if vsec_numlabels is not None else self.vsec_numlabels
        if vsec_path_connection is None:
            vsec_path_connection = self.vsec_path_connection
        show = show if show else self.show
        transparent = transparent if transparent is not None else self.transparent
        mime_type = mime_type if mime_type is not None else self.mime_type
        self.set_plot_parameters(plot_object=plot_object,
                                 vsec_path=vsec_path,
                                 vsec_numpoints=vsec_numpoints,
                                 vsec_path_connection=vsec_path_connection,
                                 vsec_numlabels=vsec_numlabels,
                                 init_time=init_time,
                                 valid_time=valid_time,
                                 style=style,
                                 bbox=bbox,
                                 figsize=figsize,
                                 noframe=noframe,
                                 draw_verticals=draw_verticals,
                                 show=show,
                                 transparent=transparent,
                                 mime_type=mime_type)

    def _set_vertical_section_path(self, vsec_path, vsec_numpoints=101,
                                   vsec_path_connection='linear'):
        """
        """
        LOGGER.debug("computing %i interpolation points, connection: %s",
                      vsec_numpoints, vsec_path_connection)
        self.lats, self.lons = coordinate.path_points(
            [_x[0] for _x in vsec_path],
            [_x[1] for _x in vsec_path],
            numpoints=vsec_numpoints, connection=vsec_path_connection)
        self.lats, self.lons = np.asarray(self.lats), np.asarray(self.lons)
        self.vsec_path = vsec_path
        self.vsec_numpoints = vsec_numpoints
        self.vsec_path_connection = vsec_path_connection

    def _load_interpolate_timestep(self):
        """
        Load and interpolate the data fields as required by the vertical
        section style instance. Only data of time <fc_time> is processed.

        Shifts the data fields such that the longitudes are in the range
        left_longitude .. left_longitude+360, where left_longitude is the
        westmost longitude appearing in the list of waypoints minus one
        gridpoint (to include all waypoint longitudes).

        Necessary to prevent data cut-offs in situations where the requested
        cross section crosses the data longitude boundaries (e.g. data is
        stored on a 0..360 grid, but the path is in the range -10..+20).
        """
        if self.dataset is None:
            return {}
        data = {}

        timestep = self.times.searchsorted(self.fc_time)
        LOGGER.debug("loading data for time step %s (%s)", timestep, self.fc_time)

        # Determine the westmost longitude in the cross-section path. Subtract
        # one gridbox size to obtain "left_longitude".
        dlon = self.lon_data[1] - self.lon_data[0]
        left_longitude = np.unwrap(self.lons, period=360).min() - dlon
        LOGGER.debug("shifting data grid to gridpoint west of westmost "
                      "longitude in path: %.2f (path %.2f).",
                      left_longitude, self.lons.min())

        # Shift the longitude field such that the data is in the range
        # left_longitude .. left_longitude+360.
        # NOTE: This does not overwrite self.lon_data (which is required
        # in its original form in case other data is loaded while this
        # file is open).
        lon_data = ((self.lon_data - left_longitude) % 360) + left_longitude
        lon_indices = lon_data.argsort()
        lon_data = lon_data[lon_indices]
        # Identify jump in longitudes due to non-global dataset
        dlon_data = np.diff(lon_data)
        jump = np.where(dlon_data > 2 * dlon)[0]

        lons = ((self.lons - left_longitude) % 360) + left_longitude

        for name, var in self.data_vars.items():
            if len(var.shape) == 4:
                var_data = var[timestep, ::-self.vert_order, ::self.lat_order, :]
            else:
                var_data = var[:][timestep, np.newaxis, ::self.lat_order, :]
            LOGGER.debug("\tLoaded %.2f Mbytes from data field <%s> at timestep %s.",
                          var_data.nbytes / 1048576., name, timestep)
            LOGGER.debug("\tVertical dimension direction is %s.",
                          "up" if self.vert_order == 1 else "down")
            LOGGER.debug("\tInterpolating to cross-section path.")
            # Re-arange longitude dimension in the data field.
            var_data = var_data[:, :, lon_indices]
            if jump:
                LOGGER.debug("\tsetting jump data to NaN at %s", jump)
                var_data = var_data.copy()
                var_data[:, :, jump] = np.nan
            data[name] = coordinate.interpolate_vertsec(var_data, self.lat_data, lon_data, self.lats, lons)
            # Free memory.
            del var_data

        return data

    def shift_data(self):
        """
        Shift the data fields such that the longitudes are in the range
        left_longitude .. left_longitude+360, where left_longitude is the
        westmost longitude appearing in the list of waypoints minus one
        gridpoint (to include all waypoint longitudes).

        Necessary to prevent data cut-offs in situations where the requested
        cross section crosses the data longitude boundaries (e.g. data is
        stored on a 0..360 grid, but the path is in the range -10..+20).
        """
        # Determine the leftmost longitude in the plot.
        left_longitude = self.lons.min()
        LOGGER.debug("shifting data grid to leftmost longitude in path "
                      "(%.2f)..", left_longitude)

        # Shift the longitude field such that the data is in the range
        # left_longitude .. left_longitude+360.
        self.lons = ((self.lons - left_longitude) % 360) + left_longitude
        lon_indices = self.lons.argsort()
        self.lons = self.lons[lon_indices]

        # Shift data fields correspondingly.
        for key in self.data:
            self.data[key] = self.data[key][:, lon_indices]

    def plot(self):
        """
        """
        d1 = datetime.now()

        # Load and interpolate the data fields as required by the vertical
        # section style instance. <data> is a dictionary containing the
        # interpolated curtains of the variables identified through CF
        # standard names as specified by <self.vsec_style_instance>.
        data = self._load_interpolate_timestep()

        d2 = datetime.now()
        LOGGER.debug("Loaded and interpolated data (required time %s).", d2 - d1)
        LOGGER.debug("Plotting interpolated curtain.")

        if len(self.lat_data) > 1 and len(self.lon_data) > 1:
            resolution = (self.lon_data[1] - self.lon_data[0],
                          self.lat_data[1] - self.lat_data[0])
        else:
            resolution = (-1, -1)

        if self.mime_type not in ("image/png", "text/xml"):
            raise RuntimeError(f"Unexpected format for vertical sections '{self.mime_type}'.")

        # Call the plotting method of the vertical section style instance.
        image = self.plot_object.plot_vsection(data, self.lats, self.lons,
                                               valid_time=self.fc_time,
                                               init_time=self.init_time,
                                               resolution=resolution,
                                               bbox=self.bbox,
                                               style=self.style,
                                               show=self.show,
                                               highlight=self.vsec_path,
                                               noframe=self.noframe,
                                               figsize=self.figsize,
                                               draw_verticals=self.draw_verticals,
                                               transparent=self.transparent,
                                               numlabels=self.vsec_numlabels,
                                               mime_type=self.mime_type)
        # Free memory.
        del data

        d3 = datetime.now()
        LOGGER.debug("Finished plotting (required time %s; total "
                      "time %s).\n", d3 - d2, d3 - d1)

        return image


class HorizontalSectionDriver(MSSPlotDriver):
    """
    The horizontal section driver is responsible for loading the data that
    is to be plotted and for calling the plotting routines (that have
    to be registered).
    """

    def set_plot_parameters(self, plot_object=None, bbox=None, level=None, crs=None, init_time=None, valid_time=None,
                            style=None, figsize=(800, 600), noframe=False, show=False, transparent=False,
                            mime_type="image/png"):
        """
        """
        MSSPlotDriver.set_plot_parameters(self, plot_object,
                                          init_time=init_time,
                                          valid_time=valid_time,
                                          style=style,
                                          bbox=bbox,
                                          figsize=figsize, noframe=noframe,
                                          transparent=transparent,
                                          mime_type=mime_type)
        self.level = level
        self.actual_level = None
        self.crs = crs
        self.show = show

    def update_plot_parameters(self, plot_object=None, bbox=None, level=None, crs=None, init_time=None, valid_time=None,
                               style=None, figsize=None, noframe=None, show=None, transparent=None, mime_type=None):
        """
        """
        plot_object = plot_object if plot_object is not None else self.plot_object
        figsize = figsize if figsize is not None else self.figsize
        noframe = noframe if noframe is not None else self.noframe
        init_time = init_time if init_time is not None else self.init_time
        valid_time = valid_time if valid_time is not None else self.fc_time
        style = style if style is not None else self.style
        bbox = bbox if bbox is not None else self.bbox
        level = level if level is not None else self.level
        crs = crs if crs is not None else self.crs
        show = show if show is not None else self.show
        transparent = transparent if transparent is not None else self.transparent
        mime_type = mime_type if mime_type is not None else self.mime_type
        self.set_plot_parameters(plot_object=plot_object, bbox=bbox, level=level, crs=crs, init_time=init_time,
                                 valid_time=valid_time, style=style, figsize=figsize, noframe=noframe, show=show,
                                 transparent=transparent, mime_type=mime_type)

    def _load_timestep(self):
        """
        Load the data fields as required by the horizontal section style
        instance at the current timestep.
        """
        if self.dataset is None:
            return {}
        data = {}
        timestep = self.times.searchsorted(self.fc_time)
        level = None
        if self.level is not None:
            # select the nearest level available
            level = np.abs(self.vert_data - self.level).argmin()
            if abs(self.vert_data[level] - self.level) > 1e-3 * np.abs(np.diff(self.vert_data).mean()):
                raise ValueError("Requested elevation not available.")
            self.actual_level = self.vert_data[level]
        LOGGER.debug("loading data for time step %s (%s), level index %s (level %s)",
                      timestep, self.fc_time, level, self.actual_level)
        for name, var in self.data_vars.items():
            if level is None or len(var.shape) == 3:
                # 2D fields: time, lat, lon.
                var_data = var[timestep, ::self.lat_order, :]
            else:
                # 3D fields: time, level, lat, lon.
                var_data = var[timestep, level, ::self.lat_order, :]
            LOGGER.debug("\tLoaded %.2f Mbytes from data field <%s>.",
                          var_data.nbytes / 1048576., name)
            data[name] = var_data
            # Free memory.
            del var_data

        return data

    def plot(self):
        """
        """
        d1 = datetime.now()

        # Load and interpolate the data fields as required by the horizontal
        # section style instance. <data> is a dictionary containing the
        # horizontal sections of the variables identified through CF
        # standard names as specified by <self.hsec_style_instance>.
        data = self._load_timestep()

        d2 = datetime.now()
        LOGGER.debug("Loaded data (required time %s).", (d2 - d1))
        LOGGER.debug("Plotting horizontal section.")

        if len(self.lat_data) > 1:
            resolution = (self.lat_data[1] - self.lat_data[0])
        else:
            resolution = 0

        if self.mime_type != "image/png":
            raise RuntimeError(f"Unexpected format for horizontal sections '{self.mime_type}'.")

        # Call the plotting method of the horizontal section style instance.
        image = self.plot_object.plot_hsection(data,
                                               self.lat_data,
                                               self.lon_data,
                                               self.bbox,
                                               level=self.actual_level,
                                               valid_time=self.fc_time,
                                               init_time=self.init_time,
                                               resolution=resolution,
                                               show=self.show,
                                               crs=self.crs,
                                               style=self.style,
                                               noframe=self.noframe,
                                               figsize=self.figsize,
                                               transparent=self.transparent)
        # Free memory.
        del data

        d3 = datetime.now()
        LOGGER.debug("Finished plotting (required time %s; total "
                      "time %s).\n", d3 - d2, d3 - d1)

        return image


class LinearSectionDriver(VerticalSectionDriver):
    """
        The linear plot driver is responsible for loading the data that
        is to be plotted and for calling the plotting routines (that have
        to be registered).
        """

    def set_plot_parameters(self, plot_object=None, lsec_path=None,
                            lsec_numpoints=101, lsec_path_connection='linear',
                            init_time=None, valid_time=None, bbox=None, mime_type=None):
        """
        """
        MSSPlotDriver.set_plot_parameters(self, plot_object,
                                          init_time=init_time,
                                          valid_time=valid_time,
                                          bbox=bbox, mime_type=mime_type)
        self._set_linear_section_path(lsec_path, lsec_numpoints, lsec_path_connection)

    def update_plot_parameters(self, plot_object=None, lsec_path=None,
                               lsec_numpoints=None, lsec_path_connection=None,
                               init_time=None, valid_time=None, bbox=None, mime_type=None):
        """
        """
        plot_object = plot_object if plot_object is not None else self.plot_object
        init_time = init_time if init_time is not None else self.init_time
        valid_time = valid_time if valid_time is not None else self.fc_time
        bbox = bbox if bbox is not None else self.bbox
        lsec_path = lsec_path if lsec_path is not None else self.lsec_path
        lsec_numpoints = lsec_numpoints if lsec_numpoints is not None else self.lsec_numpoints
        if lsec_path_connection is None:
            lsec_path_connection = self.lsec_path_connection
        mime_type = mime_type if mime_type is not None else self.mime_type
        self.set_plot_parameters(plot_object=plot_object,
                                 lsec_path=lsec_path,
                                 lsec_numpoints=lsec_numpoints,
                                 lsec_path_connection=lsec_path_connection,
                                 init_time=init_time,
                                 valid_time=valid_time,
                                 bbox=bbox,
                                 mime_type=mime_type)

    def _set_linear_section_path(self, lsec_path, lsec_numpoints=101, lsec_path_connection='linear'):
        """
        """
        LOGGER.debug("computing %i interpolation points, connection: %s",
                      lsec_numpoints, lsec_path_connection)
        self.lats, self.lons, self.alts = coordinate.path_points(
            [_x[0] for _x in lsec_path],
            [_x[1] for _x in lsec_path],
            alts=[_x[2] for _x in lsec_path],
            numpoints=lsec_numpoints, connection=lsec_path_connection)
        self.lats, self.lons, self.alts = [
            np.asarray(_x) for _x in (self.lats, self.lons, self.alts)]
        self.lsec_path = lsec_path
        self.lsec_numpoints = lsec_numpoints
        self.lsec_path_connection = lsec_path_connection

    def _load_interpolate_timestep(self):
        """
        Load and interpolate the data fields as required by the linear
        section style instance. Only data of time <fc_time> is processed.

        Shifts the data fields such that the longitudes are in the range
        left_longitude .. left_longitude+360, where left_longitude is the
        westmost longitude appearing in the list of waypoints minus one
        gridpoint (to include all waypoint longitudes).

        Necessary to prevent data cut-offs in situations where the requested
        cross section crosses the data longitude boundaries (e.g. data is
        stored on a 0..360 grid, but the path is in the range -10..+20).
        """
        if self.dataset is None:
            return {}
        data = {}

        timestep = self.times.searchsorted(self.fc_time)
        LOGGER.debug("loading data for time step %s (%s)", timestep, self.fc_time)

        # Determine the westmost longitude in the cross-section path. Subtract
        # one gridbox size to obtain "left_longitude".
        dlon = self.lon_data[1] - self.lon_data[0]
        left_longitude = np.unwrap(self.lons, period=360).min() - dlon
        LOGGER.debug("shifting data grid to gridpoint west of westmost "
                      "longitude in path: %.2f (path %.2f).",
                      left_longitude, self.lons.min())

        # Shift the longitude field such that the data is in the range
        # left_longitude .. left_longitude+360.
        # NOTE: This does not overwrite self.lon_data (which is required
        # in its original form in case other data is loaded while this
        # file is open).
        lon_data = ((self.lon_data - left_longitude) % 360) + left_longitude
        lon_indices = lon_data.argsort()
        lon_data = lon_data[lon_indices]
        # Identify jump in longitudes due to non-global dataset
        dlon_data = np.diff(lon_data)
        jump = np.where(dlon_data > 2 * dlon)[0]

        lons = ((self.lons - left_longitude) % 360) + left_longitude
        factors = []

        pressures = None
        if "air_pressure" not in self.data_vars:
            if units(self.vert_units).check("[pressure]"):
                pressures = np.log(convert_to(
                    self.vert_data[::-self.vert_order, np.newaxis],
                    self.vert_units, "Pa").repeat(len(self.lats), axis=1))
            else:
                raise ValueError(
                    "air_pressure must be available for linear plotting layers "
                    "with non-pressure axis. Please add to required_datafields.")

        # Make sure air_pressure is the first to be evaluated if needed
        variables = list(self.data_vars)
        if "air_pressure" in self.data_vars:
            if variables[0] != "air_pressure":
                variables.insert(0, variables.pop(variables.index("air_pressure")))

        for name in variables:
            var = self.data_vars[name]
            data[name] = []
            if len(var.shape) == 4:
                var_data = var[:][timestep, ::-self.vert_order, ::self.lat_order, :]
            else:
                var_data = var[:][timestep, np.newaxis, ::self.lat_order, :]
            LOGGER.debug("\tLoaded %.2f Mbytes from data field <%s> at timestep %s.",
                          var_data.nbytes / 1048576., name, timestep)
            LOGGER.debug("\tVertical dimension direction is %s.",
                          "up" if self.vert_order == 1 else "down")
            LOGGER.debug("\tInterpolating to cross-section path.")
            # Re-arange longitude dimension in the data field.
            var_data = var_data[:, :, lon_indices]
            if jump:
                LOGGER.debug("\tsetting jump data to NaN at %s", jump)
                var_data = var_data.copy()
                var_data[:, :, jump] = np.nan

            cross_section = coordinate.interpolate_vertsec(var_data, self.lat_data, lon_data, self.lats, lons)
            # Create vertical interpolation factors and indices for subsequent variables
            # TODO: Improve performance for this interpolation in general
            if len(factors) == 0:
                if name == "air_pressure":
                    pressures = np.log(convert_to(cross_section, self.data_units[name], "Pa"))
                for index_lonlat, alt in enumerate(np.log(self.alts)):
                    pressure = pressures[:, index_lonlat]
                    idx0 = None
                    for index_altitude in range(len(pressures) - 1):
                        if (pressure[index_altitude] <= alt <= pressure[index_altitude + 1]) or \
                           (pressure[index_altitude] >= alt >= pressure[index_altitude + 1]):
                            idx0 = index_altitude
                            break
                    if idx0 is None:
                        factors.append(((0, np.nan), (0, np.nan)))
                        continue

                    idx1 = idx0 + 1
                    fac1 = (pressure[idx0] - alt) / (pressure[idx0] - pressure[idx1])
                    fac0 = 1 - fac1
                    assert 0 <= fac0 <= 1, fac0
                    factors.append(((idx0, fac0), (idx1, fac1)))

            # Interpolate with the previously calculated pressure indices and factors
            for index, ((idx0, w0), (idx1, w1)) in enumerate(factors):
                value = cross_section[idx0, index] * w0 + cross_section[idx1, index] * w1
                data[name].append(value)

            # Free memory.
            del var_data
            data[name] = np.array(data[name])

        return data

    def plot(self):
        """
        """
        d1 = datetime.now()

        # Load and interpolate the data fields as required by the linear
        # section style instance. <data> is a dictionary containing the
        # interpolated curtains of the variables identified through CF
        # standard names as specified by <self.lsec_style_instance>.
        data = self._load_interpolate_timestep()
        d2 = datetime.now()

        if self.mime_type != "text/xml":
            raise RuntimeError(f"Unexpected format for linear sections '{self.mime_type}'.")

        # Call the plotting method of the linear section style instance.
        image = self.plot_object.plot_lsection(data, self.lats, self.lons,
                                               valid_time=self.fc_time,
                                               init_time=self.init_time)
        # Free memory.
        del data

        d3 = datetime.now()
        LOGGER.debug("Finished plotting (required time %s; total "
                      "time %s).\n", d3 - d2, d3 - d1)

        return image
