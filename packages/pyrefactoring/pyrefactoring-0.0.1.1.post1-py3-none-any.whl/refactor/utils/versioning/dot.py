
class DotVersion:
  """
  A version patterns use numbers and dot as separator such as x.y.z
  """

  @property
  def numbers(self):
    """
    Get version numbers as array.
    """
    return self._numbers

  def __init__(self, version: str, *args, **kwds):
    """
    Class constructor.
    :param version: version string with patterns like x.y.z
    :param args:    additional arguments.
    :param kwds:    additional keyword arguments.
    """
    self._numbers = [int(x) for x in version.split('.')]

  def precedence(self, other, *args, **kwds) -> int:
    """
    Precedence when compare to another.
    :param other:   other dot version.
    :param args:    additional arguments.
    :param kwds:    additional keyword arguments.
    """
    if not isinstance(other, DotVersion):
      c1 = self.__class__.__name__
      c2 = other.__class__.__name__
      raise TypeError(f'{c1} cannot be compared to {c2}')
    # Calculate precedence.
    l1, l2 = len(self.numbers), len(other.numbers)
    for i in range(min(l1, l2)):
      x1, x2 = self.numbers[i], other.numbers[i]
      if x1 == x2:
        continue
      else:
        return -1 if x1 < x2 else 1
    # Longer is langer.
    return -1 if l1 < l2 else 1 if l1 > l2 else 0

  def __str__(self):
    return '.'.join(self._numbers)
  
  def __eq__(self, __value: object) -> bool:
    return self.precedence(__value) == 0
  
  def __ne__(self, __value: object) -> bool:
    return self.precedence(__value) != 0
  
  def __gt__(self, __value: object) -> bool:
    return self.precedence(__value) > 0
  
  def __ge__(self, __value: object) -> bool:
    return self.precedence(__value) >= 0
  
  def __lt__(self, __value: object) -> bool:
    return self.precedence(__value) < 0
  
  def __le__(self, __value: object) -> bool:
    return self.precedence(__value) <= 0
