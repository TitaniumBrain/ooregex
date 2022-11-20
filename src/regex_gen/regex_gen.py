from __future__ import annotations

import re
from typing import Iterable

# ===============================================================================
# Utils
# ===============================================================================


def _needs_grouping(expr: str | Regex) -> bool:
    # Go to https://regex101.com/r/lVZhG2/1
    # to inspect/test the pattern
    # Pattern matches some cases where wrapping in a group is redundant
    pattern = r"(?P<char>^\\?.$)|(?P<square>^\[(?:[^\n\[]|\\\[)*[^\\]\]$)|(?P<braces>^\((?:[^\n\(]|\\\()*[^\\]\)$)"

    match = re.match(pattern, str(expr))
    # if there's a match, no need to wrap in a group
    return match is None


def _sorted_by_string(iterable: Iterable[str], order_str: str) -> list[str]:
    """Returns a list with the elements of `iterable` sorted by their index in `order_str`."""
    return sorted(iterable, key=lambda c: order_str.find(c))


class Regex:
    """
    Base regex class.
    """

    def __init__(self, *expressions: str | Regex) -> None:
        exps = []
        for exp in expressions:
            # if is instance of Regex itself and not of a subclass
            if isinstance(exp, Regex) and not issubclass(type(exp), Regex):
                exps.extend(exp._expressions)
            else:
                exps.append(exp)

        self._expressions: tuple[str | Regex, ...] = tuple(exps)

    def __str__(self) -> str:
        return "".join(str(i) for i in self._expressions)

    def __repr__(self) -> str:
        return " + ".join(repr(i) for i in self._expressions)

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __or__(self, other: str | Regex) -> Regex:
        if isinstance(other, (str, Regex)):
            return Or(self, other)
        return NotImplemented

    def __ror__(self, other: str | Regex):
        if isinstance(other, (str, Regex)):
            return Or(other, self)
        return NotImplemented

    def __add__(self, other: str | Regex):
        return Regex(self, other)

    def __radd__(self, other: str | Regex):
        return Regex(other, self)

    def __ge__(self, other: Regex):
        if isinstance(other, Regex):
            return self + Positive_LookAhead(other)
        return NotImplemented

    def __gt__(self, other: Regex):
        if isinstance(other, Regex):
            return self + Negative_LookAhead(other)
        return NotImplemented

    def __le__(self, other: Regex):
        if isinstance(other, Regex):
            return Positive_LookBehind(self) + other
        return NotImplemented

    def __lt__(self, other: Regex):
        if isinstance(other, Regex):
            return Negative_LookBehind(self) + other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))

    def __getitem__(self, key: int | slice):
        match key:
            case int():
                if key >= 0:
                    return Repeat(self, key)
                raise ValueError(
                    "Expression must match a non-negative amount of times."
                )

            case slice(start=0 | None, stop=None, step=None):
                return ZeroOrMore(self)

            case slice(start=1, stop=None, step=None):
                return OneOrMore(self)

            case slice(start=0, stop=1, step=None):
                return Optional(self)

            case slice(start=int(start_), stop=int(stop_), step=None):
                return Repeat(self, (start_, stop_))

            case _:
                raise ValueError("Invalid key. Must be an int >= 0 or an int range.")


class AnyOf(Regex):
    _values: tuple[str | Regex]

    def __init__(self, *values: str | Regex | tuple[str | Regex, str | Regex]) -> None:
        vals: list[str | Regex] = []
        for v in values:
            match v:
                case str() | Regex():
                    vals.append(v)
                case [i, ii]:
                    vals.append(rf"{i}-{ii}")
                case _:
                    raise TypeError
        self._values = tuple(vals)

    def __str__(self) -> str:
        return f"[{''.join(map(str, self._values))}]"

    def __repr__(self) -> str:
        return f"AnyOf({', '.join(map(repr, self._values))})"


class NoneOf(Regex):
    _values: tuple[str | Regex]

    def __init__(self, *values: str | Regex | tuple[str | Regex, str | Regex]) -> None:
        vals: list[str | Regex] = []
        for v in values:
            match v:
                case str() | Regex():
                    vals.append(v)
                case [i, ii]:
                    vals.append(rf"{i}-{ii}")
                case _:
                    raise TypeError
        self._values = tuple(vals)

    def __str__(self) -> str:
        return f"[^{''.join(map(str, self._values))}]"

    def __repr__(self) -> str:
        return f"NoneOf({', '.join(map(repr, self._values))})"


class Comment(Regex):
    _comment: str | Regex

    def __init__(self, comment: str | Regex) -> None:
        self._comment = comment

    def __str__(self) -> str:
        return rf"(?#{self._comment})"

    def __repr__(self) -> str:
        return rf"Comment({self._comment!r})"


