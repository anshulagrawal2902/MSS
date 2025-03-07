# -*- coding: utf-8 -*-
"""

    mslib.mscolab.server
    ~~~~~~~~~~~~~~~~~~~~

    Server for mscolab module

    This file is part of MSS.

    :copyright: Copyright 2019 Shivashis Padhi
    :copyright: Copyright 2019-2024 by the MSS team, see AUTHORS.
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
import platform
import os
import shutil
import sys
import secrets
import subprocess
import git
import flask_migrate
import pathlib

from mslib import __version__
from mslib.mscolab import migrations
from mslib.mscolab.conf import mscolab_settings
from mslib.mscolab.seed import seed_data, add_user, add_all_users_default_operation, \
    add_all_users_to_all_operations, delete_user
from mslib.mscolab.server import APP
from mslib.mscolab.utils import create_files
from mslib.utils import setup_logging, LOGGER


def handle_start(args=None):
    from mslib.mscolab.server import APP, sockio, cm, fm, start_server
    if args is not None:
        setup_logging(levelno=args.loglevel, logfile=args.logfile)
    LOGGER.info("MSS Version: %s", __version__)
    LOGGER.info("Python Version: %s", sys.version)
    LOGGER.info("Platform: %s (%s)", platform.platform(), platform.architecture())
    LOGGER.info("Launching MSColab Server")
    start_server(APP, sockio, cm, fm)


def confirm_action(confirmation_prompt):
    while True:
        confirmation = input(confirmation_prompt).lower()
        if confirmation == "n" or confirmation == "":
            return False
        elif confirmation == "y":
            return True
        else:
            print("Invalid input! Please select an option between y or n")


def handle_db_reset(verbose=True):
    if mscolab_settings.SQLALCHEMY_DB_URI.startswith("sqlite:///") and (
        db_path := pathlib.Path(mscolab_settings.SQLALCHEMY_DB_URI.removeprefix("sqlite:///"))
    ).is_relative_to(mscolab_settings.DATA_DIR):
        # Don't remove the database file
        # This would be easier if the database wasn't stored in DATA_DIR...
        p = pathlib.Path(mscolab_settings.DATA_DIR)
        for root, dirs, files in os.walk(p, topdown=False):
            for name in files:
                full_file_path = pathlib.Path(root) / name
                if full_file_path != db_path:
                    full_file_path.unlink()
            for name in dirs:
                (pathlib.Path(root) / name).rmdir()
    elif os.path.exists(mscolab_settings.DATA_DIR):
        shutil.rmtree(mscolab_settings.DATA_DIR)
    create_files()
    flask_migrate.downgrade(directory=migrations.__path__[0], revision="base")
    flask_migrate.upgrade(directory=migrations.__path__[0])
    if verbose is True:
        print("Database has been reset successfully!")


def handle_db_seed():
    handle_db_reset(verbose=False)
    seed_data()
    print("Database seeded successfully!")


def handle_mscolab_certificate_init():
    print('generating CRTs for the mscolab server......')

    try:
        cmd = ["openssl", "req", "-newkey", "rsa:4096", "-keyout",
               os.path.join(mscolab_settings.SSO_DIR, "key_mscolab.key"),
               "-nodes", "-x509", "-days", "365", "-batch", "-subj",
               "/CN=localhost", "-out", os.path.join(mscolab_settings.SSO_DIR,
                                                     "crt_mscolab.crt")]
        subprocess.run(cmd, check=True)
        LOGGER.info("generated CRTs for the mscolab server.")
        return True
    except subprocess.CalledProcessError as error:
        print(f"Error while generating CRTs for the mscolab server: {error}")
        return False


def handle_local_idp_certificate_init():
    print('generating CRTs for the local identity provider......')

    try:
        cmd = ["openssl", "req", "-newkey", "rsa:4096", "-keyout",
               os.path.join(mscolab_settings.SSO_DIR, "key_local_idp.key"),
               "-nodes", "-x509", "-days", "365", "-batch", "-subj",
               "/CN=localhost", "-out", os.path.join(mscolab_settings.SSO_DIR, "crt_local_idp.crt")]
        subprocess.run(cmd, check=True)
        LOGGER.info("generated CRTs for the local identity provider")
        return True
    except subprocess.CalledProcessError as error:
        print(f"Error while generated CRTs for the local identity provider: {error}")
        return False


def handle_mscolab_backend_yaml_init():
    saml_2_backend_yaml_content = """name: Saml2
