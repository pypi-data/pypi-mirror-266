# hyphenfrac
![Pepy Total Downlods](https://img.shields.io/pepy/dt/hyphenfrac)
![PyPI - Version](https://img.shields.io/pypi/v/hyphenfrac)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hyphenfrac)

A basic utility designed to prettify and visualize fractions.

## Usage
### Prerequisites
- A terminal accepting ANSI codes

### Displaying Fractions
Displaying a prettified fraction from a number:
```python
>>> import hyphenfrac, random
>>> hyphenfrac.visualize_number(random.randint(1, 100)/random.randint(1, 100))
20
-- + 1
49
>>>
```
You may also assign this value to a variable:
```python
>>> import hyphenfrac
>>> foo = hyphenfrac.make_pretty(1, 10)
>>> print(foo)
1
--
10
>>>
```
You can optionally use a dash instead of a hyphen-minus character for a vinculum:
```python
>>> import hyphenfrac
>>> hyphenfrac.visualize("ln(x) - ln(y)", "x - y", hyphen=False)
ln(x) - ln(y)
―――――――――――――
    x - y
>>>
```

### Creating Fractions
Fractions could also be used as their own object:
```python
>>> from hyphenfrac import Fraction
>>> myFrac = Fraction(numerator="Vd", denominator="CL", operation="", whole="ln(2)", hyphen=False)
>>> myFrac.display()
Vd
――  ln(2)
CL
>>> isinstance(myFrac, Fraction)
True
>>>
```