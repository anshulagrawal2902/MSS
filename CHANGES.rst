Changelog
=========


Version 9.3.1
~~~~~~~~~~~~~
Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/110?closed=1

Version 9.3.0
~~~~~~~~~~~~~
Bug fix release and minor enhancements:
We removed unused modules from the mscolab saml2 setup.

All changes:
https://github.com/Open-MSS/MSS/milestone/108?closed=1

Version 9.2.0
~~~~~~~~~~~~~

Bug fix release and minor enhancements:
We added a verification for xml data and changed the startup of the SocketsManager.

All changes:
https://github.com/Open-MSS/MSS/milestone/106?closed=1


Version 9.1.0
~~~~~~~~~~~~~

Bug fix release and minor enhancements:
We have corrected spelling mistakes

All changes:
https://github.com/Open-MSS/MSS/milestone/105?closed=1

Version 9.0.0
~~~~~~~~~~~~~

Nilupul Manodya implemented SAML 2.0 (Security Assertion Markup Language) Authentication.
MSColab can now be configured with an existing IdP or multiple IdPs.
In this way, a user can authenticate themselves in one system and gain access to another system
by providing proof of authentication. In our documentation in the Components section you find a detailed description.

Matthias Riße refactored the test suite and optimized and accelerated our CI test runs.
All tests run in parallel now and are not retried upon failure, and most tests are also executed in a randomized order,
instilling more confidence in the results.
Quite a bit of duplicated code was unified, mostly using pytest fixtures.
Additionally, CI test runs now also happen on x86_64- and ARM-based macOS.

Jörn Ungermann refactored various parts of MSColab for faster processing with fewer requests.

Reimar Bauer refactored the tutorials and the documentation shows now mp4 files embedded in html5.


HINT:
~~~~~
The syntax of the server configuration of MSColab and MSWMS has changed. We removed the class definition.
For MSColab we have added new configuration options related to SAML2.
The change on the MSColab server also required changes on the MSUI handling the MSColab login. These changes are
not backwards compatible. MSColab Server and MSUI Client must use versions >=9.0.0.
We introduced a MSCOLAB_auth_user_name in the users configuration which simplifies the login process.

All changes:
https://github.com/Open-MSS/MSS/milestone/93?closed=1


Version 8.3.5
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/104?closed=1

Version 8.3.4
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/102?closed=1

Version 8.3.3
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/101?closed=1

Fixes for msmws and mscolab:
details: https://www.cve.org/CVERecord?id=CVE-2024-25123
- security: fix potential path manipulation in the server sources


Version 8.3.2
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/100?closed=1


Version 8.3.1
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/99?closed=1

Version 8.3.0
~~~~~~~~~~~~~

Bug fix release and minor enhancements:
We improved the KML docking widget feature

All changes:
https://github.com/Open-MSS/MSS/milestone/98?closed=1

Version 8.2.0
~~~~~~~~~~~~~

Bug fix release and minor enhancements:

HINT:
~~~~~
We introduced to use an Operation members list for user management.
The default of the GROUP_POSTFIX is "Group" for a given category.
For example if your category is Tex and you have an operation named TexGroup
then all users defined in this operation will become inherited into any new
operation of the category Tex.
Also when an user with admin role changes users in the TexGroup operation,
then all operations of that Tex category will update their users.

All changes:
https://github.com/Open-MSS/MSS/milestone/97?closed=1

Version 8.1.1
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/96?closed=1

Version 8.1.0
~~~~~~~~~~~~~

We renamed in the UI for operations the misleading active/inactive to archive and unarchive.
On start of MSUI an old user configuration can get backuped and saved updated to the new syntax.

All changes:
https://github.com/Open-MSS/MSS/milestone/95?closed=1

Version 8.0.1
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/94?closed=1

Version 8.0.0
~~~~~~~~~~~~~

Sreelakshmi Jayarajan created a new CLI module for automated plotting by an user
and refactored existing plotting and QT based classes modules.
These classes can be used for plotting purposes without
involving QT-based GUI and Interactive functionalities.
Users can retrieve a set of plots for several flights or hundreds of time-steps
during post-campaign analysis or when compiling an overview over flights of a campaign
for a daily briefing.
This allows users to retrieve similar plots of the same parameters
such as map section, level etc., on a daily basis.
The initial idea stems from Jörn Ungermann. GSoC mentors were Reimar Bauer, Jörn Ungermann, Christian Rolf, Sonja Gisinger


