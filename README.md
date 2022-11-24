<h1 align="center">
regex_gen
</h1>

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/TitaniumBrain/regex_gen?sort=semver)
![PyPI - Downloads](https://img.shields.io/pypi/dm/regex_gen?color=orange&label=%E2%AC%87%20downloads)
![GitHub](https://img.shields.io/github/license/TitaniumBrain/regex_gen?color=blue)
![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)

A simple, object oriented, regular expression generator.

`regex_gen` is a package aimed at providing a simple syntax for composing
regular expressions, without having to memorise their syntax.

It **does not** guarantee that the expressions generated are the most efficient.

It is assumed that users have some understanding of [regular expressions](https://docs.python.org/3/library/re.html), as there's nothing preventing invalid expressions from being generated.

*This project most likely still needs more testing, so I won't bump it to version 1.0 until I'm sure it's good enough.*

## Installation

You can install this package using pip with the command

```bash
pip install regex_gen
```

## Usage

The main purpose of this package is generating regular expressions to be used in other projects, for example, with the built-in re module.

See the full documentation [here](docs/tutorial.md).

Import the module with:

```python
import regex_gen
```

Alternatively, import only the symbols that you need:

```python
from regex_gen import (...)
```

Now let's build an expression for matching a price tag:

```python
import re

from regex_gen import *

pattern = Regex(
    Group(name="price", expression=Regex(
        DIGIT[1:],
        Optional(DOT + DIGIT[:]))
        ),
    Group(name="currency", expression=
        AnyOf("$£€")
        ),
)
# (?P<price>\d+(?:\.\d*)?)(?P<currency>[$£€])

test_str = "Sales! Everything for 9.99£!"

price_tag = re.search(str(pattern), test_str)

if price_tag is not None:
    price = price_tag.group("price")
    currency = price_tag.group("currency")

    print(price, currency)
    # 9.99 £
```

Let's examine the pattern:

We have 2 groups:
* a group named "price" consisting of:
    * one or more digits
    * optionally:
        * a dot
        * zero or more digits
* a group named "currency" consisting of:
    * any character from "$£€"

Look how much clearer it is compared to the generated string:
`(?P<price>\d+(?:\.\d*)?)(?P<currency>[$£€])`

## Report a bug

If you find a bug, you can [open an issue](https://github.com/TitaniumBrain/regex_gen/issues) or [email me](mailto:titaniumbrain@vivaldi.net?subject=(regex_gen)%20Bug%20Report).


## License

This package is available under the [MIT license](https://choosealicense.com/licenses/mit/).
