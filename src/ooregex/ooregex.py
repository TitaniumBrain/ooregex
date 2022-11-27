"""
The core of the package.

Attributes
----------
All exported symbols relevant to the user are available in the main
`ooregex` namespace, i.e. do
>>> from ooregex import ...

instead of
>>> from ooregex.ooregex import ...

Examples
--------
Refer to the docs for a comprehensive explanation of the package's
functionality with examples.
"""
from __future__ import annotations

import re
from typing import Iterable

# ===============================================================================
# Utils
# ===============================================================================


def _needs_grouping(expr: str | Regex) -> bool:
    """Returns True if an expression may need to be surrounded in a group.

    Tests for a few cases where wrapping `expr` in a group is redundant.

    Parameters
    ----------
    expr : str | Regex
        The expression to be tested.

    Returns
    -------
    bool
        False in a few cases where grouping is redundant, True otherwise.

    Notes
    -----
    Go to https://regex101.com/r/lVZhG2/1 to inspect/test the pattern.

    Pattern matches some cases where wrapping in a group is redundant.
    """
    pattern = r"(?P<char>^\\?.$)|(?P<square>^\[(?:[^\n\[]|\\\[)*[^\\]\]$)|(?P<braces>^\((?:[^\n\(]|\\\()*[^\\]\)$)"

    match = re.match(pattern, str(expr))
    # if there's a match, no need to wrap in a group
    return match is None


def _sorted_by_string(iterable: Iterable[str], order_str: str) -> list[str]:
    """Returns a list sorted by the index of substrings in another string.

    Returns a list with the elements of `iterable` sorted by the first
    index at which they appear in `order_str`.

    Parameters
    ----------
    iterable : Iterable[str]
        An iterable of strings to be sorted.
    order_str : str
        A string that defines the desired order of strings.

    Returns
    -------
    list[str]
        A list of strings sorted as per `order_str`.
    """
    return sorted(iterable, key=lambda c: order_str.find(c))


# ===============================================================================
# Classes
# ===============================================================================


class Regex:
    """Base Regex class, represents a regular expression.

    Calling `str` on an instance of this class or its subclasses returns a
    string representing a regular expression.

    A Regex instance is compared to another object by comparing their
    string representations, meaning that an instance can be directly
    compared to a string, for example.

    Instances are immutable and hashable.
    Two instances have the same hash value if they have the same string
    representation.

    Instances of this class or a subclass are also returned by operations
    on other instances.
    The supported operators are `+`, `|`, `>=`, `>`, `<=`, `<` and `[]`.

    Operations
    ----------

    Adding (`+`) two instances is equivalent to concatenating their regexes.
    >>> str(Regex("spam") + Regex("eggs"))
    'spameggs'

    Or'ing (`|`) two instances is used to define matching alternatives.
    >>> str(Regex("spam") | Regex("eggs"))
    'spam|eggs'

    The `>=` operator adds the second instance as a `Positive_LookAhead`.
    >>> str(Regex("spam") >= Regex("eggs"))
    'spam(?=eggs)'
    >>> str(Regex("spam") + Positive_LookAhead("eggs"))
    'spam(?=eggs)'

    The `>` operator adds the second instance as a `Negative_LookAhead`.
    >>> str(Regex("spam") > Regex("eggs"))
    'spam(?!eggs)'
    >>> str(Regex("spam") + Negative_LookAhead("eggs"))
    'spam(?!eggs)'

    The `<=` operator adds the first instance as a `Positive_LookBehind`.
    >>> str(Regex("spam") <= Regex("eggs"))
    '(?<=spam)eggs'
    >>> str(Positive_LookBehind("spam") + Regex("eggs"))
    '(?<=spam)eggs'

    The `<` operator adds the first instance as a `Negative_LookBehind`.
    >>> str(Regex("spam") < Regex("eggs"))
    '(?<!spam)eggs'
    >>> str(Negative_LookBehind("spam") + Regex("eggs"))
    '(?<!spam)eggs'

    Indexing an instance returns an appropriate quantifier subclass
    depending on the indices.
    >>> str(Regex("z")[:])
    'z*'
    >>> str(Regex("z")[1:])
    'z+'
    >>> str(Regex("z")[0:1])
    'z?'
    >>> str(Regex("z")[27:42])
    'z{27,42}'
    >>> str(Regex("z")[42:])
    'z{42,}'

    Examples
    --------
    Refer to the docs for a comprehensive explanation of the package's
    functionality with examples.
    """

    def __init__(self, *expressions: str | Regex) -> None:
        """
        Parameters
        ----------
        *expressions : tuple[str | Regex, ...]
            Regular expressions to be concatenated. At least one required.

        Raises
        ------
        ValueError
            No expression is passed, i.e. *expressions is empty.
        """
        if len(expressions) == 0:
            raise ValueError("No expressions passed in. Pass at least one expression.")
        exps = []
        for exp in expressions:
            # if is instance of Regex itself and not of a subclass
            if type(exp) is Regex:
                exps.extend(exp._expressions)
            else:
                exps.append(exp)

        self._expressions: tuple[str | Regex, ...] = tuple(exps)

    def __str__(self) -> str:
        return "".join(str(i) for i in self._expressions)

    def __repr__(self) -> str:
        return " + ".join(
            (f"Regex({repr(i)})" if isinstance(i, str) else repr(i))
            for i in self._expressions
        )

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __or__(self, other: Regex) -> Regex:
        if isinstance(other, Regex):
            return Or(self, other)
        return NotImplemented

    def __add__(self, other: Regex):
        if isinstance(other, Regex):
            return Regex(self, other)
        return NotImplemented

    def __ge__(self, other: Regex):
        if isinstance(other, Regex):
            return self + PositiveLookAhead(other)
        return NotImplemented

    def __gt__(self, other: Regex):
        if isinstance(other, Regex):
            return self + NegativeLookAhead(other)
        return NotImplemented

    def __le__(self, other: Regex):
        if isinstance(other, Regex):
            return PositiveLookBehind(self) + other
        return NotImplemented

    def __lt__(self, other: Regex):
        if isinstance(other, Regex):
            return NegativeLookBehind(self) + other
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

            case slice(
                start=int() | None as start_, stop=int() | None as stop_, step=None
            ):
                return Repeat(self, (start_, stop_))

            case _:
                raise ValueError("Invalid key. Must be an int >= 0 or an int range.")


