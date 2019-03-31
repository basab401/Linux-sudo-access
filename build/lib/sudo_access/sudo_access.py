#!/usr/bin/env python3

from __future__ import print_function

import sys
import os
import logging
import time
import argparse
import pwd
import grp
import subprocess
import requests
from requests.auth import HTTPBasicAuth

# globals
G_EXIT_ERROR = 128

# create logger
saprint = logging.getLogger(__name__)

def SudoAccessLogger (consoleLevel=logging.INFO, 
                      fileLevel=logging.INFO,
                      logFile="/tmp/sudo_access_service.log"):
    """
    Log settings
    """
    fileHandler = logging.FileHandler(logFile)
    fileHandler.setLevel(fileLevel)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(consoleLevel)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[fileHandler, consoleHandler])

class RequestHttp():
    """
    This class wraps up the requests HTTP methods
    """
    def __init__(self, host='database.company.com', port=443,
                       user_id='admin', password='admin'):
         self.connect_target = 'https://' + host + ':' + str(port)
         self.user_id = user_id
         self.password = password
         self.session = None
    def get(self, rest_tail):
         result = None
         api_target = self.connect_target + rest_tail
         saprint.debug("Calling GET on Server {}".format(api_target))
         try:
            result = requests.get(api_target, \
                        auth=requests.auth.HTTPBasicAuth(self.user_id, \
                                                         self.password))
         except requests.exceptions.HTTPError:
             saprint.error("Http Error Connecting to {}".format(self.connect_target))
             sys.exit(G_EXIT_ERROR)
         except requests.exceptions.ConnectionError:
             saprint.error("Error Connecting to {}".format(self.connect_target))
             sys.exit(G_EXIT_ERROR)
         except requests.exceptions.Timeout:
             saprint.error("Timeout Error Connecting to {}".format(self.connect_target))
             sys.exit(G_EXIT_ERROR)
         except requests.exceptions.RequestException:
             saprint.error("OOps: Something Else Connecting to {}".format(self.connect_target))
             sys.exit(G_EXIT_ERROR)
         return result

class GrantSudoAccess():
    """
    class to add the given user into the sudo list
    """
    def __init__(self, users=[]):
        self.users = users
        if self.users:
            saprint.debug("Init User {}".format(self.users))
    def add(self):
        if self.users:
            for user in self.users:
                # First check if user exists on the system
                try:
                    pwd.getpwnam(user)
                except KeyError:
                    saprint.error('User \"{}\" does not exist on the \
                                       system'.format(user))
                    continue
                # Now check if the user is already in sudo list
                groups = grp.getgrall()
                user_has_sudo_access = False
                for group in groups:
                    for ubuntu_system_user in group[3]:
                        if ubuntu_system_user == user and \
                                group[0] == 'sudo':
                            user_has_sudo_access = True
                # Add users into the sudo list if not already part of
                if not user_has_sudo_access:
                    cmd = 'usermod '
                    cmd = cmd + '-aG '
                    cmd = cmd + 'sudo '
                    cmd = cmd + user
                    saprint.debug("subprocess cmd {}".format(cmd))
                    rc = subprocess.run(cmd, check=True,
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        shell=True)
                    if rc.returncode:
                        # subprocess returned error,
                        #   just log error and continue
                        saprint.error('Could not add \"{}\" into sudo list, \
                                        rc {}, stderror {}'.format(\
                                        user, rc.returncode, rc.stderr))


class NotSudo(Exception):
    pass

def main(*margs):
    """
    main function
    """
    if os.geteuid() != 0:
        raise NotSudo("This program is not run with elevated "
                        "privileges, which may lead to errors, exiting!")

    parser = argparse.ArgumentParser("sudo access grant service")
    parser.add_argument("--debug", action="store_true", help='Enable debug logging')
    parser.add_argument("--hostname", default="database.company.com", help='REST API Server Hostname')
    parser.add_argument('--port', type=int, default=443, help='REST API server port')
    parser.add_argument("--username", default="admin", help='REST username')
    parser.add_argument("--password", default="admin", help='REST password')
    parser.add_argument('--device_hostname', default="SAMPLE", help='Resource Device Hostname')
    args = parser.parse_args(*margs)
    # Update logging preferences
    if (args.debug):
         SudoAccessLogger(consoleLevel=logging.WARN, fileLevel=logging.DEBUG)
    else:
         SudoAccessLogger()
    # Get http service reference
    rest_service = RequestHttp(args.hostname, args.port,
                               args.username, args.password)
    # database.company.com/devices/<hostname>/allowedUsers
    rest_resource = '/devices/' + args.device_hostname + '/allowedUsers'

    # Infinite loop to keep invoking REST get
    #   to fetch the user details periodically
    while True:
        result = rest_service.get(rest_resource)
        users = []
        if result:
            # The link should respond with
            #   { 'allowedUsers': [ 'abc123', 'def456' ] }
            try:
                users = result['allowedUsers']
            except KeyError:
                # Either the result doesn't contain any users
                #  or the corresponding resource key has changed.
                #  will exit the loop
                saprint.critical('REST call response not compliant, '
                                 'allowedUsers key not found! '
                                 'exiting!')
                sys.exit(G_EXIT_ERROR)
            # Call GrantSudoAccess class to add the users
            access = GrantSudoAccess(users)
            access.add()
        # sleep for 60 seconds and continue
        time.sleep(60)

if __name__ == "__main__":
    main()