"""
A simple, object oriented, regular expression generator.

ooregex is a package aimed at providing a simple syntax for composing
regular expressions, without having to memorise their syntax.

Classes
-------
AnyOf

Comment

Flag

Flags

Group

If

Negative_LookAhead

Negative_LookBehind

NoneOf

OneOrMore

Optional

Or

Positive_LookAhead

Positive_LookBehind

Regex

Repeat

ZeroOrMore

Constants
---------
ANY

DIGIT

DOT

END

NOT_DIGIT

NOT_WHITESPACE

NOT_WORD

NOT_WORD_BOUNDARY

START

TRUE_END

TRUE_START

WHITESPACE

WORD

WORD_BOUNDARY

Flags
-----
A, ASCII

I, IGNORECASE

L, LOCALE

M, MULTILINE

S, DOTALL

U, UNICODE

X, VERBOSE

Examples
--------
Refer to the docs for a comprehensive explanation of the package's
functionality with examples.
"""

# read version from installed package
from importlib.metadata import version

__version__ = version("ooregex")

# export names from inner module
from .ooregex import (
    ANY,
    ASCII,
    DIGIT,
    DOT,
    DOTALL,
    END,
    IGNORECASE,
    LOCALE,
    MULTILINE,
    NOT_DIGIT,
    NOT_WHITESPACE,
    NOT_WORD,
    NOT_WORD_BOUNDARY,
    START,
    TRUE_END,
    TRUE_START,
    UNICODE,
    VERBOSE,
    WHITESPACE,
    WORD,
    WORD_BOUNDARY,
    A,
    AnyOf,
    Comment,
    Flag,
    Flags,
    Group,
    I,
    If,
    L,
    M,
    NegativeLookAhead,
    NegativeLookBehind,
    NoneOf,
    OneOrMore,
    Optional,
    Or,
    PositiveLookAhead,
    PositiveLookBehind,
    Regex,
    Repeat,
    S,
    U,
    X,
    ZeroOrMore,
)

__all__ = [
    "ANY",
    "ASCII",
    "DIGIT",
    "DOT",
    "DOTALL",
    "END",
    "IGNORECASE",
    "LOCALE",
    "MULTILINE",
    "NOT_DIGIT",
    "NOT_WHITESPACE",
    "NOT_WORD",
    "NOT_WORD_BOUNDARY",
    "START",
    "TRUE_END",
    "TRUE_START",
    "UNICODE",
    "VERBOSE",
    "WHITESPACE",
    "WORD",
    "WORD_BOUNDARY",
    "A",
    "AnyOf",
    "Comment",
    "Flag",
    "Flags",
    "Group",
    "I",
    "If",
    "L",
    "M",
    "NegativeLookAhead",
    "NegativeLookBehind",
    "NoneOf",
    "OneOrMore",
    "Optional",
    "Or",
    "PositiveLookAhead",
    "PositiveLookBehind",
    "Regex",
    "Repeat",
    "S",
    "U",
    "X",
    "ZeroOrMore",
]