Jatin Jain did UI and server improvements in his GSoC project.
Users can now, compare and plot multiple flightpaths on topview.
This feature can be used for flightpathes or MSColab operations.
A fligthpath style width can be changed.
Timestamps are displayed below each message in MSColab.
Mscolab Operations in use for more than 30 days, move to an inactive list.
The initial idea for multiple flightpaths on topview stems from bkirbus.
GSoC mentors were Reimar Bauer, Jörn Ungermann, Sonja Gisinger

With MSS 8.0.0 we base our installation on miniforge. This has
mamba in the base environment. Mambaforge is discouraged of September 2023.

All changes:
https://github.com/Open-MSS/MSS/milestone/81?closed=1

Version 7.0.8
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/92?closed=1

Version 7.0.7
~~~~~~~~~~~~~

Bug fix release:

All changes:
https://github.com/Open-MSS/MSS/milestone/91


Version 7.0.6
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/90?closed=1


Version 7.0.5
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/89?closed=1


Version 7.0.4
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/88?closed=1



Version 7.0.3
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/87?closed=1


Version 7.0.2
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/86?closed=1


Version 7.0.1
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/84?closed=1


Version 7.0.0
~~~~~~~~~~~~~

This is a refactoring release for consistent nameings.
Over the last six years MSS has grown and we created the Open-MSS organization with the move to github in 2021.
In this we have many repositories that support our work on the Mission Support System.
We use the term MSS for the whole thing today.
Therefore, we would like to give more appropriate names to the individual components.

HINT:
~~~~~

We changed:
- command mss was renamed to msui
- constants.MSS_CONFIG_PATH to constants.MSUI_CONFIG_PATH
- constants.MSS_SETTINGS to constants.MSUI_SETTINGS
- class MissionSupportSystemDefaultConfig to class MSUIDefaultConfig
- class MSS_AboutDialog to class class MSUI_AboutDialog
- class MSS_LV_Options_Dialog to class MSUI_LV_Options_Dialog
- class MSS_PerformanceSettingsWidget to class MSUI_PerformanceSettingsWidget
- class MSS_ShortcutsDialog to class MSUI_ShortcutsDialog
- class MSS_SV_OptionsDialog to class MSUI_SV_OptionsDialog
- class MSS_TV_MapAppearanceDialog to class MSUI_TV_MapAppearanceDialog
- class MSSLinearViewWindow to class MSUILinearViewWindow
- class MSSMainWindow to class MSUIMainWindow
- class MSSMplViewWindow to class MSUIMplViewWindow
- class MSSMscolab to class MSUIMscolab
- class MSSSideViewWindow to class MSUISideViewWindow
- class MSSTableViewWindow to class MSUITableViewWindow
- class MSSTopViewWindow to class MSUITopViewWindow
- class MSSWebMapService to class MSUIWebMapService

Configurations:
- Env var MSS_CONFIG_PATH to MSUI_CONFIG_PATH
- directory for msui_settings.json from ~/.config/mss to ~/.config/msui
- mss_settings.json to msui_settings.json
- mss_wms_settings.py to mswms_settings.py
- mss_wms_auth.py to mswms_auth.py
- mss_mscolab_auth.py to mscolab_auth.py

We moved:
- mslib.msui.mss_qt to mslib.utils.qt
- mslib.msui.mss_pyui to mslib.msui.msui

All changes:
https://github.com/Open-MSS/MSS/milestone/68?closed=1

Version 6.2.1
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/82?closed=1

Version 6.2.0
~~~~~~~~~~~~~

This release includes the use of the new basemap-1.3.3 release and enables packaging for python 3.10.x.
We added the possibility of flight level as vertical coordinate.
A user can now leave on his own an operation.


All changes:
https://github.com/Open-MSS/MSS/milestone/80?closed=1


Version 6.1.1
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/78?closed=1


Version 6.1.0
~~~~~~~~~~~~~

This release includes some small improvements of the usablity.
A few bug fixes, a new plugin for NAVAID waypoints is described and
mscolab gots few improvements for user creation.
Wind speed plots can now be created for altitudes > 25km.

All changes:
https://github.com/Open-MSS/MSS/milestone/70?closed=1


Version 6.0.6
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/76?closed=1


Version 6.0.5
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/74?closed=1

Version 6.0.4
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/73?closed=1


Version 6.0.3
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/72?closed=1


Version 6.0.2
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/71?closed=1

Version 6.0.1
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/69?closed=1


Version 6.0.0
~~~~~~~~~~~~~

Aravind Murali redesigned in google summer of code 2021 the MSUI interface.
This now connects in a user-friendly way the editing of flight paths locally
or remotely with other users. Many of Jörn Ungermann's ideas were implemented.
In addition, Aravind Murali has improved a configuration editor for our json mss_settings file
and made this user-friendly. The initial idea of the new editor stems from Reimar Bauer.
GSoC mentors were Jörn Ungermann, May Bär, Reimar Bauer