config:
  entityid_endpoint: true
  mirror_force_authn: no
  memorize_idp: no
  use_memorized_idp_when_force_authn: no
  send_requester_id: no
  enable_metadata_reload: no

  # SP Configuration for localhost_test_idp
  localhost_test_idp:
    name: "MSS Colab Server - Testing IDP(localhost)"
    description: "MSS Collaboration Server with Testing IDP(localhost)"
    key_file: path/to/key_sp.key # Will be set from the mscolab server
    cert_file: path/to/crt_sp.crt # Will be set from the mscolab server
    verify_ssl_cert: true # Specifies if the SSL certificates should be verified.
    organization: {display_name: Open-MSS, name: Mission Support System, url: 'https://open-mss.github.io/about/'}
    contact_person:
    - {contact_type: technical, email_address: technical@example.com, given_name: Technical}
    - {contact_type: support, email_address: support@example.com, given_name: Support}

    metadata:
      local: [path/to/idp.xml] # Will be set from the mscolab server

    entityid: http://localhost:5000/proxy_saml2_backend.xml
    accepted_time_diff: 60
    service:
      sp:
        ui_info:
          display_name:
            - lang: en
              text: "Open MSS"
          description:
            - lang: en
              text: "Mission Support System"
          information_url:
            - lang: en
              text: "https://open-mss.github.io/about/"
          privacy_statement_url:
            - lang: en
              text: "https://open-mss.github.io/about/"
          keywords:
            - lang: en
              text: ["MSS"]
            - lang: en
              text: ["OpenMSS"]
          logo:
            text: "https://open-mss.github.io/assets/logo.png"
            width: "100"
            height: "100"
        authn_requests_signed: true
        want_response_signed: true
        want_assertion_signed: true
        allow_unknown_attributes: true
        allow_unsolicited: true
        endpoints:
          assertion_consumer_service:
            - [http://localhost:8083/localhost_test_idp/acs/post, 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST']
            - [http://localhost:8083/localhost_test_idp/acs/redirect,
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect']
          discovery_response:
          - [<base_url>/<name>/disco, 'urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol']
        name_id_format: 'urn:oasis:names:tc:SAML:2.0:nameid-format:transient'
        name_id_format_allow_create: true


  # # SP Configuration for IDP 2
  # sp_config_idp_2:
  #   name: "MSS Colab Server - Testing IDP(localhost)"
  #   description: "MSS Collaboration Server with Testing IDP(localhost)"
  #   key_file: mslib/mscolab/app/key_sp.key
  #   cert_file: mslib/mscolab/app/crt_sp.crt
  #   organization: {display_name: Open-MSS, name: Mission Support System, url: 'https://open-mss.github.io/about/'}
  #   contact_person:
  #   - {contact_type: technical, email_address: technical@example.com, given_name: Technical}
  #   - {contact_type: support, email_address: support@example.com, given_name: Support}

  #   metadata:
  #     local: [mslib/mscolab/app/idp.xml]

  #   entityid: http://localhost:5000/proxy_saml2_backend.xml
  #   accepted_time_diff: 60
  #   service:
  #     sp:
  #       ui_info:
  #         display_name:
  #           - lang: en
  #             text: "Open MSS"
  #         description:
  #           - lang: en
  #             text: "Mission Support System"
  #         information_url:
  #           - lang: en
  #             text: "https://open-mss.github.io/about/"
  #         privacy_statement_url:
  #           - lang: en
  #             text: "https://open-mss.github.io/about/"
  #         keywords:
  #           - lang: en
  #             text: ["MSS"]
  #           - lang: en
  #             text: ["OpenMSS"]
  #         logo:
  #           text: "https://open-mss.github.io/assets/logo.png"
  #           width: "100"
  #           height: "100"
  #       authn_requests_signed: true
  #       want_response_signed: true
  #       want_assertion_signed: true
  #       allow_unknown_attributes: true
  #       allow_unsolicited: true
  #       endpoints:
  #         assertion_consumer_service:
  #           - [http://localhost:8083/idp2/acs/post, 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST']
  #           - [http://localhost:8083/idp2/acs/redirect, 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect']
  #         discovery_response:
  #         - [<base_url>/<name>/disco, 'urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol']
  #       name_id_format: 'urn:oasis:names:tc:SAML:2.0:nameid-format:transient'
  #       name_id_format_allow_create: true
"""
    try:
        file_path = os.path.join(mscolab_settings.SSO_DIR, "mss_saml2_backend.yaml")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(saml_2_backend_yaml_content)
        return True
    except (FileNotFoundError, PermissionError) as error:
        print(f"Error while generated backend .yaml for the local mscolabserver: {error}")
        return False


def handle_mscolab_metadata_init(repo_exists):
    """
        This will generate necessary metada data file for sso in mscolab through localhost idp

        Before running this function:
        - Ensure that USE_SAML2 is set to True.
        - Generate the necessary keys and certificates and configure them in the .yaml
        file for the local IDP.
    """
    print('generating metadata file for the mscolab server')

    try:
        command = ["python", os.path.join("mslib", "mscolab", "mscolab.py"),
                   "start"] if repo_exists else ["mscolab", "start"]
        process = subprocess.Popen(command)
        cmd_curl = ["curl", "--retry", "5", "--retry-connrefused", "--retry-delay", "3",
                    "http://localhost:8083/metadata/localhost_test_idp",
                    "-o", os.path.join(mscolab_settings.SSO_DIR, "metadata_sp.xml")]
        subprocess.run(cmd_curl, check=True)
        process.terminate()
        LOGGER.info('mscolab metadata file generated succesfully')
        return True

    except subprocess.CalledProcessError as error:
        print(f"Error while generating metadata file for the mscolab server: {error}")
        return False


def handle_local_idp_metadata_init(repo_exists):
    print('generating metadata for localhost identity provider')

    try:
        if os.path.exists(os.path.join(mscolab_settings.SSO_DIR, "idp.xml")):
            os.remove(os.path.join(mscolab_settings.SSO_DIR, "idp.xml"))

        idp_conf_path = os.path.join("mslib", "msidp", "idp_conf.py")

        if not repo_exists:
            import site
            site_packages_path = site.getsitepackages()[0]
            idp_conf_path = os.path.join(site_packages_path, "mslib", "msidp", "idp_conf.py")

        cmd = ["make_metadata", idp_conf_path]

        with open(os.path.join(mscolab_settings.SSO_DIR, "idp.xml"),
                  "w", encoding="utf-8") as output_file:
            subprocess.run(cmd, stdout=output_file, check=True)
        LOGGER.info("idp metadata file generated successfully")
        return True
    except subprocess.CalledProcessError as error:
        # Delete the idp.xml file when the subprocess fails
        if os.path.exists(os.path.join(mscolab_settings.SSO_DIR, "idp.xml")):
            os.remove(os.path.join(mscolab_settings.SSO_DIR, "idp.xml"))
        print(f"Error while generating metadata for localhost identity provider: {error}")
        return False


def handle_sso_crts_init():
    """
        This will generate necessary CRTs files for sso in mscolab through localhost idp
    """
    print("\n\nmscolab sso conf initiating......")
    if os.path.exists(mscolab_settings.SSO_DIR):
        shutil.rmtree(mscolab_settings.SSO_DIR)
    create_files()
    if not handle_mscolab_certificate_init():
        print('Error while handling mscolab certificate.')
        return

    if not handle_local_idp_certificate_init():
        print('Error while handling local idp certificate.')
        return

    if not handle_mscolab_backend_yaml_init():
        print('Error while handling mscolab backend YAML.')
        return

    print('\n\nAll CRTs and mscolab backend saml files generated successfully !')


def handle_sso_metadata_init(repo_exists):
    print('\n\ngenerating metadata files.......')
    if not handle_mscolab_metadata_init(repo_exists):
        print('Error while handling mscolab metadata.')
        return

    if not handle_local_idp_metadata_init(repo_exists):
        print('Error while handling idp metadata.')
        return

    print("\n\nALl necessary metadata files generated successfully")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help="show version", action="store_true", default=False)

    subparsers = parser.add_subparsers(help='Available actions', dest='action')

    server_parser = subparsers.add_parser("start", help="Start the mscolab server")
    server_parser.add_argument("--loglevel", help="set logging level", dest="loglevel", default=int(logging.INFO))
    server_parser.add_argument("--logfile", help="If set to a name log output goes to that file", dest="logfile",
                               default=None)

    database_parser = subparsers.add_parser("db", help="Manage mscolab database")
    database_parser = database_parser.add_mutually_exclusive_group(required=True)
    database_parser.add_argument("--reset", help="Reset database", action="store_true")
    database_parser.add_argument("--seed", help="Seed database", action="store_true")
    database_parser.add_argument("--users_by_file", type=argparse.FileType('r'),
                                 help="adds users into database, fileformat: suggested_username  name   <email>")
    database_parser.add_argument("--delete_users_by_file", type=argparse.FileType('r'),
                                 help="removes users from the database, fileformat: email")
    database_parser.add_argument("--default_operation", help="adds all users into a default TEMPLATE operation",
                                 action="store_true")
    database_parser.add_argument("--add_all_to_all_operation", help="adds all users into all other operations",
                                 action="store_true")
    sso_conf_parser = subparsers.add_parser("sso_conf", help="single sign on process configurations")
    sso_conf_parser = sso_conf_parser.add_mutually_exclusive_group(required=True)
    sso_conf_parser.add_argument("--init_sso_crts",
                                 help="Generate all the essential CRTs required for the Single Sign-On process "
                                 "using the local Identity Provider",
                                 action="store_true")
    sso_conf_parser.add_argument("--init_sso_metadata", help="Generate all the essential metadata files required "
                                 "for the Single Sign-On process using the local Identity Provider",
                                 action="store_true")

    args = parser.parse_args()

    if args.version:
        print("***********************************************************************")
        print("\n            Mission Support System (MSS)\n")
        print("***********************************************************************")
        print("Documentation: http://mss.rtfd.io")
        print("Version:", __version__)
        sys.exit()

    try:
        _ = git.Repo(os.path.dirname(os.path.realpath(__file__)), search_parent_directories=True)
        repo_exists = True

    except git.exc.InvalidGitRepositoryError:
        repo_exists = False

    if args.action == "start":
        handle_start(args)

    elif args.action == "db":
        if args.reset:
            confirmation = confirm_action("Are you sure you want to reset the database? This would delete "
                                          "all your data! (y/[n]):")
            if confirmation is True:
                with APP.app_context():
                    handle_db_reset()
        elif args.seed:
            confirmation = confirm_action("Are you sure you want to seed the database? Seeding will delete all your "
                                          "existing data and replace it with seed data (y/[n]):")
            if confirmation is True:
                with APP.app_context():
                    handle_db_seed()
        elif args.users_by_file is not None:
            # fileformat: suggested_username  name   <email>
            confirmation = confirm_action("Are you sure you want to add users to the database? (y/[n]):")
            if confirmation is True:
                for line in args.users_by_file.readlines():
                    info = line.split()
                    username = info[0]
                    emailid = info[-1][1:-1]
                    password = secrets.token_hex(8)
                    add_user(emailid, username, password)
        elif args.default_operation:
            confirmation = confirm_action(
                "Are you sure you want to add users to the default TEMPLATE operation? (y/[n]):")
            if confirmation is True:
                # adds all users as collaborator on the operation TEMPLATE if not added, command can be repeated
                add_all_users_default_operation(access_level='admin')
        elif args.add_all_to_all_operation:
            confirmation = confirm_action(
                "Are you sure you want to add users to the ALL operations? (y/[n]):")
            if confirmation is True:
                # adds all users to all Operations
                add_all_users_to_all_operations()
        elif args.delete_users_by_file:
            confirmation = confirm_action(
                "Are you sure you want to delete a user? (y/[n]):")
            if confirmation is True:
                # deletes users from the db
                for email in args.delete_users_by_file.readlines():
                    delete_user(email.strip())

    elif args.action == "sso_conf":
        if args.init_sso_crts:
            confirmation = confirm_action(
                "This will reset and initiation all CRTs and SAML yaml file as default. "
                "Are you sure to continue? (y/[n]):")
            if confirmation is True:
                handle_sso_crts_init()
        if args.init_sso_metadata:
            confirmation = confirm_action(
                "Are you sure you executed --init_sso_crts before running this? (y/[n]):")
            if confirmation is True:
                confirmation = confirm_action(
                    """
                    This will generate necessary metada data file for sso in mscolab through localhost idp

                    Before running this function:
                    - Ensure that USE_SAML2 is set to True.
                    - Generate the necessary keys and certificates and configure them in the .yaml
                    file for the local IDP.

                    Are you sure you set all correctly as per the documentation? (y/[n]):
                    """
                )
                if confirmation is True:
                    handle_sso_metadata_init(repo_exists)


if __name__ == '__main__':
    main()
