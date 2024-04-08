# pyunitconverter

## Description

`pyunitconverter` is a Python library of functions for unit conversions.

## Modules

- `pyunitconverter.energy`: conversion of energy units
- `pyunitconverter.length`: conversion of length units
- `pyunitconverter.mass`: conversion of mass units
- `pyunitconverter.prefixes`: prefixes for units of the International System (ie: kilo, mega, ...)
- `pyunitconverter.speed`: conversion of speed units
- `pyunitconverter.temperature`: conversion of temperature units
- `pyunitconverter.time`: conversion of time units
- `pyunitconverter.volume`: conversion of volume units

## Installation

```bash
python -m pip install pyunitconverter
```

## Usage
Example 1
```python
from pyunitconverter.mass import ounces_to_kilograms

mass = 10

print(f"{mass} ounces = {ounces_to_kilograms(mass)} kg")
```

Example 2
```python
from pyunitconverter.prefixes import PREFIX_KILO

length = 5.2

print(f"{length} km = {PREFIX_KILO*length} m")
```