class Flags(Regex):
    _flags: Flag
    _expression: str | Regex | None

    def __init__(self, flags: Flag, expression: str | Regex | None = None) -> None:
        self._flags = flags
        self._expression = expression

    def __str__(self) -> str:
        if self._expression is None:
            return rf"(?{self._flags})"
        else:
            return rf"(?{self._flags}:{self._expression})"

    def __repr__(self) -> str:
        return rf"Flags({self._flags!r}, {self._expression!r})"


class Group(Regex):
    _expression: str | Regex | int | None = None
    _name: str | None
    _capture: bool

    def __init__(
        self,
        expression: str | Regex | int | None = None,
        *,
        name: str | None = None,
        capture: bool = True,
    ) -> None:

        # Check for invalid values or combinations of parameters
        match (expression, name, capture):
            # name + numbered group reference
            case [int(), str(), _]:
                raise ValueError(
                    "Cannot combine 'name' with a group reference by number."
                )
            case [str(), str() as name, _]:
                if not name.isidentifier():
                    raise ValueError("Group names must be valid python identifiers.")
                # non-capturing group is mutually exclusive with named group
                if capture is False:
                    raise ValueError(
                        "Cannot have a named, non-capturing group. 'name' can't be used with 'capture=False'."
                    )
            case [None, None, _]:
                raise ValueError(
                    f"Neither 'expression' nor 'name' were provided. At least one of them must not be None."
                )

        self._expression = expression
        self._name = name
        self._capture = capture

    def __str__(self) -> str:
        match (self._expression, self._name):
            # Numbered group reference
            case [int(), _]:
                return rf"\{self._expression}"

            # Named group reference
            case [None, str()]:
                return rf"(?P={self._name})"

            # Named group
            case [str() | Regex(), str()]:
                return rf"(?P<{self._name}>{self._expression})"

            # Unnamed group
            case [str() | Regex(), None]:
                return ("(?:" if not self._capture else "(") + rf"{self._expression})"

            # Should not be reached unless members are changed after instanciation
            case _:
                raise ValueError("Invalid combination of parameters.")

    def __repr__(self) -> str:
        return rf"Group({self._expression!r}, name={self._name!r}, capture={self._capture!r})"


class If(Regex):
    _group: int | str
    _then: str | Regex
    _else: str | Regex | None

    def __init__(
        self, group: int | str, then: str | Regex, else_: str | Regex | None
    ) -> None:
        self._group = group
        self._then = then
        self._else = else_

    def __str__(self) -> str:
        return rf"(?({self._group}){self._then}|{self._else if self._else is not None else ''})"

    def __repr__(self) -> str:
        return rf"If({self._group!r}, {self._then!r}, {self._else!r})"


class Negative_LookAhead(Regex):
    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?!{self._expression})"

    def __repr__(self) -> str:
        return rf"Negative_LookAhead({self._expression!r})"


class Negative_LookBehind(Regex):
    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?<!{self._expression})"

    def __repr__(self) -> str:
        return rf"Negative_LookBehind({self._expression!r})"


class Positive_LookAhead(Regex):
    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?={self._expression})"

    def __repr__(self) -> str:
        return rf"Positive_LookAhead({self._expression!r})"


class Positive_LookBehind(Regex):
    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?<={self._expression})"

    def __repr__(self) -> str:
        return rf"Positive_LookAhead({self._expression!r})"


class ZeroOrMore(Regex):
    _expression: str | Regex
    _greedy: bool

    def __init__(self, expression: str | Regex, greedy: bool = True) -> None:
        self._expression = expression
        self._greedy = greedy

    def __str__(self) -> str:
        if _needs_grouping(self._expression):
            ret_val = rf"(?:{self._expression})*"
        else:
            ret_val = rf"{self._expression}*"

        if not self._greedy:
            ret_val += "?"

        return ret_val

    def __repr__(self) -> str:
        return (
            rf"({self._expression!r})[1:]" + ".non_greedy" if not self._greedy else ""
        )

    @property
    def non_greedy(self):
        return ZeroOrMore(self._expression, False)

    min = non_greedy  # Alias


class OneOrMore(Regex):
    _expression: str | Regex
    _greedy: bool

    def __init__(self, expression: str | Regex, greedy: bool = True) -> None:
        self._expression = expression
        self._greedy = greedy

    def __str__(self) -> str:
        if _needs_grouping(self._expression):
            ret_val = rf"(?:{self._expression})+"
        else:
            ret_val = rf"{self._expression}+"

        if not self._greedy:
            ret_val += "?"

        return ret_val

    def __repr__(self) -> str:
        return (
            rf"({self._expression!r})[1:]" + ".non_greedy" if not self._greedy else ""
        )

    @property
    def non_greedy(self):
        return OneOrMore(self._expression, False)

    min = non_greedy  # Alias


