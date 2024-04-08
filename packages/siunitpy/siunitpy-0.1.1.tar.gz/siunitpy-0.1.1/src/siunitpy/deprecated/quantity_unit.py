from ..utilcollections.constclass import ConstClass
from ..quantity import Quantity
from ..unit import Unit
from ..unitconst import UnitConst

__all__ = ['QuantityUnit', 'si']

class QuantityUnit:
    '''`QuantityUnit` is a unit'''
    __slots__ = ('_unit',)
    def __init__(self, unit: Unit):
        self._unit = unit

    def __mul__(self, other: 'QuantityUnit'):
        return QuantityUnit(self._unit + other._unit)
    
    def __truediv__(self, other: 'QuantityUnit'):
        return QuantityUnit(self._unit - other._unit)
    
    def __pow__(self, expo):
        return QuantityUnit(self._unit * expo)
    
    def __rmatmul__(self, value):
        return Quantity(value, self._unit)


class si(ConstClass):
    one = QuantityUnit(UnitConst.DIMENSIONLESS)
    m = QuantityUnit(UnitConst.METER)
    kg = QuantityUnit(UnitConst.KILOGRAM)
    s = QuantityUnit(UnitConst.SECOND)
    A = QuantityUnit(UnitConst.AMPERE)
    K = QuantityUnit(UnitConst.KELVIN)
    mol = QuantityUnit(UnitConst.MOLE)
    cd = QuantityUnit(UnitConst.CANDELA)
    # derived
    Hz = QuantityUnit(UnitConst.HERTZ)
    rad = QuantityUnit(UnitConst.RADIAN)
    sr = QuantityUnit(UnitConst.STERADIAN)
    N = QuantityUnit(UnitConst.NEWTON)
    Pa = QuantityUnit(UnitConst.PASCAL)
    J = QuantityUnit(UnitConst.JOULE)
    W = QuantityUnit(UnitConst.WATT)
    C = QuantityUnit(UnitConst.COULOMB)
    V = QuantityUnit(UnitConst.VOLT)
    F = QuantityUnit(UnitConst.FARAD)
    ohm = QuantityUnit(UnitConst.OHM)
    S = QuantityUnit(UnitConst.SIEMENS)
    Wb = QuantityUnit(UnitConst.WEBER)
    T = QuantityUnit(UnitConst.TESLA)
    H = QuantityUnit(UnitConst.HENRY)
    # celsius = QuantityUnit(UnitConst.DEGREE_CELSIUS)
    lm = QuantityUnit(UnitConst.LUMEN)
    lx = QuantityUnit(UnitConst.LUX)
    Bq = QuantityUnit(UnitConst.BECQUEREL)
    Gy = QuantityUnit(UnitConst.GRAY)
    Sv = QuantityUnit(UnitConst.SIEVERT)
    kat = QuantityUnit(UnitConst.KATAL)