class AnyOf(Regex):
    """Represents a character set.

    Expression will match any character in the set.
    Can be passed strings, which get included in the character set literally;
    Can be passed 2-tuples, which get included as a character range.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(AnyOf("a", "bc", ("w", "z")))
    '[abcw-z]'
    """

    _values: tuple[str | tuple[str, str], ...]

    def __init__(self, *values: str | tuple[str, str]) -> None:
        """
        Parameters
        ----------
        *values : tuple[str | tuple[str, str]]
            Characters to include in a set.
            A 2-tuple represents a character range.

        Raises
        ------
        TypeError
            One or more values of the wrong type.
        """
        vals: list[str | tuple[str, str]] = []
        for v in values:
            match v:
                case str():  # a character
                    vals.append(v)
                case [str(), str()]:  # a character range
                    vals.append(v)
                case _:
                    raise TypeError
        self._values = tuple(vals)

    def __str__(self) -> str:
        return f"[{''.join((str(i) if isinstance(i, str) else f'{i[0]}-{i[1]}') for i in self._values)}]"

    def __repr__(self) -> str:
        return f"AnyOf({', '.join(map(repr, self._values))})"


class NoneOf(Regex):
    """Represents a complemented character set.

    Expression will match any character not in the set.
    Can be passed strings, which get included in the character set literally;
    Can be passed 2-tuples, which get included as a character range.

    See Also
    --------
    AnyOf : similar but not complemented.
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(NoneOf("a", "bc", ("w", "z")))
    '[^abcw-z]'
    """

    _values: tuple[str | tuple[str, str], ...]

    def __init__(self, *values: str | tuple[str, str]) -> None:
        """
        Parameters
        ----------
        *values : tuple[str | tuple[str, str]]
            Characters to include in a set.
            A 2-tuple represents a character range.

        Raises
        ------
        TypeError
            One or more values of the wrong type.
        """
        vals: list[str | tuple[str, str]] = []
        for v in values:
            match v:
                case str():  # a character
                    vals.append(v)
                case [str(), str()]:  # a character range
                    vals.append(v)
                case _:
                    raise TypeError
        self._values = tuple(vals)

    def __str__(self) -> str:
        return f"[^{''.join((str(i) if isinstance(i, str) else f'{i[0]}-{i[1]}') for i in self._values)}]"

    def __repr__(self) -> str:
        return f"NoneOf({', '.join(map(repr, self._values))})"


