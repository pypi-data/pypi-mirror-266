import base64
import urllib.request
from pathlib import Path
from refactor.utils.resources import ResourceInterface


def from_file(res: ResourceInterface, ori: str) -> ResourceInterface:
  """
  Load resource data from file.
  :param res: resource to be loaded.
  :param ori: path to file.
  :return:    resource.
  """
  path = Path(ori).expanduser().resolve()
  res._data = path.read_bytes()
  res._ori = path
  return res

def from_base64(res: ResourceInterface, ori: str) -> ResourceInterface:
  """
  Load resource data from base64 encoded string.
  :param res: resource to be loaded.
  :param ori: base64 string.
  :return:    resource.
  """
  res._data = base64.b64decode(ori, validate=True)
  return res

def from_url(res: ResourceInterface, ori: str) -> ResourceInterface:
  """
  Load resource data from URL.
  :param res: resource to be loaded.
  :param ori: url string.
  :return:    resource.
  """
  with urllib.request.urlopen(ori) as response:
    res._data = response.read()
    return res

"""
Register all available resource loaders.
"""
LOADERS = (from_file, from_base64, from_url)

def load(res: ResourceInterface, ori: str):
  """
  Load resource from origin source.
  :param ori: origin source.
  :return:    loaded resource.
  """
  for loader in LOADERS:
    try:
      return loader(res, ori)
    except:
      continue
  raise AssertionError('Cannot load resource from invalid origin source.')


class Resource(ResourceInterface):
  """
  This class is base class of resource which is used to load and 
  perform operations in a resource file, base64 encoded or URL.
  """
  
  def load(self, ori: str) -> ResourceInterface:
    """
    Load resource from origin source.
    :param ori: origin source.
    :return:    loaded resource.
    """
    return load(super().load(ori), ori)
