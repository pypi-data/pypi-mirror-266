from abc import ABC
from typing import Optional, TypedDict
from pathlib import Path
from urllib.parse import urlparse

class Import(TypedDict):
    name: str
    type: str
    hash: Optional[str]
    info: Optional[dict]
    status: Optional[str]

class AvailableModel(TypedDict):
    name: str

class ImportSource(ABC):
    name: str

class ImportSourceFile(ImportSource):
    def __init__(self, path: str, name: Optional[str] = None):
        self.raw_path = path
        self._url = urlparse(self.raw_path)
        self._path = Path(self._url.path if self.is_url() else self.raw_path)
        self.extension = self._path.suffix
        self.name = name or self._path.name

    def is_url(self):
        return bool(self._url.netloc)

class ImportSourceTable(ImportSource):
    def __init__(self, database: str, schema: str, table: str, name: Optional[str] = None):
        self.database = database
        self.schema = schema
        self.table = table
        self.name = name or self.fqn

    @property
    def fqn(self):
        return f"{self.database}.{self.schema}.{self.table}"
