"""
A simple, object oriented, regular expression generator.
"""

# read version from installed package
from importlib.metadata import version

__version__ = version("regex_gen")

# export names from inner module
from .regex_gen import (
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
    Negative_LookAhead,
    Negative_LookBehind,
    NoneOf,
    OneOrMore,
    Optional,
    Or,
    Positive_LookAhead,
    Positive_LookBehind,
    Regex,
    Repeat,
    S,
    X,
    ZeroOrMore,
)