class Optional(Regex):
    _expression: str | Regex
    _greedy: bool

    def __init__(self, expression: str | Regex, greedy: bool = True) -> None:
        self._expression = expression
        self._greedy = greedy

    def __str__(self) -> str:
        if _needs_grouping(self._expression):
            ret_val = rf"(?:{self._expression})?"
        else:
            ret_val = rf"{self._expression}?"

        if not self._greedy:
            ret_val += "?"

        return ret_val

    def __repr__(self) -> str:
        return (
            rf"({self._expression!r})[0:1]" + ".non_greedy" if not self._greedy else ""
        )

    @property
    def non_greedy(self):
        return Optional(self._expression, False)

    min = non_greedy  # Alias


class Repeat(Regex):
    _expression: str | Regex
    _count: int | tuple[int, int]
    _greedy: bool

    def __init__(
        self,
        expression: str | Regex,
        count: int | tuple[int, int],
        greedy: bool = True,
    ) -> None:
        self._expression = expression
        self._count = count
        self._greedy = greedy

    def __str__(self) -> str:
        if isinstance(self._count, int):

            count = f"{{{self._count}}}"
        else:
            count = f"{{{self._count[0]},{self._count[1]}}}"

        if _needs_grouping(self._expression):
            ret_val = rf"(?:{self._expression}){count}"
        else:
            ret_val = rf"{self._expression}{count}"

        if not self._greedy and not isinstance(self._count, int):
            ret_val += "?"

        return ret_val

    def __repr__(self) -> str:
        if isinstance(self._count, int):
            index = f"[{self._count}]"
        else:
            index = f"[{self._count[0]}:{self._count[1]}]"

        return (
            rf"({self._expression!r}){index}" + ".non_greedy"
            if not self._greedy
            else ""
        )

    @property
    def non_greedy(self):
        return Repeat(self._expression, self._count, False)

    min = non_greedy  # Alias


class Or(Regex):
    _expressions: tuple[str | Regex, ...] = tuple()

    def __init__(self, *expressions: str | Regex) -> None:
        self._expressions = (*self._expressions, *expressions)

    def __str__(self) -> str:
        return "|".join(map(str, self._expressions))

    def __repr__(self) -> str:
        return " | ".join(map(repr, self._expressions))


# ===============================================================================
# Flags
# ===============================================================================
class Flag:
    def __init__(self, flag: str = "", disable: str = "") -> None:
        enable_flags = set(flag)
        if any(f not in "aiLmsux" for f in enable_flags):
            raise ValueError("Can only enable flags in 'aiLmsux'.")

        disable_flags = set(disable)
        if any(f not in "imsx" for f in disable_flags):
            raise ValueError("Can only disable flags in 'imsx'.")

        self._enable_flags = enable_flags
        self._disable_flags = disable_flags

    def __str__(self) -> str:
        return f"{''.join(_sorted_by_string(self._enable_flags, 'aiLmsux'))}" + (
            f"-{''.join(_sorted_by_string(self._disable_flags, 'imsx'))}"
            if len(self._disable_flags) > 0
            else ""
        )

    def __repr__(self) -> str:
        return (
            f"Flag({repr(''.join(_sorted_by_string(self._enable_flags, 'aiLmsux')))}"
            + (
                f", {repr(''.join(_sorted_by_string(self._disable_flags, 'imsx')))}"
                if len(self._disable_flags)
                else ""
            )
            + ")"
        )

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __or__(self, other: Flag) -> Flag:
        if isinstance(other, Flag):
            return Flag(
                "".join(self._enable_flags | other._enable_flags),
                "".join(self._disable_flags),
            )
        return NotImplemented

    def __add__(self, other: Flag) -> Flag:
        return self.__or__(other)

    def __sub__(self, other: Flag) -> Flag:
        if isinstance(other, Flag):
            return Flag(
                "".join(self._enable_flags - other._enable_flags),
                "".join(self._disable_flags | other._enable_flags),
            )
        return NotImplemented


# ===============================================================================
# Constants
# ===============================================================================

# Escape sequences
DOT = Regex(r"\.")
START = Regex(r"^")
TRUE_START = Regex(r"\A")
END = Regex(r"$")
TRUE_END = Regex(r"\Z")
WORD_BOUNDARY = Regex(r"\b")
NOT_WORD_BOUNDARY = Regex(r"\B")
DIGIT = Regex(r"\d")
NOT_DIGIT = Regex(r"\D")
WHITESPACE = Regex(r"\s")
NOT_WHITESPACE = Regex(r"\S")
WORD = Regex(r"\w")
NOT_WORD = Regex(r"\W")
ANY = Regex(r".")

# Flags
A = ASCII = Flag("a")
I = IGNORECASE = Flag("i")
L = LOCALE = Flag("L")
M = MULTILINE = Flag("m")
S = DOTALL = Flag("s")
U = UNICODE = Flag("u")
X = VERBOSE = Flag("x")
