#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

    mslib.mswms.mswms
    ~~~~~~~~~~~~~~~~~

    The module can be run with the Python Flask framework and can be run as
    python mswms.py.

    :copyright: Copyright 2016 Reimar Bauer
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

import argparse
import logging
import sys

from mslib import __version__
from mslib.utils import setup_logging, LOGGER
from mslib.mswms.wms import app as application

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help="show version", action="store_true", default=False)
    parser.add_argument("--host", help="hostname",
                        default="127.0.0.1", dest="host")
    parser.add_argument("--port", help="port", dest="port", default="8081")
    parser.add_argument("--threadpool", help="threadpool", dest="use_threadpool", action="store_true", default=False)
    parser.add_argument("--loglevel", help="set logging level", dest="loglevel", default=logging.INFO)
    parser.add_argument("--logfile", help="If set to a name log output goes to that file", dest="logfile",
                        default=None)

    subparsers = parser.add_subparsers(help='Available actions', dest='action')
    gallery = subparsers.add_parser("gallery", help="Subcommands surrounding the gallery")
    gallery.add_argument("--create", action="store_true", default=False,
                         help="Generates plots of all layers not already present")
    gallery.add_argument("--clear", action="store_true", default=False,
                         help="Deletes all plots and corresponding code")
    gallery.add_argument("--refresh", action="store_true", default=False,
                         help="Deletes all plots and regenerates them, a mix of --clear and --create")
    gallery.add_argument("--levels", default="", help="A comma-separated list of all levels visible on the gallery.\n"
                                                      "E.g. --levels 200,300"
                                                      "Use --levels all to include all levels.\n"
                                                      "Default is the middle level.")
    gallery.add_argument("--itimes", default="", help="A comma-separated list of all init times visible on the gallery"
                                                      ", in ISO format.\nE.g. --itimes 2012-10-17T12:00:00\n"
                                                      "Use --itimes all to use all available itimes.\n"
                                                      "Default is the latest itime.")
    gallery.add_argument("--vtimes", default="", help="A comma-separated list of all valid times visible on the gallery"
                                                      ", in ISO format.\nE.g. --vtimes 2012-10-19T12:00:00\n"
                                                      "Use --vtimes all to use all available vtimes.\n"
                                                      "Default is the latest vtime")
    gallery.add_argument("--show-code", action="store_true", default=False,
                         help="Generates plots of all layers not already present, "
                              "and generates code snippets for each plot when clicking on the image")
    gallery.add_argument("--url-prefix", default="",
                         help="Normally the plot images should appear at the relative url /static/plots/*.png.\n"
                              "In case they are prefixed by something, e.g. /demo/static/plots/*.png,"
                              " please provide the prefix /demo here.")
    gallery.add_argument("--plot_types", default=None,
                         help='A comma-separated list of all plot_types. \n'
                              'Default is ["Top", "Side", "Linear"]')

    args = parser.parse_args()
    if args.version:
        print("***********************************************************************")
        print("\n            Mission Support System (MSS)\n")
        print("***********************************************************************")
        print("Documentation: http://mss.rtfd.io")
        print("Version:", __version__)
        sys.exit()

    setup_logging(logfile=args.logfile, levelno= int(args.loglevel))

    # keep the import after the version check. This creates all layers.
    from mslib.mswms.wms import mswms_settings, server

    if args.action == "gallery":
        if args.plot_types is None:
            plot_types = ["Top", "Side", "Linear"]
        else:
            plot_types = [name.strip() for name in args.plot_types.split(',')]
        create = args.create or args.refresh
        clear = args.clear or args.refresh
        server.generate_gallery(create, clear, args.show_code, url_prefix=args.url_prefix, levels=args.levels,
                                itimes=args.itimes, vtimes=args.vtimes, plot_types=plot_types)
        LOGGER.info("Gallery generation done.")
        sys.exit()

    LOGGER.info("Configuration File: '%s'", mswms_settings.__file__)

    application.run(args.host, args.port)


if __name__ == '__main__':
    main()
