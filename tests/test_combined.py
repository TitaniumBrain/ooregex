from regex_gen import (
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

# ===============================================================================
# Test dunder method syntax
# ===============================================================================


def test_or():
    assert Regex("spam") | "eggs" == r"spam|eggs"


def test_ror():
    assert "spam" | Regex("eggs") == r"spam|eggs"


def test_radd():
    assert "spam" + Regex("eggs") == r"spameggs"


def test_pos_look_ahead():
    assert (Regex("spam") >= Regex("eggs")) == r"spam(?=eggs)"


def test_neg_look_ahead():
    assert (Regex("spam") > Regex("eggs")) == r"spam(?!eggs)"


def test_pos_look_behind():
    assert (Regex("spam") <= Regex("eggs")) == r"(?<=spam)eggs"


def test_neg_look_behind():
    assert (Regex("spam") < Regex("eggs")) == r"(?<!spam)eggs"


def test_repeat():
    assert Regex("spam")[42] == r"(?:spam){42}"


def test_zero_plus():
    assert Regex("spam")[:] == r"(?:spam)*"
    assert Regex("spam")[0:] == r"(?:spam)*"


def test_one_plus():
    assert Regex("spam")[1:] == r"(?:spam)+"


def test_optional():
    assert Regex("spam")[0:1] == r"(?:spam)?"


def test_range():
    assert Regex("spam")[27:42] == r"(?:spam){27,42}"


# Test complex expressions


def test_complex_1():
    assert (
        Group(Regex("spam") | "bacon", name="first")
        + Group("spam")[0:1]
        + If(1, then="eggs", else_=Group(name="first"))
    ) | (
        "bac" + AnyOf("o0") + "n"
    ) == r"(?P<first>spam|bacon)(spam)?(?(1)eggs|(?P=first))|bac[o0]n"
