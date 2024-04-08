from typing import Generic, Optional, TypeVar

from ..utilcollections.abc import Linear

T = TypeVar('T', bound=Linear)


class Uncertainty(Generic[T]):
    __slots__ = ('_uncertainty',)

    def __init__(self, /, uncertainty: Optional[T] = None) -> None:
        self.uncertainty_value = uncertainty

    @property
    def uncertainty_value(self) -> T | None: return self._uncertainty

    @uncertainty_value.setter
    def uncertainty_value(self, uncertainty: Optional[T] = None) -> None:
        if uncertainty is not None:
            uncertainty = abs(uncertainty)
        self._uncertainty = uncertainty