class Comment(Regex):
    """A comment in a regular expression.

    Anything inside a comment is ignored when matching the expression.

    Warnings
    --------
    Most operations don't make sense with comments and may have unexpected
    results. Use common sense.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Comment("spam"))
    '(?#spam)'
    """

    _comment: str | Regex

    def __init__(self, comment: str | Regex) -> None:
        """
        Parameters
        ----------
        comment : str | Regex
            The value to be commented.
        """
        self._comment = comment

    def __str__(self) -> str:
        return rf"(?#{self._comment})"

    def __repr__(self) -> str:
        return rf"Comment({self._comment!r})"


class Flags(Regex):
    """Adds inline flags to an expression.

    Include flags as part of an expression.

    If not passed an expression, it applies to the whole final expression
    and should only be used at the beginning of it.
    If passed an expression, the flags only apply to that subexpression.

    See Also
    --------
    Regex : Base class, see other methods.
    Flag : regex flags.

    Examples
    --------
    >>> str(Flags(I, "spam"))
    '(?i:spam)'
    """

    _flags: Flag
    _expression: str | Regex | None

    def __init__(self, flags: Flag, expression: str | Regex | None = None) -> None:
        """
        Parameters
        ----------
        flags : Flag
            A Flag instance representing the flags to be included.
        expression : str | Regex | None, optional
            Expression to have flags applied to, by default None.
            If None, must be used at the beginning of the final expression.
        """
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
    """Represents a group within an expression.

    Groups an expression in a (non)capturing group if one is passed in.
    If no expression is passed in, it instead represents a reference to a
    previous group, specified by name or number.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Group(Regex("spam"), name=eggs))
    '(?P<eggs>spam)'
    >>> str(Group(name=eggs))
    '(?P=eggs)'
    """

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
        """
        Parameters
        ----------
        expression : str | Regex | int | None, optional
            Expression to wrap in a group, by default None.
            If None, represents a group reference.
            If an int, represents a group reference by number.
        name : str | None, optional
            If provided, the group's name, by default None.
            Must be a valid python identifier.
        capture : bool, optional
            Whether this is a capturing group, by default True.
            If True, cannot pass in a `name`.

        Raises
        ------
        ValueError
            Invalid combination of arguments.
        """

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
    """Match an expression if a group exists.

    Matches an expression if a group with a specified name or number
    exists, with an optional alternative expression if it doesn't.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(If(1, then="spam", else_="eggs"))
    '(?(1)spam|eggs)'
    >>> str(If(1, then="spam"))
    '(?(1)spam)'
    """

    _group: int | str
    _then: str | Regex
    _else: str | Regex | None

    def __init__(
        self, group: int | str, then: str | Regex, else_: str | Regex | None = None
    ) -> None:
        """
        Parameters
        ----------
        group : int | str
            Group to test for. Can be a name or a number.
        then : str | Regex
            Expression to match if group exists.
        else_ : str | Regex | None, optional
            Expression to match if group doesn't exist.
        """
        self._group = group
        self._then = then
        self._else = else_

    def __str__(self) -> str:
        return (
            rf"(?({self._group}){self._then}"
            + (f"|{self._else}" if self._else is not None else "")
            + ")"
        )

    def __repr__(self) -> str:
        return rf"If({self._group!r}, {self._then!r}, {self._else!r})"


class NegativeLookAhead(Regex):
    """Match if the expression doesn't match next.

    Match if the expression doesn't match after the current position,
    without consuming any of the string.
    Returned by the `>` operator.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam") > Regex("eggs"))
    'spam(?!eggs)'
    """

    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression that shouldn't match.
        """
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?!{self._expression})"

    def __repr__(self) -> str:
        return rf"Negative_LookAhead({self._expression!r})"


class NegativeLookBehind(Regex):
    """Match if the expression doesn't precede the current position.

    Match if the expression doesn't precede the current position.
    Returned by the `<` operator.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam") < Regex("eggs"))
    '(?<!spam)eggs'
    """

    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression that shouldn't precede.
            Must be a fixed length expression.
        """
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?<!{self._expression})"

    def __repr__(self) -> str:
        return rf"Negative_LookBehind({self._expression!r})"


