from abc import ABC, abstractmethod
from datetime import date as dateonly, time as timeonly, datetime
from collections.abc import Iterable, Mapping, Sequence

BlobTypes = bytes|bytearray|memoryview
DateTypes = dateonly|timeonly|datetime   # Note that datetime in Python derives from date

# Frid type (Flexibly represented inteactive data)

# The Prime types including all types supported internally by default

class FridMixin(ABC):
    """The abstract base frid class to be loadable and dumpable.

    A frid class needs to implement three methods:
    - A class method `frid_keys()` that returns a list of acceptable keys
      for the class (default includes the class name);
    - A class method `frid_from()` that constructs and object of this class
      with the name, and a set of positional and keyword arguments
      (default is to check the name against acceptable keys, and then call
      the constructor with these arguments).
    - A instance method `frid_repr()` that converts the object to a triplet:
      a name, a list of positional values, and a dict of keyword values
      (this method is abstract).
    """
    @classmethod
    def frid_keys(cls) -> Iterable[str]:
        """The list of keys that the class provides; the default containing class name only."""
        return [cls.__name__]

    @classmethod
    def frid_from(cls, name: str, *args: 'FridValue', **kwds: 'FridValue') -> 'FridMixin':
        """Construct an instance with given name and arguments."""
        assert name in cls.frid_keys()
        return cls(*args, **kwds)

    @abstractmethod
    def frid_repr(self) -> tuple[str,Sequence['FridValue'],Mapping[str,'FridValue']]:
        """Converts an instance to a triplet of name, a list of positional values,
        and a dict of keyword values.
        """
        raise NotImplementedError

FridPrime = str|float|int|bool|BlobTypes|DateTypes|None
StrKeyMap = Mapping[str,Mapping|Sequence|FridPrime|FridMixin]
FridValue = StrKeyMap|Sequence[StrKeyMap|Sequence|FridPrime|FridMixin]|FridPrime|FridMixin
FridArray = Sequence[FridValue]
