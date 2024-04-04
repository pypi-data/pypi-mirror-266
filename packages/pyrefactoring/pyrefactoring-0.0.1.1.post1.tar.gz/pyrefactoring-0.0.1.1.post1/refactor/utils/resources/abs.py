import os
import base64
import hashlib
from pathlib import Path
from abc import ABC, abstractmethod


class ResourceInterface(ABC):
  """
  Interface of resource which is used for load content from 
  various source such as file, base64 encoded or URL.
  """

  def __init__(self, ori: str):
    """
    Class constructor.
    :param ori: origin source. Can be file, base64 encoded or URL.
    """
    self._ori: str = None
    self._hash: str = None
    self._data: bytes = None
    self._base64: str = None
    self.load(ori)

  @property
  def ori(self):
    """
    Get origin source.
    """
    return self._ori

  @property
  def data(self):
    """
    Get resource data.
    """
    if self._data is None:
      return self.load(self.ori).data
    return self._data
  
  @property
  def hash(self):
    """
    Get resource hash.
    """
    if self._hash is None:
      self._hash = hashlib.md5(self.data).hexdigest()
    return self._hash
  
  @property
  def base64(self):
    """
    Get resource base64.
    """
    if self._base64 is None:
      self._base64 = str(base64.b64encode(self.data))
    return self._base64

  def checksum(self, md5: str) -> bool:
    """
    Perform checksum.
    :param md5: md5 hash to be checked.
    "return:    true|false
    """
    return self.hash == md5

  @abstractmethod
  def load(self, ori: str):
    """
    Load resource from origin source.
    :param ori: origin source. Can be file, base64 encoded or URL.
    :return:    loaded resource.
    """
    self._ori = ori
    self._hash = None
    self._data = None
    self._base64 = None
    return self
  
  def save(self, dir: str = os.path.join(os.getcwd(), 'res'), name: str = None, format: str = 'bin') -> Path:
    """
    Save resource to local file.
    :param dir:     saved directory.
    :param name:    saved filename.
    :param format:  saved format.
    :return:        path to saved file.
    """
    dir = Path(dir).expanduser().resolve()
    dir.mkdir(exist_ok=True)
    path = dir.joinpath(f'{self.hash if name is None else name}.{format}')
    path.write_bytes(self._data)
    return path