class PositiveLookAhead(Regex):
    """Match if the expression matches next.

    Match if the expression matches after the current position,
    without consuming any of the string.
    Returned by the `>=` operator.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam") >= Regex("eggs"))
    'spam(?=eggs)'
    """

    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression that shouldn match next.
        """
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?={self._expression})"

    def __repr__(self) -> str:
        return rf"Positive_LookAhead({self._expression!r})"


class PositiveLookBehind(Regex):
    """Match if the expression precedes the current position.

    Match if the expression precedes the current position.
    Returned by the `<=` operator.

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam") <= Regex("eggs"))
    '(?<=spam)eggs'
    """

    _expression: str | Regex

    def __init__(self, expression: str | Regex) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression that shouldn precede.
            Must be a fixed length expression.
        """
        self._expression = expression

    def __str__(self) -> str:
        return rf"(?<={self._expression})"

    def __repr__(self) -> str:
        return rf"Positive_LookAhead({self._expression!r})"


class ZeroOrMore(Regex):
    """Match an expression zero or more times.

    Matches an expression zero or more times.
    Returned by indexing an instance of `Regex` with `[:]` or `[0:]`.

    Attributes
    ----------
    min, non_greedy

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam")[:])
    '(?:spam)*'
    >>> str(Regex("spam")[:].min)
    '(?:spam)*?'
    """

    _expression: str | Regex
    _greedy: bool

    def __init__(self, expression: str | Regex, greedy: bool = True) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression to match.
        greedy : bool, optional
            Whether to match as many times possible, by default True.
            If False, matches as little times as possible.
        """
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
        """Return a non greedy instance.

        Returns a non greedy instance with the same expression, which
        matches as little times as possible.

        Returns
        -------
        ZeroOrMore
            A non greedy instance.

        See Also
        --------
        min : Alias.
        """
        return ZeroOrMore(self._expression, False)

    min = non_greedy  # Alias


class OneOrMore(Regex):
    """Match an expression one or more times.

    Matches an expression one or more times.
    Returned by indexing an instance of `Regex` with `[1:]`.

    Attributes
    ----------
    min, non_greedy

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam")[1:])
    '(?:spam)+'
    >>> str(Regex("spam")[1:].min)
    '(?:spam)+?'
    """

    _expression: str | Regex
    _greedy: bool

    def __init__(self, expression: str | Regex, greedy: bool = True) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression to match.
        greedy : bool, optional
            Whether to match as many times possible, by default True.
            If False, matches as little times as possible.
        """
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
        """Return a non greedy instance.

        Returns a non greedy instance with the same expression, which
        matches as little times as possible.

        Returns
        -------
        OneOrMore
            A non greedy instance.

        See Also
        --------
        min : Alias.
        """
        return OneOrMore(self._expression, False)

    min = non_greedy  # Alias


