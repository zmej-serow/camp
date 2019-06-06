from main import Singleton, logging

from mediums.googledrive import GoogleDrive
from mediums.ftp import FTP


class Uploader(metaclass=Singleton):
    """Class to upload files."""
    def __init__(self, medium, creds, dst_folder):
        """
        Initializes the uploading entity.
        :param medium: transport for uploading files
        :param creds: credentials file
        :param dst_folder: folder name on remote system. In this folder the files will be uploaded
        Private parameters:
        _first_time: used in _authorize() to determine if connection is alive or we need to re-sign to the service
        _mediums: dict of medium names and their classes
        """
        self.dst_folder = dst_folder
        self.medium = medium
        self.creds = creds
        self._first_time = True
        self._mediums = {
            'gdrive': GoogleDrive,
            'ftp': FTP
        }
        self._authorize()

    def _authorize(self):
        """
        Service authorization goes here.
        The method will set up Uploader.service property and it will hold medium's worker method.
        """
        if self._first_time:
            self.service = self._mediums[self.medium](self.creds).worker
            self._first_time = False
        try:
            self.service.listdir('') or self.service.listdir('/')  # check if connection is alive
        except:
            self.service = self._mediums[self.medium](self.creds).worker

    def _mutate_filename(self, file, source):
        """
        If file exists in destination folder, this method will mutate it's name until success,
        adding underscore and number to file name' stem. I.e.: aaa.pdf -> aaa_1.pdf -> aaa_2.pdf et cetera.
        :param file: file name to mutate
        :param source: FS instance to which file belongs to
        :return: path: str, mutated filename
        """
        stem = source.getinfo(file).stem
        suffixes = ''.join(source.getinfo(file).suffixes)
        counter = 1
        path = f'{self.dst_folder}/{stem}_{counter}{suffixes}'
        while self.service.exists(path):
            counter += 1
            path = f'{self.dst_folder}/{stem}_{counter}{suffixes}'
        return path

    def upload(self, attachments, source):
        """
        Uploading method.
        :param attachments: dict of pairs {filename:None} we have to upload
        :param source: FS instance holding uploading files
        :return: dict of pairs {filename:link}
        """
        self._authorize()
        for file in attachments.keys():
            path = f'{self.dst_folder}/{file}'

            if not self.service.exists(self.dst_folder):
                try:
                    self.service.makedir(self.dst_folder)
                except Exception as e:
                    logging.error(f'Cannot make directory {self.dst_folder}: {e}')
                    return None

            if self.service.exists(path):
                path = self._mutate_filename(file, source)

            try:
                with self.service.open(path, 'wb') as f:
                    source.download(file, f)
            except Exception as e:
                logging.error(f'Cannot upload: {e}')
                return None

            try:
                link = self.service.share(path=path, role='reader')
                if not link:
                    return None
            except AttributeError:  # we don't have to explicitly share resource, it's already accessible
                link = self.service.geturl(path)

            attachments[file] = link
        return attachments
