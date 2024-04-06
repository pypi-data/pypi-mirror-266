# Simple Unit (Python implementation)

[![Anaconda-Server Badge](https://anaconda.org/cosmoloj/unit_simple/badges/version.svg)](https://anaconda.org/cosmoloj/unit_simple)
[![PyPI repository Badge](https://badge.fury.io/py/unit_simple.svg)](https://badge.fury.io/py/unit_simple)

* [Standard usage](#Utilisation-standard)
* [Operator overloading usage](#Utilisation-avec-surcharge-des-opérateurs)



## Standard usage

The Simple Unit Python implementation standard usage refers to method and classes defined in the Simple Unit specification.

Usage of transformed units:

```py
import unit_simple as su

m = su.FundamentalUnit()
km = m.scale_multiply(1000)
cm = m.scale_divide(100)
cmToKm = cm.get_converter_to(km)

cmToKm.convert(3) # 0.00003
cmToKm.inverse().convert(0.00003) # 3
```

Usage of derived units:

```py
import unit_simple as su

m = su.FundamentalUnit()
km = m.scale_multiply(1000)

km2 = su.DerivedUnit(km.factor(2))
cm = m.scale_divide(100)
cm2 = su.DerivedUnit(cm.factor(2))
km2Tocm2 = km2.get_converter_to(cm2)

km2Tocm2.convert(3) # 30000000000
km2Tocm2.inverse().convert(30000000000) # 3
```

Usage of derived units combining dimensions:

```py
import unit_simple as su

m = su.FundamentalUnit()
kg = su.FundamentalUnit()
g = kg.scale_divide(1000)
ton = kg.scale_multiply(1000)
gPerM2 = su.DerivedUnit(g, m.factor(-2))
km = m.scale_multiply(1000)
tonPerKm2 = su.DerivedUnit(ton, km.factor(-2))
cm = m.scale_divide(100)
tonPerCm2 = su.DerivedUnit(ton, cm.factor(-2))
gPerM2ToTonPerKm2 = gPerM2.get_converter_to(tonPerKm2)
gPerM2ToTonPerCm2 = gPerM2.get_converter_to(tonPerCm2)

gPerM2ToTonPerKm2.convert(1) # 1
gPerM2ToTonPerKm2.inverse().convert(3) # 3
gPerM2ToTonPerCm2.convert(1) # 1e-4
gPerM2ToTonPerCm2.convert(3) # 3e-10
gPerM2ToTonPerCm2.offset() # 0.0
gPerM2ToTonPerCm2.scale() # 1e-10
gPerM2ToTonPerCm2.inverse().offset() # -0.0
gPerM2ToTonPerCm2.inverse().convert(3e-10) # 3
```

Usage of temperatures (affine and linear conversions):

```py
import unit_simple as su

k = su.FundamentalUnit()
c = k.shift(273.15)
kToC = k.get_converter_to(c)

kToC.convert(0) # -273.15
kToC.inverse().convert(0) # 273.15

# combined with other units, temperatures only keep their linear conversion part
m = su.FundamentalUnit()
cPerM = su.DerivedUnit(c, m.factor(-1))
kPerM = su.DerivedUnit(k, m.factor(-1))
kPerMToCPerM = kPerM.get_converter_to(cPerM)

kPerMToCPerM.convert(3) # 3
kPerMToCPerM.inverse().convert(3) # 3
```

Usage of non-decimal conversions:

```py
import unit_simple as su

m = su.FundamentalUnit()
km = m.scale_multiply(1000.)

s = su.FundamentalUnit()
h = s.scale_multiply(3600.)

ms = su.DerivedUnit(m, s.factor(-1))
kmh = su.DerivedUnit(km, h.factor(-1))

msToKmh = ms.get_converter_to(kmh)

msToKmh.convert(100.) # 360
msToKmh.inverse().convert(18.) # 5
```

## Operator overloading usage

The Simple Unit Python implementation provides an extension of the base specification to overloads some language operators.

Usage of transformed units:

```py
import unit_simple as su

m = su.FundamentalUnit()
km = m * 1000
cm = m / 100
cmToKm = cm >> km

cmToKm(3) # 0.00003
(~cmToKm)(0.00003) # 3
```

Usage of derived Units:

```py
import unit_simple as su

m = su.FundamentalUnit()
km = m * 1000

km2 = km ** 2
cm = m / 100
cm2 = cm ** 2
km2Tocm2 = km2 >> cm2

km2Tocm2(3) # 30000000000
(~km2Tocm2)(30000000000) # 3
```

Usage of derived units combining dimensions:

```py
import unit_simple as su

m = su.FundamentalUnit()
kg = su.FundamentalUnit()
g = kg / 1000
ton = kg * 1000
gPerM2 = g / m ** 2
km = m * 1000
tonPerKm2 = ton * ~km ** 2
cm = m / 100
tonPerCm2 = ton / cm ** 2
gPerM2ToTonPerKm2 = gPerM2 >> tonPerKm2
gPerM2ToTonPerCm2 = tonPerCm2 << gPerM2

gPerM2ToTonPerKm2(1) # 1
(~gPerM2ToTonPerKm2)(3) # 3
gPerM2ToTonPerCm2(1) # 1e-4
gPerM2ToTonPerCm2(3) # 3e-10
gPerM2ToTonPerCm2.offset() # 0.0
gPerM2ToTonPerCm2.scale() # 1e-10
(~gPerM2ToTonPerCm2).offset() # -0.0
(~gPerM2ToTonPerCm2)(3e-10) # 3
```

Usage of temperatures (affine and linear conversions):

```py
import unit_simple as su

k = su.FundamentalUnit()
c = k + 273.15
kToC = k >> c

kToC(0) # -273.15
(~kToC)(0) # 273.15

# combined with other units, temperatures only keep their linear conversion part
m = su.FundamentalUnit()
cPerM = c / m
kPerM = k / m
kPerMToCPerM = kPerM >> cPerM

kPerMToCPerM(3) # 3
(~kPerMToCPerM)(3) # 3
```

Usage of non-decimal conversions:

```py
import unit_simple as su

m = su.FundamentalUnit()
km = m * 1000.

s = su.FundamentalUnit()
h = s * 3600.

ms = m / s
kmh = km / h

msToKmh = ms >> kmh

msToKmh(100.) # 360
(~msToKmh)(18.) # 5
```