Hrithik Kumar Verma developed a toolchain for the automatic creation of tutorials
in the Google Summer of Code 2021. This simplifies the creation of video tutorials in
a similar way to updating tests. Using these tutorial scripts to create videos
also increases test coverage. The initial idea stems from Reimar Bauer.
GSoC mentors were Reimar Bauer, May Bär

Jörn Ungermann improved kml visualizing the same way as of a flightpath.

Reimar Bauer improved permissions, projects and signalling for mscolab.

All changes:
https://github.com/Open-MSS/MSS/milestone/50?closed=1

Version 5.0.2
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/66?closed=1

Version 5.0.1
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/64?closed=1

Version 5.0.0
~~~~~~~~~~~~~

This release brings many improvements to the WMS Server along with new features for the UI.
May Bär implemented a gallery feature. On demand a WMS server can show what kind of view graphics
are provided.
Optional the source for creating the graphics can be published over the web service too.
By this any existing server shows examples how to create graphics. Have a look on
our documentation on https://mss.readthedocs.io/en/stable/gallery/index.html for this feature.

The linear styles got improved to work also on .ml files

We refactored some of our oldest code in thermolib and moved to the famous metpy module.
A new docking widget for topview was introduced for integrating airbase data by openaip.net and ourairports.com

Newer versions than 5.0.0 can now use the built-in update feature on command line or by the UI.

All changes:
https://github.com/Open-MSS/MSS/milestone/59?closed=1

Version 4.0.4
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/63?closed=1

Version 4.0.3
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/62?closed=1

Version 4.0.2
~~~~~~~~~~~~~

Bug fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/60?closed=1

Version 4.0.1
~~~~~~~~~~~~~

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/58?closed=1

Version 4.0.0
-------------

This release brings a new view mode of 1-D samples along the flight path.
Also in sideview waypoint symbols and corresponding vertical lines can be switched off.
A lot of UI improvements, e.g. import and export filters, topview history and home button implemented
for steorographic projections

HINT:
~~~~~

For using the 1-D samples along the flight path you have to add a configuration to your
mss_wms_settings.py. Similar as to the other layers add:

.. code-block:: python

  register_linear_layers = None
  if mpl_lsec_styles is not None:
      register_linear_layers = [
          # ECMWF standard 1D section styles.
          (mpl_lsec_styles.LS_DefaultStyle, "air_temperature", ["ecmwf_EUR_LL015"]),
          (mpl_lsec_styles.LS_DefaultStyle, "divergence_of_wind", ["ecmwf_EUR_LL015"]),
      ]


All changes:
https://github.com/Open-MSS/MSS/milestone/52?closed=1


Version 3.0.4
-------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/57?closed=1

Version 3.0.3
-------------

Bug Fix release

* Security fix: viewers were able to store attachments within the chat and could undo flightpathes. #43f7fab10b0ae57c2747de94f39df08535d52cad
* Security fix: omit recording of the token. #9afc5b4768817b4cd8dceca7201a4f1ebc331944


All changes:
https://github.com/Open-MSS/MSS/milestone/56?closed=1


Version 3.0.2
-------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/55?closed=1

Version 3.0.1
-------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/54?closed=1


Version 3.0.0
-------------
May Bär implemented multilayer support for the Server and Client. By this
Layers have a selectable priority in which they will be displayed. The multilayers
are searchable and filterable. Layer parameters can be synchronized.
The used style of each layer is persistently stored.
The selection of layers is supported by favorization.


Hint:
~~~~~
With version 3.0.0 we change our default channel order.
conda-forge is now sorted before defaults.


All changes:
https://github.com/Open-MSS/MSS/milestone/3?closed=1


Version 2.0.4
-------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/51?closed=1

Version 2.0.3
-------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/49?closed=1

Version 2.0.2
-------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/48?closed=1

Version 2.0.1
---------------

Bug Fix release

All changes:
https://github.com/Open-MSS/MSS/milestone/47?closed=1

Version 2.0.0
-------------

Shivashis Padhi created the fundament for a collaboration server in the
MSS project in google summer of code 2019.
Tanish Grover continued this work in the google summer of code 2020 and
overworked our user interface. The initial idea of mscolab stems from Reimar Bauer.
GSoC mentors were Reimar Bauer and Jörn Ungermann.
In addition to the mswms server the project now has a mscolab server for editing a flight path.

Vaibhav Mehra has integrated an editor for the MSS setting file.

The KML docking widget was improved in google summer of code 2020 by Aryan Gupta.
GSoC mentors were Jörn Ungermann and Christian Rolf. Initial idea of the project by Jörn Ungermann.

