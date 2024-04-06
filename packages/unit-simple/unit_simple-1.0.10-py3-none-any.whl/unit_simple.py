"""Simple Unit module"""

from enum import Enum


class UnitConverter:
    """convertisseur d'unites"""

    def __init__(self, scale: float != 0., offset: float = 0.0, inverse=None):
        assert scale != 0.
        self._scale = scale
        self._offset = offset
        if scale == 1. and offset == 0. and inverse is None:
            self._inverse = self
        else:
            self._inverse = UnitConverter(scale=1. / self._scale,
                                          offset=-self._offset / self._scale,
                                          inverse=self) if inverse is None else inverse

    def scale(self):
        """pente (facteur d'echelle) de la conversion"""
        return self._scale

    def offset(self):
        """decalage d'origine d'echelle"""
        return self._offset

    def inverse(self):
        """convertisseur inverse au convertisseur courant : de son unite cible vers son unite source"""
        return self._inverse

    def linear(self):
        """convertisseur lineaire conservant uniquement le facteur d'echelle du convertisseur d'appel"""
        # comparaison volontaire avec un double
        if self._offset == 0.:
            return self
        return UnitConverters.linear(scale=self._scale)

    def linear_pow(self, power: float):
        """convertisseur lineaire conservant uniquement le facteur d'echelle du convertisseur d'appel, eleve a la
        puissance en parametre"""
        # comparaison volontaire avec des doubles
        if self._offset == 0. and power == 1.:
            return self
        return UnitConverters.linear(scale=self._scale ** power)

    def convert(self, value: float) -> float:
        """exprime la valeur en parametre dans l'unite cible du convertisseur en faisant l'hypothese qu'elle est
        exprimee dans son unite source"""
        return value * self._scale + self._offset

    def concatenate(self, converter):
        """convertisseur correspondant a la combinaison de la conversion du convertisseur en parametre suivie de la
        conversion du convertisseur d'appel"""
        return UnitConverter(scale=converter.scale() * self.scale(),
                             offset=self.convert(converter.offset()))

    def __invert__(self):
        return self.inverse()

    def __call__(self, *args, **kwargs):
        return self.convert(args[0])


class UnitConverters(Enum):
    """utility unit converter factory"""
    _IDENTITY = UnitConverter(scale=1.0)

    @staticmethod
    def linear(scale):
        """build a linear converter"""
        return UnitConverter(scale=scale)

    @staticmethod
    def offset(offset):
        """build an offset converter"""
        return UnitConverter(scale=1.0, offset=offset)

    @staticmethod
    def identity():
        """get the instance of the identity converter"""
        return UnitConverters._IDENTITY.value


class Factor:
    """representation d'une unite elevee a une puissance rationnelle"""

    def __init__(self, unit, numerator: int = 1, denominator: int = 1):
        if isinstance(unit, Unit):
            self._unit = unit
            self._numerator = numerator
            self._denominator = denominator
        else:
            self._unit = unit.dim()
            self._numerator = numerator * unit.numerator()
            self._denominator = denominator * unit.denominator()

    def dim(self):
        """dimension (unite) du facteur"""
        return self._unit

    def numerator(self) -> int:
        """numerateur de la puissance rationnelle du facteur"""
        return self._numerator

    def denominator(self) -> int:
        """denominateur de la puissance rationnelle du facteur"""
        return self._denominator

    def power(self) -> float:
        """puissance du facteur"""
        return self._numerator if self._denominator == 1. else self._numerator / self._denominator

    def __mul__(self, other):
        return DerivedUnit(self, other)

    def __truediv__(self, other):
        return DerivedUnit(self, Factor(other, -1))

    def __invert__(self):
        return DerivedUnit(Factor(self, -1))


