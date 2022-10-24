import pytest
from regex_gen import (
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


def test_base():
    assert Regex("spam") == r"spam"


def test_zero_plus():
    assert ZeroOrMore("spam") == r"(?:spam)*"


def test_one_plus():
    assert OneOrMore("spam") == r"(?:spam)+"


def test_optional():
    assert Optional("spam") == r"(?:spam)?"


def test_repeat():
    assert Repeat("spam", count=42) == r"(?:spam){42}"


def test_repeat_range():
    assert Repeat("spam", count=(1, 42)) == r"(?:spam){1,42}"


def test_repeat_non_greedy():
    assert Repeat("spam", count=42, greedy=False) == r"(?:spam){42}"


def test_repeat_range_non_greedy():
    assert Repeat("spam", count=(1, 42), greedy=False) == r"(?:spam){1,42}?"


def test_set():
    assert AnyOf(r"spam") == r"[spam]"


def test_set_with_range():
    assert AnyOf((r"a", r"m")) == r"[a-m]"


def test_set_args():
    assert AnyOf(r"s", r"p", (r"a", r"m")) == r"[spa-m]"


def test_not_set():
    assert NoneOf(r"spam") == r"[^spam]"


def test_not_set_with_range():
    assert NoneOf((r"a", r"m")) == r"[^a-m]"


def test_not_set_args():
    assert NoneOf(r"s", r"p", (r"a", r"m")) == r"[^spa-m]"


def test_or():
    assert Or(r"spam", r"eggs") == r"spam|eggs"


def test_group():
    assert Group(r"spam") == r"(spam)"


def test_group_reference():
    assert Group(42) == r"\42"


def test_named_group():
    assert Group(r"spam", name="eggs") == r"(?P<eggs>spam)"


def test_named_group_reference():
    assert Group(name="eggs") == r"(?P=eggs)"


def test_non_capture_group():
    assert Group(r"spam", capture=False) == r"(?:spam)"


def test_non_capture_named_exception():
    with pytest.raises(ValueError):
        Group(r"spam", name="spam", capture=False)


def test_flag():
    assert Flags(Flag.IGNORE_CASE) == r"(?i)"


def test_flag_inline():
    assert Flags(Flag.IGNORE_CASE, r"spam") == r"(?i:spam)"


def test_comment():
    assert Comment("spam") == r"(?#spam)"


def test_positive_lookahead():
    assert Positive_LookAhead(r"spam") == r"(?=spam)"


def test_negative_lookahead():
    assert Negative_LookAhead(r"spam") == r"(?!spam)"


def test_positive_lookbehind():
    assert Positive_LookBehind(r"spam") == r"(?<=spam)"


def test_negative_lookbehind():
    assert Negative_LookBehind(r"spam") == r"(?<!spam)"


def test_conditional():
    assert If("spam", then=r"eggs", else_=r"bacon") == r"(?(spam)eggs|bacon)"

    assert If(42, then=r"eggs", else_=r"bacon") == r"(?(42)eggs|bacon)"


def test_flag_join():
    assert str(A + I) == r"ai"
    assert str(A | I) == r"ai"


def test_flag_disable():
    assert str(A - I) == r"a-i"