All changes:
https://github.com/Open-MSS/MSS/milestone/7

Version 1.9.5
-------------

Bug Fixes:
  - SPDX Identifiers in meta.yaml, #569
  - AttributeError: 'datetime.timezone' object has no attribute 'localize', #568

Version 1.9.4
-------------

Bug Fixes:
  - AttributeError: 'datetime.timezone' object has no attribute 'localize', #568
  - rename in rtfd docs env into envs, #565
  - mss performance ceiling altitude feature not properly documented, #557

Other Changes:
  - enable configurable timeout of openUrl, #567

Version 1.9.3
-------------

Bug Fixes:
  - tests failing on OSX, #549
  - fixate socketio and engineio, #546
  - Revoking permission does not remove project from revoked user's mscolab project window, #538

Version 1.9.2
-------------

Bug Fixes:
  - replace xml.etree.ElementTree, #542
  - flake8 3.5.0 has better tests, #541
  - update doc samples compare with mswms demodata, #540
  - Error in handling project permission update in mscolab, #539
  - mscolab: Selected Project highlight removed if new project is added, #533
  - GUI tests fail in OSX, #531
  - developer hint separate data from source, #529
  - PyVirtualDisplay Package not found for Windows OS, #527
  - sync our meta.yaml with the one on conda-forge, #526
  - improve "Building a development environment", #524
  - Mscolab on first connection gives error, #523
  - server vhost documentation home directory wrong path, #519
  - layers of different horizontal extent may be combined, erroneously, by MSWMS, 513
  - update Dockerfile for mscolab, #499
  - Describe how to setup mscolab wsgi by gunicorn, #494


Version 1.9.1
-------------

Bug Fixes:
  - side view crashes when no ceiling perf data available, #507
  - mss pyui crashes when quitting, #505
  - Dockerfile fails on demodata, #501
  - Dockerfile Unable to locate package python-xpyb, #500
  - msco server does not check for None in certain circumstances, #498
  - make rtfd use of Non-ASCII characters, #492
  - mscolab server command crashes, #491
  - MSS doesn't close when "quit"ing while being connected to MSCO server, #490
  - "Checkout" of older revisions has no effect without double-clicking the revision, #485
  - Adding unknown user to project throws exception, #483
  - mcso windows cannot be closed by ctrl+w, #473

Version 1.9.0
-------------

New Features:
  - `Collaborative editing of flight path in real-time - GSoC19 (Shivashis Padhi)  <https://bitbucket.org/wxmetvis/mss/wiki/Mscolab:%20Collaborative%20editing%20of%20flight%20path%20in%20real-time%20-%20GSoC19>`_
  - test should not write pyc bytecode files, #469
  - MSS should allow simpler access to skip checks on additional dimensions or variables in NetCDF files, #463
  - satellite overpass widget shall get a "all" options. #450
  - unification of time string parsing, #440
  - Store lon_indices in plot driver so more complicated plots are feasible, #428
  - Support data with no init time in MSS server, #427
  - env disable for pyvirtualdisplay for tests, #426
  - Server is too slow when loading in many netCDF files, #423
  - use pint for unit conversion, #422
  - use package multidict, #404
  - color for missing data, move to matplotlib 3.1.0, #397
  - enlarge vertical range of demodata, #396
  - display realistic flight altitude on descent/ascent in side view, #299

Bug Fixes:
  - Some bugs and important features missing in KML support, #474
  - Server does not provide a capability xml with erroneous files, #468
  - Fix dependency issue of python-socketio, flask-socketio, #466
  - After moving a waypoint, the point first jumps to a different location before settling to its final position, #436
  - deprecation errors and warnings with current matplotlib versions, #435
  - mss server does not provide logging message in case of unexpected exception, #433
  - skyfield database download breaks sometimes, #431
  - Rounding of lon/lat coordinates, #285

Other Changes:
  - check on proper citing/licensing of employed matplotlib related sections, #438
  - Remove python2 remnants, #432

HINT
~~~~
  - We deprecated and disabled the unmaintained feature trajectory and time series view. This will become removed in
    the next major release, #476
  - We added a new powerful feature for collaborative editing of flight paths.
    This is a new server and also a new client gui window.
    In a future version the client gui will replace the standard gui.


Version 1.8.3
-------------

Bug Fixes:
  - Visual distortion after changing side view settings, #464
  - MSS ignores skip variable dimension check, #461
  - tangent points not properly calculated at longitudes != 0, #451
  - disable progressbar in skyfield Loader, #449
  - TopView hang upon switching projection under certain conditions, #445
  - Top view crashes under windows 7 when started from start-menu, #444
  - barb plots show barbs outside range of valid data, #443
  - crash upon switch from pressure altitude to pressure, #439
  - Zooming in TopView does not update properly, #437