class Optional(Regex):
    """Match an expression zero or one times.

    Matches an expression zero or one times.
    Returned by indexing an instance of `Regex` with `[0:1]`.

    Attributes
    ----------
    min, non_greedy

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam")[0:1])
    '(?:spam)?'
    >>> str(Regex("spam")[0:1].min)
    '(?:spam)??'
    """

    _expression: str | Regex
    _greedy: bool

    def __init__(self, expression: str | Regex, greedy: bool = True) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression to match.
        greedy : bool, optional
            Whether to match as many times possible, by default True.
            If False, matches as little times as possible.
        """
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
        """Return a non greedy instance.

        Returns a non greedy instance with the same expression, which
        matches as little times as possible.

        Returns
        -------
        Optional
            A non greedy instance.

        See Also
        --------
        min : Alias.
        """
        return Optional(self._expression, False)

    min = non_greedy  # Alias


class Repeat(Regex):
    """Match an expression a specified amount of times.

    Matches an expression either n times or
    between a and b times.
    Returned by indexing an instance of `Regex` with `[n]` or `[a:b]`.

    Attributes
    ----------
    min, non_greedy

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam")[27:42])
    '(?:spam){27,42}'
    >>> str(Regex("spam")[42])
    '(?:spam){42}'
    """

    _expression: str | Regex
    _count: int | tuple[int | None, int | None]
    _greedy: bool

    def __init__(
        self,
        expression: str | Regex,
        count: int | tuple[int | None, int | None],
        greedy: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        expression : str | Regex
            Expression to match.
        count : int | tuple[int, int]
            Amount of times to match.
            Can be an exact amount or a tuple of the lower and upper bounds.
        greedy : bool, optional
            Whether to match as many times possible, by default True.
            If False, matches as little times as possible.
        """
        self._expression = expression
        self._count = count
        self._greedy = greedy

    def __str__(self) -> str:
        if isinstance(self._count, int):

            count = f"{{{self._count}}}"
        else:
            count = (
                "{"
                + (f"{self._count[0]}" if self._count[0] else "")
                + ","
                + (f"{self._count[1]}" if self._count[1] else "")
                + "}"
            )

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
        """Return a non greedy instance.

        Returns a non greedy instance with the same expression, which
        matches as little times as possible.

        Returns
        -------
        Repeat
            A non greedy instance.

        See Also
        --------
        min : Alias.
        """
        return Repeat(self._expression, self._count, False)

    min = non_greedy  # Alias


class Or(Regex):
    """Match either expression.

    Matches any of the expressions passed in.
    Returned by the `|` operator.

    Warnings
    --------
    Unless you want an alternative for the whole expression, you may need
    to wrap the `Or` in a group.

    For example,
    >>> str(Regex("spam") + Or("spam", "eggs"))
    'spamspam|eggs'
    >>> str(Regex("spam") + (Regex("spam") | Regex("eggs")))
    'spamspam|eggs'

    will match either 'spamspam' or 'eggs', not 'spamspam' or 'spameggs'
    as one might expect.

    To get the desired result, you could do
    >>> str(Regex("spam") + Group(Or("spam", "eggs"), capture=False))
    'spam(?:spam|eggs)'

    See Also
    --------
    Regex : Base class, see other methods.

    Examples
    --------
    >>> str(Regex("spam") | Regex("eggs")))
    'spam|eggs'
    """

    _expressions: tuple[str | Regex, ...] = tuple()

    def __init__(self, *expressions: str | Regex) -> None:
        """
        Parameters
        ----------
        *expressions : tuple[str | Regex, ...]
            Regular expression alternatives.
        """
        exps = []
        for exp in expressions:
            if isinstance(exp, Or):
                exps.extend(exp._expressions)
            else:
                exps.append(exp)

        self._expressions = tuple(exps)

    def __str__(self) -> str:
        return "|".join(map(str, self._expressions))

    def __repr__(self) -> str:
        return "(" + " | ".join(map(repr, self._expressions)) + ")"


# ===============================================================================
# Flags
# ===============================================================================
class Flag:
    """A class to handle regex flag operations.

    An instance of this class represents one of or a combination of the
    flags that can be used in a regular expression.
    Instances of this class should not be created directly, but instead
    you should use the provided instances.

    Operations
    ----------
    Flags can be combined with `+` or `|` (equivalent).
    >>> str(A + I)
    'ai'

    Flags can be disabled with the `-` operator.
    >>> str(A - X)
    'a-x'

    Combine these as needed:
    >>> str((A + I) - (S + X) - M)
    'ai-msx'

    See Also
    --------
    Flags : Add inline flags to a regex.

    Examples
    --------
    Refer to the docs for a comprehensive explanation of the package's
    functionality with examples.
    """

    def __init__(self, flag: str = "", disable: str = "") -> None:
        """
        Parameters
        ----------
        flag : str, optional
            A string of all the flags to enable, by default "".
            Possible values are any combination of substrings of "aiLmsux".
        disable : str, optional
            A string of all the flasg to disable, by default "".
            Possible values are any combination of substrings of "imsx".

        Raises
        ------
        ValueError
            Invalid value in `flag`.
        ValueError
            Invalid value in `disable`.
        """
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

    def __neg__(self):
        return Flag(
            "".join(set()),
            "".join(self._enable_flags),
        )


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
