"""
TODO:
- [X] Add check exists on DropBox Backend
- [X] For Dropbox Upload - Implement
    - [X] Splitting of Bytes
    - [X] Upload into Folder of Files
    - [X] Parallel Upload
"""
import abc
import os
import io
import tqdm
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from fsspec import AbstractFileSystem
import webbrowser
import dropbox
import requests
import base64
from dropboxdrivefs import DropboxDriveFileSystem
from .backend import Backend


class DropboxConfig:
    """
    Get OAuth2 Token
    """
    REFRESH_TOKEN_FILE = 'DROPBOX_REFRESH_TOKEN.ini'

    @property
    def refresh_token(self):
        if os.getenv('DROPBOX_REFRESH_TOKEN') is not None:
            return os.getenv('DROPBOX_REFRESH_TOKEN')
        elif os.path.exists(DropboxConfig.REFRESH_TOKEN_FILE):
            with open(DropboxConfig.REFRESH_TOKEN_FILE, 'r') as f:
                token = f.read()
                try:
                    dbx = dropbox.Dropbox(
                        app_key=self.app_key,
                        app_secret=self.app_secret,
                        oauth2_refresh_token=token
                    )
                    dbx.files_list_folder('')
                except dropbox.exceptions.AuthError:
                    token = self.__obtain_refresh_token()
            return token
        else:
            token = self.__obtain_refresh_token()
            return token

    def __obtain_refresh_token(self):
        url = f'https://www.dropbox.com/oauth2/authorize?client_id={self.app_key}&' \
            f'response_type=code&token_access_type=offline'
        webbrowser.open(url)
        access_token = input('dropbox_access_token:\n')
        refresh_token = self._get_refresh_token(access_token)
        with open(DropboxConfig.REFRESH_TOKEN_FILE, 'w') as f:
            f.write(refresh_token)
        return refresh_token

    def _get_refresh_token(self, access_code_generated):
        auth = base64.b64encode(f'{self.app_key}:{self.app_secret}'.encode())
        headers = {
            'Authorization': f"Basic {auth}",
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = f'code={access_code_generated}&grant_type=authorization_code'
        response = requests.post('https://api.dropboxapi.com/oauth2/token',
                                 data=data,
                                 auth=(self.app_key, self.app_secret),
                                 headers=headers)
        data = response.json()
        if 'refresh_token' in data:
            return data['refresh_token']

    @property
    def app_key(self):
        return os.getenv('DROPBOX_APP_KEY')

    @property
    def app_secret(self):
        return os.getenv('DROPBOX_APP_SECRET')


class MyDropboxFS(DropboxConfig, DropboxDriveFileSystem):
    def connect(self):
        """ connect to the dropbox account with the given token
        """
        self.dbx = dropbox.Dropbox(
            app_key=self.app_key,
            app_secret=self.app_secret,
            oauth2_refresh_token=self.refresh_token
        )
        self.token = self.refresh_token
        self.session = requests.Session()
        self.session.auth = ("Authorization", self.token)

    def copy(self, path1, path2, recursive=True, **kwargs):
        if isinstance(path1, list):
            for file_path in path1:
                assert not file_path.endswith(
                    '/'), 'multiple file copy should takes files as input'
                self.copy(file_path, path2)
        else:
            if path1.endswith('/') and path2.endswith('/'):
                assert recursive, 'recursive should be True for folder copying'
                if not self.exists(path2[:-1]):
                    self.dbx.files_copy(path1[:-1], path2[:-1])
                else:
                    self.rm(path2[:-1], recursive=True)
                    self.dbx.files_copy(path1[:-1], path2[:-1])
            elif path2.endswith('/'):
                self.dbx.files_copy(path1, path2 + path1.split('/')[-1])
            else:
                self.dbx.files_copy(path1, path2)

    def cp_file(self, path1, path2, **kwargs):
        assert not path1.endswith('/'), f'{path1} is not a file'
        assert not path2.endswith('/'), f'{path2} is not a file'
        self.dbx.files_copy(path1, path2)


class FileSystem(Backend):
    """
    FileSystem Backend for storing python objects.

    Example: DropBoxStorage
    """

    def __init__(self, fsspec_fs: AbstractFileSystem):
        self._fs = fsspec_fs

    def upload_core(self, file_obj: io.BytesIO, remote_path: str):
        """Upload file object

        Args:
            file_obj (io.BytesIO): file to be upload
            remote_path (str): remote file path
        """
        self._upload_core(file_obj, remote_path)
        self._check_upload_success(file_obj, remote_path)

    def _check_upload_success(self, file_obj: io.BytesIO, remote_path: str):
        download_data = self.download_core(remote_path)
        download_data.seek(0)
        file_obj.seek(0)
        size = len(download_data.read())
        target_size = len(file_obj.read())
        assert size == target_size, f'size inequal. upload size: {size}; target size: {target_size}'
        download_data.seek(0)
        file_obj.seek(0)
        assert download_data.read() == file_obj.read()
        file_obj.seek(0)
        download_data.seek(0)

    @abc.abstractmethod
    def _upload_core(self, file_obj: io.BytesIO, remote_path: str):
        """Upload file object to local storage

        Args:
            file_obj (io.BytesIO): file to be upload
            remote_path (str): remote file path
        """
        raise NotImplementedError

    @abc.abstractmethod
    def download_core(self, remote_path: str) -> io.BytesIO:
        """Download file from remote storage

        Args:
            remote_path (str): remote file path

        Returns:
            io.BytesIO: downloaded file
        """
        raise NotImplementedError

    def check_exists(self, remote_path: str) -> bool:
        return self._fs.exists(remote_path)

    def drop_file(self, remote_path: str):
        try:
            return self._fs.rm(remote_path)
        except FileNotFoundError:
            pass

    def copy_file(self, src_file: str, dest_file):
        assert '.' in src_file, f'requires file ext .xxx provided in `src_file` but it is {src_file}'
        assert '.' in dest_file, f'requires file ext .xxx provided in `dest_file` but it is {dest_file}'
        self.drop_file(dest_file)
        self._fs.cp(src_file, dest_file, recursive=True)


class LocalBackend(FileSystem):
    def __init__(self, directory='./'):
        root_fs = LocalFileSystem()
        if not root_fs.exists(directory):
            root_fs.mkdir(directory)
        super().__init__(DirFileSystem(directory))

    def _upload_core(self, file_obj: io.BytesIO, remote_path: str):
        """Upload file object to local storage

        Args:
            file_obj (io.BytesIO): file to be upload
            remote_path (str): remote file path
        """
        try:
            file_obj.seek(0)
            with self._fs.open(remote_path, 'wb') as f:
                f.write(file_obj.getbuffer())
        except BaseException as e:
            raise ValueError(f'{remote_path} upload failed') from e

    def download_core(self, remote_path: str) -> io.BytesIO:
        """Download file from remote storage

        Args:
            remote_path (str): remote file path

        Returns:
            io.BytesIO: downloaded file
        """
        try:
            with self._fs.open(remote_path, 'rb') as f:
                result = io.BytesIO(f.read())
            result.seek(0)
            return result
        except BaseException as e:
            raise ValueError(f'{remote_path} download failed') from e


limit_pool = Semaphore(value=8)


class DropboxBackend(FileSystem):
    """
    Storage object with IO interface left abstract
    """

    def __init__(self, directory='/', chunksize=2000000):
        assert directory.startswith('/')
        root_fs = MyDropboxFS(token='')
        super().__init__(DirFileSystem(directory, root_fs))
        self._chunksize = chunksize

    def _upload_core(self, file_obj: io.BytesIO, remote_path: str):
        """Upload file object to local storage

        Args:
            file_obj (io.BytesIO): file to be upload
            remote_path (str): remote file path
        """
        assert '.' in remote_path, f'requires file ext .xxx provided in `remote_path` but it is {remote_path}'
        file_name = remote_path.split('.')[0]
        ext = remote_path.split('.')[1]
        if self._fs.exists(file_name):
            self._fs.rm(file_name)
        self._fs.mkdir(file_name)
        assert self._fs.exists(file_name), f'{file_name} folder make failed'
        dfs = DirFileSystem(f'/{file_name}', self._fs)

        def partial_upload(item):
            limit_pool.acquire()
            try:
                index = item[0]
                chunk = item[1]
                with dfs.open(f'{index}.{ext}', 'wb') as f:
                    f.write(chunk)
            finally:
                limit_pool.release()
        try:
            file_obj.seek(0)
            buff = file_obj.getbuffer()
            with ThreadPoolExecutor(max_workers=8) as executor:
                input_pipe = self.__split_bytes(buff)
                output_pipe = executor.map(
                    partial_upload, enumerate(input_pipe))
                _ = list(tqdm.tqdm(output_pipe,
                                   total=len(buff) // self._chunksize))
            # Checking Data Size Correctness
            local_size = len(buff)
            remote_file_info = dict([(_fn['name'].split('/')[-1], _fn['size'])
                                    for _fn in self._fs.ls(f'{file_name}') if _fn['type'] == 'file'])
            remote_size = sum(remote_file_info.values())
            assert local_size == remote_size, f'local size ({local_size}) != remote size ({remote_size})'
        except BaseException as e:
            raise ValueError(f'{remote_path} upload failed') from e

    def __split_bytes(self, buff: bytes):
        for i in range(len(buff) // self._chunksize + 1):
            yield buff[i * self._chunksize: (i + 1) * self._chunksize]

    def download_core(self, remote_path: str) -> io.BytesIO:
        """Download file from remote storage

        Args:
            remote_path (str): remote file path

        Returns:
            io.BytesIO: downloaded file
        """
        assert '.' in remote_path, f'requires file ext .xxx provided in `remote_path` but it is {remote_path}'
        file_name = remote_path.split('.')[0]
        ext = remote_path.split('.')[1]
        assert self._fs.exists(
            f'{file_name}'), f'{file_name} folder does not exists for FileSystem: {self._fs}'
        remote_file_info = dict([(_fn['name'].split('/')[-1], _fn['size'])
                                for _fn in self._fs.ls(f'{file_name}') if _fn['type'] == 'file'])
        dfs = DirFileSystem(file_name, self._fs)

        def partial_download(index):
            limit_pool.acquire()
            try:
                fn = f'{index}.{ext}'
                assert dfs.exists(fn), f'{fn} does not exists in {dfs}'
                with dfs.open(fn, 'rb') as f:
                    _result = f.read()
                assert len(
                    _result) == remote_file_info[fn], f'download size does not match with remote size. download size:{len(_result)}; remote size: {remote_file_info[fn]}; remote'
                return _result
            finally:
                limit_pool.release()

        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                output_pipe = executor.map(
                    partial_download, range(
                        len(remote_file_info)))
                output_pipe = tqdm.tqdm(
                    output_pipe, total=len(remote_file_info))
                results = list(output_pipe)
            buff = b''.join(results)
            result = io.BytesIO(buff)
            # Checking Data Size Correctness
            local_size = len(buff)
            remote_size = sum(remote_file_info.values())
            assert local_size == remote_size, f'local size ({local_size}) != remote size ({remote_size})'
            result.seek(0)
            return result
        except BaseException as e:
            raise ValueError(f'{remote_path} download failed') from e

    def check_exists(self, remote_path: str) -> bool:
        assert '.' in remote_path, f'requires file ext .xxx provided in `remote_path` but it is {remote_path}'
        file_name = remote_path.split('.')[0]
        return self._fs.exists(file_name)

    def drop_file(self, remote_path: str):
        assert '.' in remote_path, f'requires file ext .xxx provided in `remote_path` but it is {remote_path}'
        file_name = remote_path.split('.')[0]
        try:
            return self._fs.rm(file_name)
        except FileNotFoundError:
            pass

    def copy_file(self, src_file: str, dest_file):
        assert '.' in src_file, f'requires file ext .xxx provided in `src_file` but it is {src_file}'
        assert '.' in dest_file, f'requires file ext .xxx provided in `dest_file` but it is {dest_file}'
        self.drop_file(dest_file)
        src_file = src_file.split('.')[0]
        dest_file = dest_file.split('.')[0]
        self._fs.cp(src_file, dest_file, recursive=True)