Other Changes:
  - we contributed to the conda-forge feedstock of skyfield, #447

Version 1.8.2
-------------

Bug Fixes:
  - Rework ylabels to remove crash for low pressures, #439
  - mss server requires long time to provide capabilities document, #432

Other Changes:
  - hint in docs for mod_wsgi, #415


Version 1.8.1
-------------

Bug Fixes:
  - SideView options allow for illegal vertical range, #430
  - mss server raises error once, when asked for available, but previously unknown data, #425
  - epsg code support warnings too annoying in practice, #421
  - GetCapabilities&version= version string ignores, #411
  - Runtime Error for Url without parameters, #410
  - Improve wsgi documentation, #409
  - fixate matplotlib 3.0.2, #408

Other Changes:
  - improve documentation for demodata, #413


Version 1.8.0
-------------

New Features:
  - rename/refactor where we now use QSettings, #402
  - developer docu has to be fixed, #395
  - remove proj4 workarounds, #393
  - x/y mouse over coordinates in TopView are not always in lat/lon notation, #389
  - sideview mouse over, show data of position, #386
  - insert/delete waypoints in sideview, #380
  - support of vertical cross sections beyond 30km altitude, #379
  - access rights in the cache directory, #375
  - views cannot be closed without titlebar, #373
  - mss and matplotlib 3.0, #368
  - "colour of vertices" is misleading for the colour of the flight path, #347
  - Simplify unit conversion, #343
  - refactor: replace pickle files by QSettings, #325
  - replace paste by flask, #324
  - table view save dialog, #322
  - rename _tests/utils.py, #319
  - Add "clone" button to TableView, #254
  - Avoid "catch-all" exception handlers, #42

Bug Fixes:
  - Top View Map Appearance options not defined with web map services, #401
  - Image disappears after insert/delete operation in sideview mode, #399
  - sideview options dialog suffix always hPa, #394
  - Msui crashes on selecting Northern Hemisphere (stereo) from drop down menu under Top View section, #388
  - qt widget property issue, #387
  - localhost server url path not defined, #345
  - Updating only MSS in anaconda may result in an error, #336

Other Changes:
  - clean up comments, #406
  - remove superfluous pass statements, #405
  - Change comments for function "flightlevel2pressure_a", #384
  - Documentation about Reporting Issues, #112

HINT:
~~~~~

We dropped Python2 support. You need for this release miniconda3 or anaconda3.


Version 1.7.6
-------------

Bug Fixes:
  - http_auth for gui login broken for local builtin server, #392
  - don't limit future, #391
  - x/y move of waypoint in sideview clear Flightlevel, #390
  - remotesensing_dockwidget: year 58668 is out of range, #383

Version 1.7.5
-------------

Bug Fixes:
  - Changed pyqt Version in conda environment. see #377
  - PEP8 Fix, see #381

Hint:
  - Python 2 will no longer be supported in mss-1.8.0, see #381

Version 1.7.4
-------------

Bug Fixes:
  - remove py3.5 build because windows install fails with 1.7.3 build py_35_1, #370
  - netcdf cftime update needed for demodata / mswms, #366
  - LinkError: post-link script failed for package conda-forge::mss-1.7.3-py36_0, #365
  - msui on docker ImportError: libGL.so.1: cannot open shared object file, #362
  - mss cannot start in root environment, PROJ_LIB Path, KeyError , #360
  - Support http://msgcpp-ogc-realtime.knmi.nl/msgrt.cgi WMS Server, #352
  - Support http://geoservices.knmi.nl/cgi-bin/HARM_N25.cgi WMS server, #351
  - Support NASA WMS Server "https://neo.sci.gsfc.nasa.gov/wms/wms", #348
  - wms server: return only on the getcapability request a capability document, #346
  - demodata pressure levels uses inconsistent units, #341
  - waypoint labels (in sideview) not readable, #317

Other Changes:
  - remove warning for non installed features, #359

Hint:
~~~~~
The installation of mss in the root/base environment is deprecated.


Version 1.7.3
-------------

Bug Fixes:
  - wms capability view in mswms cannot show XML document in py3, #340
  - mswms crashes on a wms server when the request object is None, #339, #342
  - data_dir not used for default filepicker, #337
  - post_link.sh update on conda-forge, #334


Version 1.7.2
-------------

Bug Fixes:
  - update Dockerfile to Python3, #333
  - tableview misses data, #332
  - check selectors for conda-forge escpecialy for OSX, #306
  - docker installations have issues with mss-post-link.sh, #207


