# -*- coding: utf-8 -*-
"""

    mslib.msui.viewindows
    ~~~~~~~~~~~~~~~~~~~~~

    Common PyQt-derived classes and methods required by all msui ui
    modules.

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

from abc import abstractmethod

from PyQt5 import QtCore, QtWidgets
from mslib.utils.config import save_settings_qsettings
from mslib.utils import LOGGER


class MSUIViewWindow(QtWidgets.QMainWindow):
    """
    Derives QMainWindow to provide some common functionality to all
    MSUI view windows.
    """
    name = "Abstract MSS View Window"
    identifier = None

    viewCloses = QtCore.pyqtSignal(name="viewCloses")
    # views for mscolab
    # viewClosesId = QtCore.pyqtSignal(int, name="viewClosesId")

    def __init__(self, parent=None, model=None, _id=None):
        super().__init__(parent)

        # Object variables:
        self.waypoints_model = model  # pointer to the current flight track.

        # List that accommodates the dock window instances: Needs to be defined
        # in proper size in derived classes!
        self.docks = []

        # # emit _id if not none
        # logging.debug(_id)
        # self._id = _id
        # Used to force close window without the dialog popping up
        self.force_close = False
        # Flag variable to check whether tableview window exists or not.
        self.tv_window_exists = True

    def handle_force_close(self):
        self.force_close = True
        self.close()

    def closeEvent(self, event):
        """
        If force_close is True then close window without dialog
        else ask user if he/she wants to close the window.

        Overloads QtGui.QMainWindow.closeEvent(). This method is called if
        Qt receives a window close request for our application window.
        """
        if self.force_close:
            ret = QtWidgets.QMessageBox.Yes
        else:
            ret = QtWidgets.QMessageBox.warning(self, self.tr("Mission Support System"),
                                                self.tr(f"Do you want to close this {self.name}?"),
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)

        if ret == QtWidgets.QMessageBox.Yes:
            # if self._id is not None:
            #     self.viewClosesId.emit(self._id)
            #     logging.debug(self._id)
            # sets flag as False which shows tableview window had been closed.
            self.tv_window_exists = False
            self.viewCloses.emit()
            event.accept()
        else:
            event.ignore()

    def exists(self):
        """
        Returns the flag False if self.closeEvent() is triggered else returns True.
        This is only for helping as a flag information in
        force closing of tableview when main window closes.
        """
        return self.tv_window_exists

    def setFlightTrackModel(self, model):
        """
        Set the QAbstractItemModel instance that the view displays.
        """
        # Update title flighttrack name
        if self.waypoints_model:
            self.setWindowTitle(self.windowTitle().replace(self.waypoints_model.name, model.name))

        self.waypoints_model = model

    def controlToBeCreated(self, index):
        """
        Check if the dock widget at index <index> exists. If yes, show
        the widget and return -1. Otherwise return <index-1>.
        """
        index -= 1
        if index >= 0 and self.docks[index] is not None:
            # The widget has already been created, but is not visible at
            # the moment.
            self.docks[index].show()
            self.docks[index].raise_()
            index = -1
        if hasattr(self, "cbTools"):
            self.cbTools.setCurrentIndex(0)
        return index

    def createDockWidget(self, index, title, widget):
        """
        Create a new dock widget. A pointer to the dock widget will be
        stored in self.docks[index]. The dock will have the title <title>
        and contain the Qt widget <widget>.
        """
        self.docks[index] = QtWidgets.QDockWidget(title, self)
        self.docks[index].setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        # setWidget transfers the widget's ownership to Qt -- no setParent()
        # call is necessary:
        self.docks[index].setWidget(widget)

        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.docks[index])

        # Check if another dock widget occupies the dock area. If yes,
        # tabbify the old and the new widget.
        for dock in self.docks:
            if dock and not dock == self.docks[index] and not dock.isFloating():
                self.tabifyDockWidget(dock, self.docks[index])
                break
        self.docks[index].show()
        self.docks[index].raise_()

    @abstractmethod
    def getView(self):
        """
        Return view object that tools can interact with.

        ABSTRACT method, needs to be implemented in derived classes.
        """
        return None

    def setIdentifier(self, identifier):
        self.identifier = identifier

    def enable_navbar_action_buttons(self):
        """
        function enables some control, used if access_level is appropriate
        """
        if self.name in ("Top View", "Table View"):
            # Make Roundtrip Button
            self.btRoundtrip.setEnabled(self.is_roundtrip_possible())
        if self.name in ("Top View", "Side View", "Linear View"):
            actions = self.mpl.navbar.actions()
            for action in actions:
                action_text = action.text()
                if action_text in ("Ins WP", "Del WP", "Mv WP"):
                    action.setEnabled(True)
        else:
            # Table View
            self.btAddWayPointToFlightTrack.setEnabled(True)
            self.btCloneWaypoint.setEnabled(True)
            self.btDeleteWayPoint.setEnabled(True)
            self.btInvertDirection.setEnabled(True)
            self.cbTools.setEnabled(True)
            self.tableWayPoints.setEnabled(True)

    def disable_navbar_action_buttons(self):
        """
        function disables some control, used if access_level is not appropriate
        """
        if self.name in ("Top View", "Table View"):
            # Make Roundtrip Button
            self.btRoundtrip.setEnabled(False)
        if self.name in ("Top View", "Side View", "Linear View"):
            actions = self.mpl.navbar.actions()
            for action in actions:
                action_text = action.text()
                if action_text in ("Ins WP", "Del WP", "Mv WP"):
                    action.setEnabled(False)
                    if str(self.mpl.navbar.mode) == "insert waypoint" and action_text == "Ins WP":
                        action.trigger()
                    elif str(self.mpl.navbar.mode) == "delete waypoint" and action_text == "Del WP":
                        action.trigger()
                    elif str(self.mpl.navbar.mode) == "move waypoint" and action_text == "Mv WP":
                        action.trigger()
        else:
            # Table View
            self.btAddWayPointToFlightTrack.setEnabled(False)
            self.btCloneWaypoint.setEnabled(False)
            self.btDeleteWayPoint.setEnabled(False)
            self.btInvertDirection.setEnabled(False)
            self.cbTools.setEnabled(False)
            self.tableWayPoints.setEnabled(False)

    def changeEvent(self, event):
        """
        Change event method

        This method is called when a change event is triggered for the linearview, tableview, topview, sideview widget.
        It is an overridden method of the QWidget class.

        Parameters:
        :event: The QEvent object representing the change event.
        """
        if self.tutorial_mode:
            top_left = self.mapToGlobal(QtCore.QPoint(0, 0))
            if top_left.x() != 0:
                os_screen_region = (top_left.x(), top_left.y(), self.width(), self.height())
                settings = {'os_screen_region': os_screen_region}
                # we have to save this to reuse it by the tutorials
                save_settings_qsettings(self.settings_tag, settings)
            QtWidgets.QWidget.changeEvent(self, event)

    def moveEvent(self, event):
        """
        Move event method

        This method is called when a move event is triggered for the linearview, tableview, topview, sideview widget.
        It is an overridden method of the QWidget class.

        Parameters:
        :event: The QEvent object representing the move event.
        """
        if self.tutorial_mode:
            top_left = self.mapToGlobal(QtCore.QPoint(0, 0))
            if top_left.x() != 0:
                os_screen_region = (top_left.x(), top_left.y(), self.width(), self.height())
                settings = {'os_screen_region': os_screen_region}
                # we have to save this to reuse it by the tutorials
                save_settings_qsettings(self.settings_tag, settings)
            QtWidgets.QWidget.moveEvent(self, event)


class MSUIMplViewWindow(MSUIViewWindow):
    """
    Adds Matplotlib-specific functionality to MSUIViewWindow.
    """

    def __init__(self, parent=None, model=None, _id=None):
        super().__init__(parent, model, _id)
        LOGGER.debug(_id)
        self.mpl = None

    def setFlightTrackModel(self, model):
        """
        Set the QAbstractItemModel instance that the view displays.
        """
        super().setFlightTrackModel(model)

        if self.mpl is not None:
            self.mpl.canvas.set_waypoints_model(model)

            # Update Top View flighttrack name
            if hasattr(self.mpl.canvas, "map"):
                self.mpl.canvas.map.ax.figure.suptitle(f"{model.name}", x=0.95, ha='right')
                self.mpl.canvas.map.ax.figure.canvas.draw()

            elif hasattr(self.mpl.canvas, 'plotter'):
                self.mpl.canvas.plotter.fig.suptitle(f"{model.name}", x=0.95, ha='right')
                self.mpl.canvas.plotter.fig.canvas.draw()

    def getView(self):
        """
        Return the MplCanvas instance of the window.
        """
        return self.mpl.canvas
