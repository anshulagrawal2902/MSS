# -*- coding: utf-8 -*-
"""

    mslib.msui.topview
    ~~~~~~~~~~~~~~~~~~

    Top view implementation for the msui.
    See the reference documentation, Supplement, for details on the
    implementation.

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

import functools

from mslib.utils.config import config_loader
from mslib.utils.get_projection_params import get_projection_params
from PyQt5 import QtGui, QtWidgets, QtCore
from mslib.msui.qt5 import ui_topview_window as ui
from mslib.msui.qt5 import ui_topview_mapappearance as ui_ma
from mslib.msui.viewwindows import MSUIMplViewWindow
from mslib.msui import wms_control as wc
from mslib.msui import satellite_dockwidget as sat
from mslib.msui import remotesensing_dockwidget as rs
from mslib.msui import kmloverlay_dockwidget as kml
from mslib.msui import airdata_dockwidget as ad
from mslib.msui import multiple_flightpath_dockwidget as mf
from mslib.msui import flighttrack as ft
from mslib.msui import autoplot_dockwidget as apd
from mslib.msui.icons import icons
from mslib.msui.flighttrack import Waypoint
from mslib.utils.colordialog import CustomColorDialog
from mslib.utils import LOGGER

# Dock window indices.
WMS = 0
SATELLITE = 1
REMOTESENSING = 2
KMLOVERLAY = 3
AIRDATA = 4
MULTIPLEFLIGHTPATH = 5
AUTOPLOT = 6


class MSUI_TV_MapAppearanceDialog(QtWidgets.QDialog, ui_ma.Ui_MapAppearanceDialog):
    """
    Dialog to set map appearance parameters. User interface is
    defined in "ui_topview_mapappearance.py".
    """
    signal_ft_vertices_color_change = QtCore.pyqtSignal(str, tuple)
    signal_line_thickness_change = QtCore.pyqtSignal(float)
    signal_line_style_change = QtCore.pyqtSignal(str)
    signal_transparency_change = QtCore.pyqtSignal(float)

    def __init__(self, parent=None, settings=None, wms_connected=False):
        """
        Arguments:
        parent -- Qt widget that is parent to this widget.
        settings -- dictionary containing topview options.
        """
        super().__init__(parent)
        self.setupUi(self)

        assert settings is not None
        settings["fill_waterbodies"] = True  # removing water bodies does not work properly

        self.wms_connected = wms_connected
        # check parent.wms_connected to disable cbFillWaterBodies and cbFillContinents
        if self.wms_connected:
            self.cbFillContinents.setChecked(False)
            self.cbFillWaterBodies.setChecked(False)
            self.cbFillContinents.setEnabled(False)
            self.cbFillContinents.setStyleSheet("color: black")
            self.cbFillWaterBodies.setStyleSheet("color: black")
        else:
            self.cbFillWaterBodies.setChecked(settings["fill_waterbodies"])
            self.cbFillWaterBodies.setEnabled(False)
            self.cbFillContinents.setChecked(settings["fill_continents"])
            self.cbFillContinents.setEnabled(True)

        self.cbDrawGraticule.setChecked(settings["draw_graticule"])
        self.cbDrawCoastlines.setChecked(settings["draw_coastlines"])
        self.cbDrawFlightTrack.setChecked(settings["draw_flighttrack"])
        self.cbDrawMarker.setChecked(settings["draw_marker"])
        self.cbLabelFlightTrack.setChecked(settings["label_flighttrack"])

        self.sbLineThickness.setValue(settings.get("line_thickness", 2))
        self.cbLineStyle.addItems(["Solid", "Dashed", "Dotted", "Dash-dot"])  # Item added in the list
        self.cbLineStyle.setCurrentText(settings.get("line_style", "Solid"))
        self.hsTransparencyControl.setValue(int(settings.get("line_transparency", 1.0) * 100))

        for button, ids in [(self.btWaterColour, "colour_water"),
                            (self.btLandColour, "colour_land"),
                            (self.btWaypointsColour, "colour_ft_waypoints"),
                            (self.btVerticesColour, "colour_ft_vertices")]:
            palette = QtGui.QPalette(button.palette())
            colour = QtGui.QColor()
            colour.setRgbF(*settings[ids])
            palette.setColor(QtGui.QPalette.Button, colour)
            button.setPalette(palette)

        # Connect colour button signals.
        self.btWaterColour.clicked.connect(functools.partial(self.setColour, "water"))
        self.btLandColour.clicked.connect(functools.partial(self.setColour, "land"))
        self.btWaypointsColour.clicked.connect(functools.partial(self.setColour, "ft_waypoints"))
        self.btVerticesColour.clicked.connect(functools.partial(self.setColour, "ft_vertices"))

        # Store values instead of emitting signals immediately
        self.line_thickness = settings.get("line_thickness", 2)
        self.line_style = settings.get("line_style", "Solid")
        self.line_transparency = settings.get("line_transparency", 1.0)

        self.sbLineThickness.valueChanged.connect(self.onLineThicknessChanged)
        self.cbLineStyle.currentTextChanged.connect(self.onLineStyleChanged)
        self.hsTransparencyControl.valueChanged.connect(self.onTransparencyChanged)

        # Shows previously selected element in the fontsize comboboxes as the current index.
        for i in range(self.tov_cbtitlesize.count()):
            if self.tov_cbtitlesize.itemText(i) == settings["tov_plot_title_size"]:
                self.tov_cbtitlesize.setCurrentIndex(i)

        for i in range(self.tov_cbaxessize.count()):
            if self.tov_cbaxessize.itemText(i) == settings["tov_axes_label_size"]:
                self.tov_cbaxessize.setCurrentIndex(i)

    def onLineThicknessChanged(self, value):
        self.line_thickness = value

    def onLineStyleChanged(self, value):
        self.line_style = value

    def onTransparencyChanged(self, value):
        self.line_transparency = value / 100.0

    def get_settings(self):
        """
        """
        settings = {
            "draw_graticule": self.cbDrawGraticule.isChecked(),
            "draw_coastlines": self.cbDrawCoastlines.isChecked(),
            "fill_waterbodies": self.cbFillWaterBodies.isChecked(),
            "fill_continents": self.cbFillContinents.isChecked(),
            "draw_flighttrack": self.cbDrawFlightTrack.isChecked(),
            "draw_marker": self.cbDrawMarker.isChecked(),
            "label_flighttrack": self.cbLabelFlightTrack.isChecked(),
            "tov_plot_title_size": self.tov_cbtitlesize.currentText(),
            "tov_axes_label_size": self.tov_cbaxessize.currentText(),
            "line_thickness": self.line_thickness,
            "line_style": self.line_style,
            "line_transparency": self.line_transparency,
            "colour_water":
                QtGui.QPalette(self.btWaterColour.palette()).color(QtGui.QPalette.Button).getRgbF(),
            "colour_land":
                QtGui.QPalette(self.btLandColour.palette()).color(QtGui.QPalette.Button).getRgbF(),
            "colour_ft_vertices":
                QtGui.QPalette(self.btVerticesColour.palette()).color(QtGui.QPalette.Button).getRgbF(),
            "colour_ft_waypoints":
                QtGui.QPalette(self.btWaypointsColour.palette()).color(QtGui.QPalette.Button).getRgbF(),
        }
        return settings

    def setColour(self, which):
        """
        Slot for the colour buttons: Opens a QColorDialog and sets the
        new button face colour.
        """
        if which == "water":
            button = self.btWaterColour
        elif which == "land":
            button = self.btLandColour
        elif which == "ft_vertices":
            button = self.btVerticesColour
        elif which == "ft_waypoints":
            button = self.btWaypointsColour

        dialog = CustomColorDialog(self)
        dialog.color_selected.connect(lambda color: self.on_color_selected(which, color, button))
        dialog.show()

    def on_color_selected(self, which, color, button):
        if color.isValid():
            self.signal_ft_vertices_color_change.emit(which, color.getRgbF())
            palette = QtGui.QPalette(button.palette())
            palette.setColor(QtGui.QPalette.Button, color)
            button.setPalette(palette)


class MSUITopViewWindow(MSUIMplViewWindow, ui.Ui_TopViewWindow):
    """
    PyQt window implementing a MapCanvas as an interactive flight track
    editor.
    """
    name = "Top View"

    signal_activate_flighttrack1 = QtCore.pyqtSignal(ft.WaypointsTableModel)
    signal_activate_operation = QtCore.pyqtSignal(int)
    signal_ft_vertices_color_change = QtCore.pyqtSignal(tuple)
    signal_operation_added = QtCore.pyqtSignal(int, str)
    signal_operation_removed = QtCore.pyqtSignal(int)
    signal_login_mscolab = QtCore.pyqtSignal(str, str)
    signal_logout_mscolab = QtCore.pyqtSignal()
    signal_listFlighttrack_doubleClicked = QtCore.pyqtSignal()
    signal_permission_revoked = QtCore.pyqtSignal(int)
    signal_render_new_permission = QtCore.pyqtSignal(int, str)
    sections_changed = QtCore.pyqtSignal(str)
    refresh_signal_emit = QtCore.pyqtSignal()
    refresh_signal_send = QtCore.pyqtSignal()
    item_selected = QtCore.pyqtSignal(str, str, str, str)
    itemSecs_selected = QtCore.pyqtSignal(str)
    vtime_vals = QtCore.pyqtSignal([list])

    def __init__(self, parent=None, mainwindow=None, model=None, _id=None,
                 active_flighttrack=None, mscolab_server_url=None, token=None, config_settings=None,
                 tutorial_mode=False):
        """
        Set up user interface, connect signal/slots.
        """
        super().__init__(parent, model, _id)
        LOGGER.debug(_id)
        self.settings_tag = "topview"
        self.tutorial_mode = tutorial_mode
        # ToDo review 2026 after EOL of Win 10 if we can use parent again
        self.mainwindow_signal_login_mscolab = mainwindow.signal_login_mscolab
        self.mainwindow_signal_logout_mscolab = mainwindow.signal_logout_mscolab
        self.mainwindow_signal_listFlighttrack_doubleClicked = mainwindow.signal_listFlighttrack_doubleClicked
        self.mainwindow_signal_activate_operation = mainwindow.signal_activate_operation
        self.mainwindow_signal_permission_revoked = mainwindow.signal_permission_revoked
        self.mainwindow_signal_render_new_permission = mainwindow.signal_render_new_permission
        self.mainwindow_signal_activate_flighttrack = mainwindow.signal_activate_flighttrack
        self.mainwindow_listFlightTracks = mainwindow.listFlightTracks
        self.mainwindow_filterCategoryCb = mainwindow.filterCategoryCb
        self.mainwindow_listOperationsMSC = mainwindow.listOperationsMSC

        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(icons('64x64')))

        # Dock windows [WMS, Satellite, Trajectories, Remote Sensing, KML Overlay, Multiple Flightpath]:
        self.docks = [None, None, None, None, None, None, None]

        # Initialise the GUI elements (map view, items of combo boxes etc.).
        self.setup_top_view()

        # Boolean to store active wms connection
        self.wms_connected = False

        # Store active flighttrack waypoint model
        self.active_flighttrack = active_flighttrack

        # Stores active mscolab operation id
        self.active_op_id = mainwindow.mscolab.active_op_id

        # Mscolab Server Url and token
        self.mscolab_server_url = mscolab_server_url
        self.token = token

        self.currurl = ""
        self.currlayer = ""
        self.currlevel = ""
        self.currstyles = ""
        self.currsections = ""
        self.currflights = ""
        self.curritime = ""
        self.currvtime = ""
        self.currlayerobj = None

        # Connect slots and signals.
        # ==========================
        # ToDo review 2026 after EOL of Win 10 if we can use parent again
        if mainwindow is not None:
            mainwindow.refresh_signal_connect.connect(self.refresh_signal_send.emit)

        # Map controls.
        self.btMapRedraw.clicked.connect(self.mpl.canvas.redraw_map)
        self.cbChangeMapSection.activated.connect(self.changeMapSection)

        # Settings
        self.btSettings.clicked.connect(self.open_settings_dialog)

        # Roundtrip
        self.btRoundtrip.clicked.connect(self.make_roundtrip)

        # Tool opener.
        self.cbTools.currentIndexChanged.connect(lambda ind: self.openTool(
            index=ind, parent=mainwindow, config_settings=config_settings))

        if mainwindow is not None:
            # Update flighttrack
            self.mainwindow_signal_activate_flighttrack.connect(self.update_active_flighttrack)
            self.mainwindow_signal_activate_operation.connect(self.update_active_operation)

            self.signal_operation_added.connect(self.add_operation_slot)
            self.signal_operation_removed.connect(self.remove_operation_slot)

            self.mainwindow_signal_login_mscolab.connect(self.login)

    def __del__(self):
        del self.mpl.canvas.waypoints_interactor

    @QtCore.pyqtSlot(ft.WaypointsTableModel)
    def update_active_flighttrack(self, active_flighttrack):
        """
        Slot that handles update of active flighttrack variable.
        """
        self.active_flighttrack = active_flighttrack
        self.signal_activate_flighttrack1.emit(active_flighttrack)

    @QtCore.pyqtSlot(int)
    def update_active_operation(self, active_op_id):
        self.active_op_id = active_op_id
        self.signal_activate_operation.emit(self.active_op_id)

    @QtCore.pyqtSlot(int, str)
    def add_operation_slot(self, op_id, path):
        self.signal_operation_added.emit(op_id, path)

    @QtCore.pyqtSlot(int)
    def remove_operation_slot(self, op_id):
        self.signal_operation_removed.emit(op_id)

    @QtCore.pyqtSlot(str, str)
    def login(self, mscolab_server_url, token):
        self.mscolab_server_url = mscolab_server_url
        self.token = token
        self.signal_login_mscolab.emit(mscolab_server_url, token)

    def setup_top_view(self):
        """
        Initialise GUI elements. (This method is called before signals/slots
        are connected).
        """
        toolitems = ["(select to open control)", "Web Map Service", "Satellite Tracks", "Remote Sensing",
                     "KML Overlay", "Airports/Airspaces", "Multiple Flightpath", "Autoplot"]
        self.cbTools.clear()
        self.cbTools.addItems(toolitems)

        # Fill combobox for predefined map sections.
        self.update_predefined_maps()

        # Initialise the map and the flight track. Get the initial projection
        # parameters from the tables in msui_settings.
        kwargs = self.changeMapSection(only_kwargs=True)
        self.mpl.canvas.init_map(**kwargs)
        self.setFlightTrackModel(self.waypoints_model)

        # Automatically enable or disable roundtrip when data changes
        self.waypoints_model.dataChanged.connect(self.update_roundtrip_enabled)
        self.update_roundtrip_enabled()
        self.mpl.navbar.push_current()

        self.openTool(WMS + 1)

    def update_predefined_maps(self, extra=None):
        current_map_key = self.cbChangeMapSection.currentText()
        self.cbChangeMapSection.clear()
        predefined_map_sections = config_loader(
            dataset="predefined_map_sections")
        self.cbChangeMapSection.addItems(sorted(predefined_map_sections.keys()))
        if extra is not None and len(extra) > 0:
            self.cbChangeMapSection.insertSeparator(self.cbChangeMapSection.count())
            self.cbChangeMapSection.addItems(sorted(extra))
        # set initial map key again
        if current_map_key in predefined_map_sections.keys():
            self.cbChangeMapSection.setCurrentText(current_map_key)

    def openTool(self, index, parent=None, config_settings=None):
        """
        Slot that handles requests to open control windows.
        """
        index = self.controlToBeCreated(index)
        if index >= 0:
            if index == WMS:
                # Create a new WMSDockWidget.
                title = "Web Map Service (Top View)"
                widget = wc.HSecWMSControlWidget(
                    default_WMS=config_loader(dataset="default_WMS"),
                    view=self.mpl.canvas,
                    wms_cache=config_loader(dataset="wms_cache"))
                widget.vtime_data.connect(lambda vtime: self.valid_time_vals(vtime))
                widget.base_url_changed.connect(lambda url: self.url_val_changed(url))
                widget.layer_changed.connect(lambda layer: self.layer_val_changed(layer))
                widget.on_level_changed.connect(lambda level: self.level_val_changed(level))
                widget.styles_changed.connect(lambda styles: self.styles_val_changed(styles))
                widget.itime_changed.connect(lambda styles: self.itime_val_changed(styles))
                widget.vtime_changed.connect(lambda styles: self.vtime_val_changed(styles))
                self.item_selected.connect(lambda url, layer, style,
                                           level: widget.row_is_selected(url, layer, style, level, "top"))
                self.itemSecs_selected.connect(lambda vtime: widget.leftrow_is_selected(vtime))
                widget.signal_disable_cbs.connect(self.disable_cbs)
                widget.signal_enable_cbs.connect(self.enable_cbs)
            elif index == SATELLITE:
                title = "Satellite Track Prediction"
                widget = sat.SatelliteControlWidget(parent=self, view=self.mpl.canvas)
            elif index == REMOTESENSING:
                title = "Remote Sensing Tools"
                widget = rs.RemoteSensingControlWidget(parent=self, view=self.mpl.canvas)
            elif index == KMLOVERLAY:
                title = "KML Overlay"
                widget = kml.KMLOverlayControlWidget(parent=self, view=self.mpl.canvas)
            elif index == AIRDATA:
                title = "Airdata"
                widget = ad.AirdataDockwidget(parent=self, view=self.mpl.canvas)
            elif index == MULTIPLEFLIGHTPATH:
                title = "Multiple Flightpath"
                widget = mf.MultipleFlightpathControlWidget(parent=self, view=self.mpl.canvas,
                                                            listFlightTracks=self.mainwindow_listFlightTracks,
                                                            listOperationsMSC=self.mainwindow_listOperationsMSC,
                                                            category=self.mainwindow_filterCategoryCb,
                                                            activeFlightTrack=self.active_flighttrack,
                                                            active_op_id=self.active_op_id,
                                                            mscolab_server_url=self.mscolab_server_url,
                                                            token=self.token)

                self.mainwindow_signal_logout_mscolab.connect(self.signal_logout_mscolab.emit)
                self.mainwindow_signal_listFlighttrack_doubleClicked.connect(
                    lambda: self.signal_listFlighttrack_doubleClicked.emit())
                self.mainwindow_signal_permission_revoked.connect(
                    lambda op_id: self.signal_permission_revoked.emit(op_id))
                self.mainwindow_signal_render_new_permission.connect(
                    lambda op_id, path: self.signal_render_new_permission.emit(op_id, path))
                if self.active_op_id is not None:
                    self.signal_activate_operation.emit(self.active_op_id)
            elif index == AUTOPLOT:
                title = "Autoplot (Top View)"
                widget = apd.AutoplotDockWidget(parent=self, parent2=parent,
                                                view="Top View", config_settings=config_settings)
                widget.treewidget_item_selected.connect(
                    lambda url, layer, style, level: self.tree_item_select(url, layer, style, level))
                widget.autoplot_treewidget_item_selected.connect(
                    lambda section, vtime: self.treePlot_item_select(section, vtime))
                widget.update_op_flight_treewidget.connect(
                    lambda opfl, flight: parent.update_treewidget_op_fl(opfl, flight))
            else:
                raise IndexError("invalid control index")

            # Create the actual dock widget containing <widget>.
            self.createDockWidget(index, title, widget)

    @QtCore.pyqtSlot()
    def disable_cbs(self):
        self.wms_connected = True

    @QtCore.pyqtSlot()
    def enable_cbs(self):
        self.wms_connected = False

    @QtCore.pyqtSlot()
    def tree_item_select(self, url, layer, style, level):
        self.item_selected.emit(url, layer, style, level)

    @QtCore.pyqtSlot()
    def treePlot_item_select(self, section, vtime):
        self.cbChangeMapSection.setCurrentText(section)
        self.changeMapSection()
        self.itemSecs_selected.emit(vtime)

    @QtCore.pyqtSlot()
    def url_val_changed(self, strr):
        self.currurl = strr

    @QtCore.pyqtSlot()
    def valid_time_vals(self, vtimes_list):
        self.vtime_vals.emit(vtimes_list)

    @QtCore.pyqtSlot()
    def layer_val_changed(self, strr):
        self.currlayerobj = strr
        layerstring = str(strr)
        second_colon_index = layerstring.find(':', layerstring.find(':') + 1)
        self.currurl = layerstring[:second_colon_index].strip() if second_colon_index != -1 else layerstring.strip()
        self.currlayer = layerstring.split('|')[1].strip() if '|' in layerstring else None

    @QtCore.pyqtSlot()
    def level_val_changed(self, strr):
        self.currlevel = strr.split(' ')[0]

    @QtCore.pyqtSlot()
    def styles_val_changed(self, strr):
        if strr is None or not str(strr).strip():
            self.currstyles = ""
        else:
            split_strr = str(strr).strip().split()
            self.currstyles = split_strr[0].strip() if split_strr else ""

    @QtCore.pyqtSlot()
    def itime_val_changed(self, strr):
        self.curritime = strr

    @QtCore.pyqtSlot()
    def vtime_val_changed(self, strr):
        self.currvtime = strr

    def changeMapSection(self, index=0, only_kwargs=False):
        """
        Change the current map section to one of the predefined regions.
        """
        # Get the initial projection parameters from the tables in msui_settings.
        current_map_key = self.cbChangeMapSection.currentText()
        predefined_map_sections = config_loader(
            dataset="predefined_map_sections")
        current_map = predefined_map_sections.get(
            current_map_key, {"CRS": current_map_key, "map": {}})

        if current_map["CRS"] != "":
            proj_params = get_projection_params(current_map["CRS"])
            # Create a keyword arguments dictionary for basemap that contains
            # the projection parameters.
            kwargs = dict(current_map["map"])
            kwargs.update({"CRS": current_map["CRS"], "BBOX_UNITS": proj_params["bbox"],
                           "OPERATION_NAME": self.waypoints_model.name})
            kwargs.update(proj_params["basemap"])

            if only_kwargs:
                # Return kwargs dictionary and do NOT redraw the map.
                return kwargs

            LOGGER.debug("switching to map section '%s' - '%s'", current_map_key, kwargs)
            self.mpl.canvas.redraw_map(kwargs)
            self.mpl.navbar.clear_history()

    def setIdentifier(self, identifier):
        super().setIdentifier(identifier)
        self.mpl.canvas.map.set_identifier(identifier)

    def open_settings_dialog(self):
        """
        Open the map appearance settings dialog.
        """
        settings = self.getView().get_settings()
        dlg = MSUI_TV_MapAppearanceDialog(parent=self, settings=settings, wms_connected=self.wms_connected)
        dlg.setModal(False)
        dlg.signal_ft_vertices_color_change.connect(self.set_ft_vertices_color)
        dlg.signal_line_thickness_change.connect(self.set_line_thickness)  # Connect to signal
        dlg.signal_line_style_change.connect(self.set_line_style)
        dlg.signal_transparency_change.connect(self.set_line_transparency)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            settings = dlg.get_settings()
            self.set_line_thickness(settings["line_thickness"])
            self.set_line_style(settings["line_style"])
            self.set_line_transparency(settings["line_transparency"])
            self.getView().set_settings(settings, save=True)
            self.mpl.canvas.waypoints_interactor.redraw_path()
        dlg.destroy()

    def set_line_thickness(self, thickness):
        """Set the line thickness of the flight track."""
        self.mpl.canvas.waypoints_interactor.set_line_thickness(thickness)

    def set_line_style(self, style):
        """Set the line style of the flight track"""
        self.mpl.canvas.waypoints_interactor.set_line_style(style)

    def set_line_transparency(self, transparency):
        """Set the line transparency of the flight track"""
        self.mpl.canvas.waypoints_interactor.set_line_transparency(transparency)

    @QtCore.pyqtSlot(str, tuple)
    def set_ft_vertices_color(self, which, color):
        if which == "ft_vertices":
            self.signal_ft_vertices_color_change.emit(color)

    def make_roundtrip(self):
        """
        Copies the first waypoint and inserts it at the back of the list again
        Essentially creating a roundtrip
        """
        # This case should never be True for users, but might be for developers at some point
        if not self.is_roundtrip_possible():
            return

        first_waypoint = self.waypoints_model.waypoint_data(0)

        self.waypoints_model.insertRows(self.waypoints_model.rowCount(), rows=1, waypoints=[
            Waypoint(lat=first_waypoint.lat, lon=first_waypoint.lon, flightlevel=first_waypoint.flightlevel,
                     location=first_waypoint.location)])

    def is_roundtrip_possible(self):
        """
        Checks if there are at least 2 waypoints, and the first and last are not the same
        """
        condition = self.waypoints_model.rowCount() > 1

        if condition:
            first_waypoint = self.waypoints_model.waypoint_data(0)
            last_waypoint = self.waypoints_model.waypoint_data(self.waypoints_model.rowCount() - 1)

            condition = ((first_waypoint.lat != last_waypoint.lat) or
                         (first_waypoint.lon != last_waypoint.lon) or
                         (first_waypoint.flightlevel != last_waypoint.flightlevel))

        return bool(condition)

    def update_roundtrip_enabled(self):
        self.btRoundtrip.setEnabled(self.is_roundtrip_possible())
