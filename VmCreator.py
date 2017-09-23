
import paramiko
import time
import socket


class Deployer:

    """
    This class is used for creating the connection to a server using Paramiko module
    """

    debug = False

    def __init__(self, server, usr, passw):

        """
        Constructor that creates a connection to the server using paramiko
        """

        if self.debug is True:
            print "Connecting to server %s" % server
        else:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                self.client.connect(server, username=usr, password=passw)
                print "Successful connection"
            except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
                    paramiko.SSHException, socket.error) as e:
                print e
                raise Exception("connection_failed")

            self.ssh_transp = self.client.get_transport()

    def __del__(self):

        """
        This function is used to close a paramiko connection
        """
        if self.debug is True:
            print "Closing connection"
        else:
            self.client.close()

    def run_command(self, command):

        """
        This function is used to run the commands within a paramiko session
        """
        print "Running the command: " + command
        if self.debug is True:
            time.sleep(1)
        else:
            chan = self.ssh_transp.open_session()
            chan.setblocking(0)
            chan.exec_command(command)

            # TODO: add timeout
            while True:
                if chan.exit_status_ready():
                    break
                time.sleep(1)
            retcode = chan.recv_exit_status()
            return retcode

    def copy_file(self, localpath, remotepath):

        """
        This function is used to copy a file from the localpath to a remotepath within a paramiko session
        """
        print "Copying file from %s to %s on remote" % (localpath, remotepath)
        if self.debug is True:
            time.sleep(1)
        else:
            sftp = self.client.open_sftp()
            sftp.put(localpath, remotepath)
            sftp.close()
            self.client.close()
            print "Copied the file"