Version 1.7.1
-------------

Bug Fixes:
  - Some WMS VS plots create service exception when called for "empty" region, #331
  - MSS crashes on point insertion, #330

Version 1.7.0
-------------

New Features:
 - Decrease unit dependency of plotting styles, #328
 - Support basemap 1.1.0, #315, #329
 - zorder of several plot elements in topview is wrong, #314
 - pyfilesystem2 implemented, #313
 - Provide more information on solar angles in remote sensing view, #311
 - remove not used UI elements from NavigationToolbar, #297
 - basemap / matplotlib edge case artifacts, #296
 - Add measurement directions for remote sensing overlay, 294
 - "Clear map" button renamed for VSec plotting, #286
 - Performance calculation flawed in case of long leg between penultimate and ultimate point with FL 0, #280
 - Support unicode characters in WMS Plot titles, #278
 - Minimize possible action when mouse-clicking on the topview plots, #269

Bug Fixes:
 - Satellite Dockwidget FileDialog crashes with pyqt5, #320
 - Error message for EUMETSAT server for non-available stereographic projections unhelpful, #318
 - pykml replaced by xml library to fix the incompatibility to python 3, #187,

Other Changes:
 - new json parameter introduced:
    "data_dir": "~/mssdata", see section usage
    "filepicker_default": "default", see section usage
 - removed QT4, #321
 - add a better hint if Default MSS config file missing, #303, #307
 - Installing on osx-64 installs in anaconda 4 root environment old versions due to dependencies, #302, #315
 - add LICENSE to MANIFEST, #301

HINT:
~~~~~

With 1.7.0 we move to Python 3. At current state we still support Python 2. But as Python 2 will retire  we have
 to move on.
This release therefore has many refactoring changes. We removed PyQT4 because it is not compatible to PyFilesystem2.
We decided to use PyFilesystem2 because of its unified great API for internal or external storages. This enables
 for example to store flightpathes on a webdav server or other web storages by just entering a fs url.


Version 1.6.3
-------------

Bug Fixes:
 - Fix units in performance sample file comments, #300
 - Table view (with German environment) displays pressure with '.' instead of ',', #305
 - Test cases fail for pyqt5, #310

Version 1.6.2
-------------

Bug Fixes:
 - Update MSSChemDataAccess from example configuration in documentation, #291
 - cfg pickle files of older Version cause a crash of more recent MSS under windows only, #284
 - flightstar input plugin rounds coordinates, #283
 - DefaultDataAccess class crashes in case that two files of same
   vertical coordinate type have different number of levels, #282


Version 1.6.1
-------------

Bug Fixes:
 - Location names are not displayed in Table view, #281


Version 1.6.0
-------------

New Features:
 - disable traceback for server, #156
 - hybrid sigma coordinate would work with float values, #203
 - WMS data access classes difficult to set up, #210
 - add mss to docker platform, 211
 - loading a flighttrackfile does not set filename, #214
 - MSWMS consistency checks for data files, #218
 - Provide units field to Plot routines, #219
 - WMS Server get capabilities update if the data files changed, #221
 - Altitude scale in side view plots, #226
 - Add button to remove the WMS overlay graphic from flightplan, #234
 - Change wms control in such a way that the latest not the first init_time is chosen by default, #236
 - Change wms control in a way that the level keeps the same on a layer change, if feasible, #237
 - Already cached WMS information is not activated upon start of wms_control for default WMS server, #247
 - Try preloading WMS servers on startup, #250
 - traceback should show version info, #256
 - add version info to output files, #259
 - completely remove vt_cache, #260
 - update layer list on get_capabilities, #268

Bug Fixes:
 - WMS Server crashes if (some) files do not contain a variable associated with a dimension, #220
 - the proper Cf standard_name "omega" is "lagrangian_tendency_of_air_pressure", #225
 - WMS_control does not disable controls in all necessary circumstances, #239
 - MSS provides unhelpful error message when requesting unsupported projections from non-WMS servers, #244
 - WMSServer' object has no attribute 'hsec_layer_registry', #270
 - demodata vertical pressure levels contain wrong units, #276

Other Changes:
 - Remove loop view until a maintainer is found, #275


Hint:
~~~~~

DefaultDataAccess
+++++++++++++++++

With 1.6.0 we introduced a DefaultDataAccess Class. This requires a change in your server configuration.
This is an example from demodata.
data = {
   "ecmwf_EUR_LL015": mslib.mswms.dataaccess.DefaultDataAccess(_datapath, "EUR_LL015"),
}
This class substitutes all previous defined classes for data access.
The Constructor needs information on data path and domain ID, see documentation.
Also we replaced the name from nwpaccess to data.
The vt_cache caching was removed.

