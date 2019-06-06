import liteconfig
from fs.ftpfs import FTPFS


class FTP:
    """FTP instance"""
    def __init__(self, creds_file):
        creds = liteconfig.Config(creds_file)
        self.worker = FTPFS(creds.host,
                            user=creds.user,
                            passwd=creds.passwd,
                            port=creds.port or 21)


if __name__ == "__main__":
    print("Please fill in hostname, username, password and (optionally) port in the 'ftp-credentials' file."
          "In case of port absence we will attempt to connect to standard port 21.")