class Unit(Factor):
    """classe abstraite de fonctionnalites communes a toutes les unites"""

    def __init__(self):
        super().__init__(self, numerator=1, denominator=1)

    def get_converter_to(self, target) -> UnitConverter:
        """construit un convertisseur de l'unite d'appel vers l'unite cible en parametre"""
        return target.to_base().inverse().concatenate(converter=self.to_base())

    def to_base(self) -> UnitConverter:
        """construit un convertisseur vers le jeu d'unites fondamentales sous-jascent a l'unite d'appel"""

    def shift(self, value: float):
        """construit une unite transformee en decalant l'origine de l'echelle de la valeur en parametre par rapport a
        l'unite d'appel"""
        return TransformedUnit(to_reference=UnitConverters.offset(offset=value), reference=self)

    def scale_multiply(self, value: float):
        """construit une unite transformee en multipliant le facteur d'echelle par la valeur en parametre par rapport a
        l'unite d'appel"""
        return TransformedUnit(to_reference=UnitConverters.linear(scale=value), reference=self)

    def scale_divide(self, value: float):
        """construit une unite transformee en divisant le facteur d'echelle par la valeur en parametre par rapport a
        l'unite d'appel"""
        return self.scale_multiply(value=1.0 / value)

    def factor(self, numerator: int, denominator: int = 1):
        """construit un facteur de l'unite d'appel eleve a la puissance rationnelle dont le numerateur et le
        denominateur sont en parametre"""
        return Factor(self, numerator=numerator, denominator=denominator)

    def __add__(self, other):
        return self.shift(other)

    def __sub__(self, other):
        return self.shift(-other)

    def __mul__(self, other):
        if isinstance(other, Factor):
            return super().__mul__(other)
        return self.scale_multiply(other)

    def __truediv__(self, other):
        if isinstance(other, Factor):
            return super().__truediv__(other)
        return self.scale_divide(other)

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            return DerivedUnit(self.factor(power))
        raise ValueError

    def __rshift__(self, other):
        return self.get_converter_to(other)

    def __lshift__(self, other):
        return self.get_converter_to(other).inverse()


class FundamentalUnit(Unit):
    """unite definie par elle-meme"""

    def to_base(self) -> UnitConverter:
        return UnitConverters.identity()


class TransformedUnit(Unit):
    """unite definie par transformation d'une unite de reference"""

    def __init__(self, to_reference: UnitConverter, reference: Unit):
        super().__init__()
        self._to_reference = to_reference
        self._reference = reference

    def to_reference(self) -> UnitConverter:
        """convertisseur de l'unite d'appel vers l'unite de reference"""
        return self._to_reference

    def reference(self) -> Unit:
        """unite de reference de l'unite transformer"""
        return self._reference

    def to_base(self) -> UnitConverter:
        return self.reference().to_base().concatenate(converter=self.to_reference())


class DerivedUnit(Unit):
    """unite definie comme combinaison de facteurs d'unites, chacune elevee a une puissance rationnelle"""

    def __init__(self, *definition):
        super().__init__()
        self._definition = definition

    def definition(self):
        """collection des facteurs de definition de l'unite derivee"""
        return self._definition

    def to_base(self) -> UnitConverter:
        transform = UnitConverters.identity()
        for factor in self._definition:
            transform = factor.dim().to_base().linear_pow(factor.power()).concatenate(transform)
        return transform


class Metric(Enum):
    """definition des prefixes du systeme metrique"""
    YOTTA = 1e24
    ZETTA = 1e21
    EXA = 1e18
    PETA = 1e15
    TERA = 1e12
    GIGA = 1e9
    MEGA = 1e6
    KILO = 1000
    HECTO = 100
    DEKA = 10
    DECI = 1e-1
    CENTI = 1e-2
    MILLI = 1e-3
    MICRO = 1e-6
    NANO = 1e-9
    PICO = 1e-12
    FEMTO = 1e-15
    ZEPTO = 1e-21
    YOCTO = 1e-24

    def __init__(self, factor: float):
        self._factor = factor

    def prefix(self, unit: Unit) -> TransformedUnit:
        """application du prefixe du systeme metrique a une unite"""
        return unit.scale_multiply(value=self._factor)

    def __call__(self, *args, **kwargs):
        return self.prefix(args[0])
