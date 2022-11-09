"""
A simple, object oriented, regular expression generator.
"""

# read version from installed package
from importlib.metadata import version

__version__ = version("regex_gen")

# export names from inner module
from .regex_gen import (
    ASCII,
    DOTALL,
    IGNORECASE,
    LOCALE,
    MULTILINE,
    VERBOSE,
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
