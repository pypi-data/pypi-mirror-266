from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, Optional, List, ClassVar, Union
from pathlib import Path
from azure.storage.blob import BlobServiceClient, ContainerClient
import json
import numpy as np
import io

"""
Storage services for saving data from ZoneVu into local file or user cloud storage
Copyright 2024 Ubiterra Corporation
"""


@dataclass
class Storage(ABC):
    """
    Abstract class that models user storage for backing up ZoneVu data.
    """
    VersionTag: ClassVar[str] = 'Version'

    @abstractmethod
    def save(self, blob_path: Path, data: bytes, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Save a blob or file
        :param blob_path: blob/file path&name within container/parent-dir
        :param data: data to upload
        :param tags: optional metadata tags
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def retrieve(self, blob_path: Path) -> bytes:
        """
        Retrieve a blob or file
        :param blob_path: blob/file path&name within container/parent-dir
        :return: the byte data from the file/blob
        """

    @abstractmethod
    def exists(self, blob_path: Path) -> bool:
        """
        Check for existence of a blob, and if it exists, return its Version(row version) tag.
        :param blob_path: local blob path/name
        :return: a flag which is True if blob does exist
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def tags(self, blob_path: Path) -> Optional[Dict[str, str]]:
        """
        Get the metadata tags for this blob
        :param blob_path: path/name of blob within the container
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def list(self, dir_path: Path) -> List[Path]:
        """
        Lists blobs in the specified container with the given dir path.
        :param dir_path:
        :return: List of blob names in the dir path.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def delete(self, blob_path: Path) -> None:
        """
        Deletes blobs from the specified container.
        :param blob_path:
        """
        raise NotImplementedError("Subclasses must implement this method")

    def save_text(self, blob_path: Path, text: str, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Save a text string with optional tags to a file or blob
        :param blob_path:
        :param text:
        :param tags:
        :return:
        """
        data = bytes(text, 'utf-8')
        self.save(blob_path, data, tags)

    def retrieve_text(self, blob_path: Path) -> str:
        """
        Retrieves text from a file or blob
        :param blob_path:
        :return:
        """
        data = self.retrieve(blob_path)
        text = str(data, 'utf-8')
        return text

    def version(self, blob_path: Path) -> Optional[str]:
        """
        Get the version metadata tag for this blob
        :param blob_path: path/name of blob within the container
        :return:
        """
        tags = self.tags(blob_path)
        if tags is None or self.VersionTag not in tags:
            return None
        return tags[self.VersionTag]

    def save_array(self, path: Path, array: Optional[np.ndarray]) -> None:
        """
        Saves a numpy array to storage
        :param path:
        :param array:
        :return:
        """
        if array is None:
            return
        in_memory_file = io.BytesIO()
        np.save(in_memory_file, array)  # type: ignore
        array_bytes = in_memory_file.getvalue()
        self.save(path, array_bytes, None)

    def retrieve_array(self, path) -> Optional[np.ndarray]:
        """
        Retrieves a numpy array from storage
        :param path:
        :return:
        """
        file_exists = self.exists(path)
        if not file_exists:
            return None
        raw_bytes = self.retrieve(path)
        in_memory_file = io.BytesIO(raw_bytes)
        array = np.load(in_memory_file) if file_exists else None  # type: ignore
        return array


class FileStorage(Storage):
    """
    Implementation of storage service for local file storage
    """
    zonevu_dir: Path    # The absolute path to the directory for all ZoneVu data for this company.

    def __init__(self, parent_folder: Path):
        self.zonevu_dir = parent_folder

    def save(self, blob_path: Path, data: bytes, tags: Optional[Dict[str, str]] = None) -> None:
        # Write out well json
        abs_blob_path = self.zonevu_dir / blob_path
        abs_blob_path.parent.mkdir(parents=True, exist_ok=True)  # Make sure directory for file exists.
        # Write file
        with open(abs_blob_path, "wb") as f:
            f.write(data)
        # Write tags
        if tags:
            abs_tags_path = abs_blob_path.parent / ('%s_tags.json' % blob_path.stem)
            with open(abs_tags_path, "w") as f:
                json.dump(tags, f)

    def retrieve(self, blob_path: Path) -> bytes:
        """
        Retrieve a blob or file
        :param blob_path: blob/file path&name within container/parent-dir
        :return: the byte data from the file/blob
        """
        abs_blob_path = self.zonevu_dir / blob_path
        data = abs_blob_path.read_bytes()
        return data

    def exists(self, blob_path: Path) -> bool:
        abs_blob_path = self.zonevu_dir / blob_path
        exists = abs_blob_path.is_file()
        return exists

    def tags(self, blob_path: Path) -> Optional[Dict[str, str]]:
        abs_blob_path = self.zonevu_dir / blob_path
        abs_tags_path = abs_blob_path.parent / ('%s_tags.json' % blob_path.stem)
        if abs_tags_path.exists():
            with abs_tags_path.open() as tags_file:
                tags = json.load(tags_file)
            return tags
        return None

    def list(self, dir_path: Path) -> List[Path]:
        abs_dir_path = self.zonevu_dir / dir_path
        dir_exists = abs_dir_path.is_dir()
        files: List[Path] = []
        if dir_exists:
            files = [file for file in abs_dir_path.glob("*")]
        return files

    def delete(self, blob_path: Path) -> None:
        abs_blob_path = self.zonevu_dir / blob_path
        abs_blob_path.unlink()


@dataclass_json
@dataclass
class AzureCredential:
    url: str  # Azure storage account base URL
    container: str  # Azure storage container name for ZoneVu data
    token: str  # Azure storage account authorization key
    path: Optional[str] = None  # Relative path below url to a blob if this is specific to a single blob

    @property
    def full_url(self) -> str:
        return str(Path(self.url) / self.container / self.path)


class AzureStorage(Storage):
    """
    Implementation of storage service for Azure Blob Storage
    """
    credential: AzureCredential
    _blob_svc: BlobServiceClient
    _container_svc: ContainerClient

    def __init__(self, credential: AzureCredential):
        self.credential = credential
        self._blob_svc = BlobServiceClient(account_url=credential.url, credential=credential.token)
        self._container_svc = self._blob_svc.get_container_client(credential.container)

    def save(self, blob_path: Path, data: bytes, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Upload a blob
        :param blob_path: path/name of blob within the container
        :param data: data to upload
        :param tags: optional metadata tags
        :return:
        """
        client = self._blob_svc.get_blob_client(container=self.credential.container, blob=str(blob_path))
        client.upload_blob(data, overwrite=True)
        if tags is not None:
            client.set_blob_tags(tags)

    def retrieve(self, blob_path: Path) -> bytes:
        """
        Retrieve a blob or file
        :param blob_path: blob/file path&name within container/parent-dir
        :return: the byte data from the file/blob
        """
        client = self._blob_svc.get_blob_client(container=self.credential.container, blob=str(blob_path))
        data = client.download_blob().readall()
        return data

    def exists(self, blob_path: Path) -> bool:
        """
        Check for existence of a blob, and if it exists, return its Version(row version) tag.
        :param blob_path: path/name of blob within the container
        :return: a flag which is True if blob does exist
        """
        client = self._blob_svc.get_blob_client(container=self.credential.container, blob=str(blob_path))
        does_exist = client.exists()
        return does_exist

    def tags(self, blob_path: Path) -> Optional[Dict[str, str]]:
        """
        Get the metadata tags for this blob
        :param blob_path: path/name of blob within the container
        :return:
        """
        client = self._blob_svc.get_blob_client(container=self.credential.container, blob=str(blob_path))
        does_exist = client.exists()
        if does_exist:
            tags: Dict[str, str] = client.get_blob_tags()
            return tags
        return None

    def list(self, dir_path: Path) -> List[Path]:
        """
        Lists blobs in the specified container with the given prefix.
        :param dir_path:
        :return: List of blob names matching the prefix.
        """
        client = self._blob_svc.get_container_client(self.credential.container)
        blob_list = [Path(blob.name) for blob in client.list_blobs(name_starts_with=str(dir_path))]
        return blob_list

    def delete(self, blob_path: Path) -> None:
        """
        Deletes blobs from the specified container.
        :param blob_path: path/name of blob within the container
        """
        client = self._blob_svc.get_container_client(self.credential.container)
        client.delete_blob(str(blob_path))
