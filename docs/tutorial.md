# Tutorial

This file teaches you about all the available functionality of the package.

## Before you start

It is assumed that the user has a basic understanding of [regular expressions](https://docs.python.org/3/library/re.html).

When dealing with regular expressions, it is recommended to use raw strings for expressions involving `\`.
```python
# a raw string is a normal string prefixed with r
r"the \ doesn't need to be escaped here and escape sequences like \U don't have any special meaning."
```

Beware of [operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence). When in doubt, use parenthesis.

## Basics

### Regex
The base class is `Regex`, which all other classes inherit.

It takes one or more string or instances of `Regex` (or a subclass) and concatenates them.

To get the expression, just call `str()` on it:

```python
>>> str(Regex("spam", "eggs"))
'spameggs'
```

`Regex` instances are immutable and hashable, in case that may be useful to some user.

Instances are compared by comparing their `__str__`, so
```python
>>> Regex("spam") == "spam"
True
```

### Concatenation
You can add two instances together to concatenate their resulting expressions:

```python
>>> str(Regex("spam") + Regex("eggs"))
'spameggs'
```

This is equivalent to passing all expressions to the `Regex` constructor, which is the preferred way as it reduces bugs due to operator precedence.

### Or'ing

Or'ing (`|`) two (or more) expressions is used to define matching alternatives.

```python
>>> str(Regex("spam") | Regex("eggs"))
'spam|eggs'
```

This is the same as using [Or](#or).

If you want only part of the expression to have alternatives, wrap that part in a [Group](#group)

### Repetition

You can index an expression to define how many times it should be repeated.

```python
Regex("spam")[0:1] # zero or one times
Regex("spam")[0:] # zero or more times
Regex("spam")[:] # also zero or more times
Regex("spam")[1:] # one or more times
Regex("spam")[2:6] # from 2 to 6 times
Regex("spam")[3] # exacly 3 times
```

See [Optional](#optional), [ZeroOrMore](#zeroormore), [OneOrMore](#oneormore) amd [Repeat](#repeat) for more information.

## Constants

For convenience, there are a few symbols and escape sequences provided as constants, so you don't have to remember them.

These are:
```python
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
```

## Comment

Leave a comment inside a regular expression. Comments are ignored when parsing, but help make the expression more readable (🤔 but that's why you're using this package, isn't it?)

```python
>>> str(Regex("eggs", Comment("spam")))
'eggs(?#spam)'
```

## Character sets
Character sets define a set of characters that can m«be matched.

Special characters lose their special meaning inside a set.

Escape sequences are still allowed.

A tuple `(a, b)` denotes a range of characters from a to b.

### AnyOf
Match any of the characters in the set.

```python
>>> str(AnyOf("abc", "d", ("0", "9")))
'[abcd0-9]'
```

### NoneOf
Match any of the characters **not** in the set.

```python
>>> str(NoneOf("abc", "d", ("0", "9")))
'[^abcd0-9]'
```

## Inline Flags
Instead of passing flags to the functions in the `re` module, you ca include these functions as part of the xpression itself.

### Flags
Include one or more [`Flag`](#flag) in a pattern.

If you pass an expression to `Flags`, apply the passed in flags to only that expression.
```python
>>> str(Regex("eggs", Flags(I, "spam"), "spam"))
'eggs(?i:spam)spam'
```

If you don't pass an expression, the flags apply to the whole final expression and you must use this at the beginning of your pattern.

```python
>>> str(Regex(Flags(I), "spameggs"))
'(?i)spameggs'
```

### Flag
A `Flag` instance represents the enabled flags and disabled flags to be included as inline flags when passed to [`Flags`](#flags).

There's no need to create an instance yourself, as all possible flags are available already:

```python
A = ASCII = Flag("a")
I = IGNORECASE = Flag("i")
L = LOCALE = Flag("L")
M = MULTILINE = Flag("m")
S = DOTALL = Flag("s")
U = UNICODE = Flag("u")
X = VERBOSE = Flag("x")
```

Flags can be combined with `+` or `|`.
```python
>>> str(A + I)
'ai'
```

Flags can be disabled with `-`.
```python
>>> str(- I)
'-i'
>>> str(A - X)
'a-x'
```

Combine these as needed:
```python
>>> str((A + I) - (S + X) - M)
'ai-msx'
```

## Group

You can wrap an expression in a `Group`, treating it as one unit.

```python
>>> str(Group(Regex("spam")))
'(spam)'
```

Groups can optionally be named. The name must be a valid python identifier.
```python
>>> str(Group(Regex("spam"), name="eggs"))
'(?P<eggs>spam)'
```

You can make a backreference to a group, by name or by number, by omitting the expression.

```python
>>> str(Group(1))
'\\1'
>>> str(Group("eggs"))
'(?P=eggs)'
```

You can also make a non-capturing group, which can't be backreferenced nor affects the group numbering.

```python
>>> str(Group(Regex("spam", capture=False)))
'(?:spam)'
```

## If

Match one pattern if a certain group exists.
Optionally, match another pattern if the group doesn't exist.

```python
>>> str(Regex(Group("eggs"), If(1, then="spam")))
'(eggs)(?(1)spam)'
>>> str(Regex(Group("eggs", name="bacon"), If("bacon", then="spam", else_="eggs")))
'(?P<bacon>eggs)(?(bacon)spam|eggs)'
```

## Or

Join multiple expressions as alternatives.

Equivalent to using `|`.

```python
>>> str(Or("spam", "eggs", "bacon"))
'spam|eggs|bacon'
```

Unless you want an alternative for the whole expression, you may need to wrap the `Or` in a group.

For example,
```python
>>> str(Regex("spam") + Or("spam", "eggs"))
'spamspam|eggs'
>>> str(Regex("spam") + (Regex("spam") | Regex("eggs")))
'spamspam|eggs'
```
will match either 'spamspam' or 'eggs', not 'spamspam' or 'spameggs' as one might expect.

To get the desired result, you could do
```python
>>> str(Regex("spam") + Group(Or("spam", "eggs"), capture=False))
'spam(?:spam|eggs)'
```

## Quantifiers

You can index/slice (`[]`) an expression to indicate how many times it should match.

You can make a quantifier non-greedy (match as little times as possible) by using the `.non_greedy` (alias `.min`) property.

```python
>>> str(DIGIT[1:].non_greedy)
'\d+'
>>> str(Regex("spam")[1:].non_greedy)
'(?:spam)+'
```

Except for some obvious cases, the expression is wrapped in a non-capturing group, although it may sometimes be redundant.

### Optional

Match zero or one times.
Returned by indexing with `[0:1]`.

```python
>>> str(Regex("spam")[0:1])
'(?:spam)?'
>>> str(Optional("spam", greedy=False))
'(?:spam)??'
```

### ZeroOrMore

Match zero or more times.
Returned by indexing with `[0:]` and `[:]`.

```python
>>> str(Regex("spam")[0:])
'(?:spam)*'
>>> str(ZeroOrMore("spam", greedy=False))
'(?:spam)*?'
```

### OneOrMore

Match one or more times.
Returned by indexing with `[1:]`.

```python
>>> str(Regex("spam")[1:])
'(?:spam)+'
>>> str(OneOrMore("spam", greedy=False))
'(?:spam)+?'
```

### Repeat

Match `n` times or between `a` and `b` times.
Returned by indexing with `[n]` or `[a:b]`.

```python
>>> str(Regex("spam")[42])
'(?:spam){42}'
>>> str(Repeat("spam", 42))
'(?:spam){42}'
>>> str(Repeat("spam", (2, 6)).min)
'(?:spam){2,6}'
>>> str(Repeat("spam", (2, None)).min)
'(?:spam){2,}'
```

## Assertions

Assertions let you match expressions behind or ahead of the current position in the string, without consuming the string.

They can be done by using comparison operators.

`<` and `<=` do a *lookbehind*; `>` and `>=` do a *lookahead*.

`<` and `>` do a negative assertion; `<=` and `>=` do a positive assertion

### PositiveLookAhead

Match if the expression matches after the current position, without consuming any of the string.

Returned by the `>=` operator.

```python
>>> str(Regex("spam") >= Regex("eggs"))
'spam(?=eggs)'
>>> str(Regex("spam", PositiveLookAhead("eggs")))
'spam(?=eggs)'
```

### NegativeLookAhead

Match if the expression doesn't match after the current position, without consuming any of the string.

Returned by the `>` operator.

```python
>>> str(Regex("spam") > Regex("eggs"))
'spam(?!eggs)'
>>> str(Regex("spam", NegativeLookAhead("eggs")))
'spam(?!eggs)'
```

### PositiveLookBehind

Match if the expression precedes the current position.

Returned by the `<=` operator.

```python
>>> str(Regex("spam") <= Regex("eggs"))
'(?<=spam)eggs'
>>> str(Regex(PositiveLookBehind("spam"), Regex("eggs")))
'(?<=spam)eggs'
```

### NegativeLookBehind

Match if the expression doesn't precede the current position.

Returned by the `<` operator.

```python
>>> str(Regex("spam") < Regex("eggs"))
'(?<!spam)eggs'
>>> str(Regex(NegativeLookBehind("spam"), Regex("eggs")))
'(?<!spam)eggs'
```
