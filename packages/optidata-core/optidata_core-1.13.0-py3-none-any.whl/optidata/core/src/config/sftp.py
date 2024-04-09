import logging
import os
from functools import cache

import paramiko
import pysftp

from ..config import settings

log = logging.getLogger(__name__)


@cache
class Sftp(object):
    # Accept any host key (still wrong see below)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    def __init__(self):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.sftp_client = None
        self.ssh_client = None
        self.hostname = settings.SFTP_HOSTNAME
        self.username = settings.SFTP_USERNAME
        self.password = settings.SFTP_PASSWORD
        self.port = settings.SFTP_PORT

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            # create SSH client and connect to sftp host
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                allow_agent=True
            )

            self.sftp_client = self.ssh_client.open_sftp()

        except pysftp.HostKeysException as e:
            self.sftp_client._init_error = True
            # raise paramiko.ssh_exception.SSHException(str(e))
        except Exception as err:
            log.exception(err)
            # raise Exception(err)
        finally:
            log.info(f"Connected to {self.hostname} as {self.username}.")

    def disconnect(self):
        """Closes the sftp connection"""
        self.sftp_client.close()
        log.info(f"Disconnected from host {self.hostname}")

    def listdir(self, remote_path):
        list_files = []
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.sftp_client.listdir(remote_path):
            list_files.append(obj)
        return list_files

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.sftp_client.listdir_attr(remote_path):
            yield attr

    def download(self, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """

        try:
            log.info(
                f"downloading from {self.hostname} as {self.username} [(remote path : {remote_path});(local path: {target_local_path})]"
            )

            # Create the target directory if it does not exist
            path, _ = os.path.split(target_local_path)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except Exception as err:
                    log.exception(err)
                    raise Exception(err)

            # Download from remote sftp server to local
            self.sftp_client.get(remote_path, target_local_path)
            log.info("download completed")

        except Exception as err:
            log.exception(err)
            raise Exception(err)

    def upload(self, source_local_path, remote_path):
        """
        Uploads the source files from local to the sftp server.
        """

        try:
            log.info(
                f"uploading to {self.hostname} as {self.username} [(remote path: {remote_path});(source local path: {source_local_path})]"
            )

            # Download file from SFTP
            self.sftp_client.put(source_local_path, remote_path)
            log.info("Upload completed")

        except Exception as err:
            log.exception(err)
            raise Exception(err)

    def read_content(self, my_filename):
        with self.sftp_client.open(my_filename) as sftp_file:
            contents = sftp_file.read()
            return contents