WMS Server
++++++++++
The server does not need a restart by new data. Any get capability request by the user loads the recent data.


Version 1.5.6
-------------

Bug Fixes:
 - Using non-US locale and pyqt4, moving points with mouse may not work, #255


Version 1.5.5
-------------

Bug Fixes:
 - Changing WP in TopView and SideView by mouse broken, #248


Version 1.5.4
-------------

Bug Fixes:
 - MSS crashes if one cancels the load performance data dialogue, #229
 - Crash in MSWMS vertical section plot If the two last waypoints share the same coordinate, #232
 - MSS crashes in SideView if the flightpath consists of exactly two identical points, #233
 - MSS crashes occasionally when moving a point in TopView, #238
 - txt export plugin broken, #240
 - Trying to clean WMC image cache may crash application (rights), #243
 - Inserting Waypoint in steorographic view is much too magnetic to locations, #245


Version 1.5.3
-------------

Bug Fixes:
 - incorrect time info on side view plots, #227
 - Coordinates close to Locations cannot be entered into TableView, #228


Version 1.5.2
-------------

Bug Fixes:
 - Server not giving WMS compliant error messages for invalid time/elevation data, #205
 - colour bar labels for generic plots do not show sufficient significant digits, #209
 - Open File Dialogue broken in PyQt5, #212
 - Table View not properly updated in PyQt5, #213


Version 1.5.1
-------------

Bug Fixes:
 - clicks on same position crashes waypoint insert for cyl projection, #197
 - existing picklefiles of py2 crash on py3 version (vice versa), #198


Version 1.5.0
-------------

New Features:
 - old OWSlib removed from repository and replaced by conda-forge package, #1
 - the get capabilities button becomes enabled if the WMS Url changes, #106
 - About of the mss ui got a link to the documentation, #110
 - About shows that we are a python powered project, #111
 - by configuration, sizes of topview, sideview, tableview,
   could be predefined and for topview and sideview set to immutable., #123
 - refactored strings to unicode, #126
 - refactored url strings, #150
 - performance data used for time information on vertical plots, #151
 - use a singleton for WMS capability storage, #168
 - ui files, _test folders excluded from conda build packages, #169
 - implemented virtualdisplay for linux, #172
 - cache for basemap coastline and country shape data added, #173
 - consistent naming of "as" imports, #175
 - loopview enable/disabled, based on given URL, #183
 - configurable external proxy to cache on low bandwidth transferred images, #188


Bug Fixes:
 - Graticule strange/broken for southern polar stereographic projection, #178
 - Flightpath / Location positioning problematic when crossing 180 degree E/W in cylindrical projection, #179
 - tests independent from local mss_settings.json, #191
 - catch invalid WMS Urls, #195


Other Changes:
 - line separator of source files unified to LF, #92
 - refactored whole codebase for compatibility with python3, #176
 - version number of recent conda package added to documentation, #185
 - split mss_settings.json.sample into snippet parts, and further documentation #194

Hint:
~~~~~
This version has a lot of refactoring work.
We are now compatible with Python 3. We have not all dependent libraries verified
to behave similar as for Python 2. After done this we will build also a Python 3 package.



Version 1.4.1
-------------

Bug Fixes:
 - changing WMS Url needs to reset some options, #170
 - plugins, e.g. kml plugin can not be loaded via configuration (.json) file on any platform, #171
 - Changing map appearance deletes WMS image title, #174


Version 1.4.0
-------------

New Features:
 - Keyboard control for side/top views, #167
 - Pressure contours to MSSChem hsects added, #164
 - Export active flight track as .kml, #158
 - Integration of CLaMS-Ice data products, #155
 - mss gui got arguments on call, #153
 - Support QT5, #114
 - Enhanced KML support, #98
 - Integration of CAMS regional AQ forecast,  #95
 - Integrate prefetch functionality into msui client to speed up map loading, #2


Bug Fixes:
 - refactored wsgi auth handler, #141, #118
 - WMS Url is updated to redirect Url, #135
 - Better identification of configured layers without (valid) data, #101


Other Changes:
 - Our source now has a unified fileheader, #137
 - Loop view  and Time Series moved into the Tools menu, #136
 - MSS Icon missing from startmenu after conda install, #115
 - MSS Logo, #100
 - We worked extensive on py.test test coverage also refactored all
   existing inline code tests, #21

Hint:
~~~~~
On linux and window installing of mss will create an icon in your Desktop start menu.

Because authentication can happen as different user than the one driving the mss server
we have moved the password setup to mss_wms_auth.py


