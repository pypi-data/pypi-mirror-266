import sys
from collections.abc import MutableSequence
from typing import TypeVar, overload, Iterable, Iterator, Callable, SupportsIndex
# from _typeshed import SupportsRichComparison, SupportsRichComparisonT


__all__ = ['VectorDeprecated']

_T = TypeVar('_T')


class VectorDeprecated(MutableSequence[_T]):
    __slots__ = ('_data',)

    @overload
    def __init__(self): self._data = list()
    @overload
    def __init__(self, __iterable: Iterable[_T]):
        self._data = list(__iterable)

    def __repr__(self) -> str:
        return self.__class__.__name__ + repr(self._data)

    def __str__(self) -> str: return str(self._data)

    def copy(self) -> 'VectorDeprecated': return VectorDeprecated(self._data.copy())

    def append(self, __object: _T) -> None: self._data.append(__object)

    def extend(self, __iterable: Iterable[_T]) -> None:
        self._data.extend(__iterable)

    def pop(self, __index: SupportsIndex = -1): return self._data.pop(__index)

    def index(self, __value: _T, __start: SupportsIndex = 0, 
              __stop: SupportsIndex = sys.maxsize) -> int:
        return self._data.index(__value, __start, __stop)
    
    def count(self, __value: _T) -> int: return self._data.count(__value)

    def insert(self, __index: SupportsIndex, __object: _T) -> None: 
        self._data.insert(__index, __object)

    def remove(self, __value: _T) -> None: self._data.remove(__value)

    def sort(self, *, key: Callable, reverse: bool = False) -> None: 
        self._data.sort(key=key, reverse=reverse)
    
    def __len__(self) -> int: return len(self._data)

    def __iter__(self) -> Iterator[_T]: return iter(self._data)

    def __hash__(self) -> int: return hash(self._data)

    @overload
    def __getitem__(self, __i: SupportsIndex) -> _T: return self._data[__i]
    '''
    @overload
    def __getitem__(self, __s: slice) -> 'Vector'[_T]: return self._data[__s]
    @overload
    def __setitem__(self, __key: SupportsIndex, __value: _T) -> None: ...
    @overload
    def __setitem__(self, __key: slice, __value: Iterable[_T]) -> None: ...
    def __delitem__(self, __key: SupportsIndex | slice) -> None: ...
    # Overloading looks unnecessary, but is needed to work around complex mypy problems
    @overload
    def __add__(self, __value: list[_T]) -> list[_T]: ...
    @overload
    def __add__(self, __value: _T) -> list[_T]: ...
    def __iadd__(self, __value: Iterable[_T]) -> Self: ...  # type: ignore[misc]
    def __mul__(self, __value: SupportsIndex) -> list[_T]: ...
    def __rmul__(self, __value: SupportsIndex) -> list[_T]: ...
    def __imul__(self, __value: SupportsIndex) -> 'Vector': ...
    def __contains__(self, __key: object) -> bool: ...
    def __reversed__(self) -> Iterator[_T]: ...
    def __gt__(self, __value: list[_T]) -> bool: ...
    def __ge__(self, __value: list[_T]) -> bool: ...
    def __lt__(self, __value: list[_T]) -> bool: ...
    def __le__(self, __value: list[_T]) -> bool: ...
    def __eq__(self, __value: object) -> bool: ...
    '''