Version 1.3.3
-------------

Bug Fixes:
 - Inserting Waypoint outside of map in TopView crashes MSS, #149
 - Some of the additional tools don't close completely, #139


Version 1.3.2
-------------

Bug Fixes:
 - Generic Maps for CLaMS employ incorrect styles, #138
 - update of map on changes and style changes, #131
 - Weight from aircraft limited to 99999, #128
 - GUI load of different config.json fails, #127
 - Delete Waypoint via Top/Sideview does not work, #124
 - sideview axis too much details, #104


Version 1.3.1
-------------

Bug Fixes:
 - Inconsistent projections employed in default/sample data for client and server, #109
 - local caching needs to take care of wms url, #107
 - options of side view fails, #105
 - flight track saving shows on linux an extension problem, #102
 - Export Active Flight Track as CSV, #103


Version 1.3.0
-------------

New Features:
 - Suggest standard name for saving plots, #13
 - KML Overlay introduced for overplot of flight region borders, #61, #97
 - implemented demodata for standalone server and py.test, #80
 - simplified server setup, added demodata.
 - Always provide simplified aircraft range estimates in TableView. #85
 - server data needs standard_name in data, #87
 - plugin infrastructure introduced for supporting file formats for flight track saving/loading, #69, #88

Bug Fixes:
 - Generic chemical Plots cannot be used in vertical cuts unless they are given on pressure grid, #62
 - config_loader overwrites internally config file, #82
 - WMS read does not recognize temperature in ECMWF data, #83
 - falling back to default configuration if mss_settings.json is missing, #89
 - PathInteractors not properly deleted when View is closed, #91

Other Changes:
 - channel atmo deprecated and removed from documentation
 - flightperformance refactored to a simpler approach, cs #5bef122
 - mss_wms_cl removed, #48
 - wms_login_cache refactored to a module of constants, #47
 - Reimplemented Hexagon Tools from Stefan using a docking widget for TableView. #18

HINT:
~~~~~

We are now based on the channel *conda-forge*, as some libraries were not in defaults of anaconda::

    $ conda config --add channels conda-forge



Version 1.2.4
-------------

Bug Fixes:
  - Flight performance computation broken, #75

Other Changes:
  - pyqt version 4.11.*, #74



Version 1.2.3
-------------

Bug Fixes:
 - check whether variables cmin, cmax are None, #68

Other Changes:
 - version dependencies removed from documentation



Version 1.2.2
-------------

Bug Fixes:
 - initialize of basemap for GUI and WMS have to use same resolution, #60
 - resize of colorbar and its font for labels in the plots, #66
 - style "fixed colour scale" on vertical plots contain unit scaling, #67

New Features:
 - addition of age-of-air parameters to CLaMS plots, #65

Other Changes:
 - installation with conda-forge described#63

Version 1.2.1
-------------

Bug Fixes:
 - server throws useful messages if mss_wms_settings.py is missing necessary variables, #58

Other Changes:
 - most version pinning removed, #59. Thanks to ocefpaf (conda-forge-member)

Version 1.2.0
-------------

New Features:
 - mss client, setup default configuration and json config file, #36, #37
 - mss client get capabilities update without new login, #29
 - wsgi and standalone server refactored and merged into one application,
   mswms is the new name of the standalone server #30
 - server configuration files simplified, #39
 - server templates got more variables defined in mss_wms_settings.py, #44, #45
 - geopy distance calculation dependency replaced by pyproj, #34
 - Simplification for adding or removing CLaMS parameters, #12

Bug Fixes:
 - execute bit only on executables, #40

Other Changes:
 - Isabell Krisch added to AUTHORS
 - skipped dependency of conda-forge, because geopy function replaced, #38
 - https://anaconda.org/atmo/mss introduced
 - moved of mslib.thirdparty.owslib to mslib.owslib and hardcoded all imports in owslib to mslib.owslib, #1
 - improved documentations


Version 1.1.0
-------------

New Features:
 - Vertical section styles supported in standalone server, #10
 - More formats for exchanging flight paths implemented, #7
 - Reverse flight path, #11
 - Displaying model data from CLaMS, #4
 - Visualisation of gravity wave forecasts, #14
 - Improved labels in plots, #8

Bug Fixes:
 - Improved debugging in standalone server, #9
 - Fix for Labels accumulate in plots upon saving, #5
 - PEP8, #19


Other Changes:
 - Namespace refactored, all modules dependent to mslib #24
 - Sphinx documentation introduced, #25, #26
 - Documentation on http://mss.rtfd.io
 - Installation recipes based on conda
 - First public release on June 28, 2016
