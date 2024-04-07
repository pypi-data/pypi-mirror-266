# Pillory

A linter to scrutinize how you are using mocks in Python.

If you often hear or make the comment "patch the import not the definition" or
spend a lot of time explaining or helping people debug mocks, this linter could
help you.

## Usage

Install from PyPI with pip:

```
pip install pillory
```

Run pillory on the current directory:

```
python -m pillory
```

Or give a specific file, directory, or glob:

```
python -m pillory 'tests/**/test_*.py'
```

### Rules

*PM101 patched implementation*
: You patched the implementation of a class or function instead of where it is
imported to in the module under test. e.g. "parsers.Parser" where Parser is
defined instead of "__main__.Parser" where it is used. This means you may not
have affected the module under test at all, or you have replaced the target in a
way which will affect other code that uses it, which is bad for test isolation
(making sure tests don't affect other tests, and that each test tests what is
intended and don't change how other parts of the code work). There is a warning
about not affecting the right module in the [Python Standard Library
docs][stdlibdocs], but there is an [even better article by Ned
Batchelder][nedbat] explaining how it works and the additional problems with
test isolation.

*PM102 patched is not a top level module attribute*
: You patched something like a method on a class. Because class methods can't be
imported by themselves, this means all uses of the class will be affected, not
just the module under test.

*PM103 patched builtins*
: You patched the builtins module instead of the built-in function in the module
under test. Built-ins are actually added to every module and that's where they
should be patched, to avoid similar issues to patching the implementation. There
is a CPython detail that means the builtins module may be added to the lookup of
each module, so patching the builtins module _can_ work, but it's not guaranteed
and it still has problems with test isolation.

[stdlibdocs]: https://docs.python.org/3/library/unittest.mock.html#where-to-patch
[nedbat]: https://nedbatchelder.com/blog/201908/why_your_mock_doesnt_work.html

## Known issues

* No --help text.
* No console script entry point (pillory command), have to use with python -m.
* Only takes one path or glob.
* No config file support.
* Not fast.
* Must import modules. Doesn't work well with frameworks like Django that
  require special setup for things like settings before importing.
* Globs have to be relative to the current directory.
* No further explanations for the errors.
* No pretty error handling, just tracebacks.
* Will error when mocking something in the module under test, which is arguably
  "OK".
* No pre-commit integration.

## What's with the name?

I thought it was funny that mock can also mean "make fun of" as well as the
meaning of "mimic" that we use in testing. I imagined the linter cruelly calling
out how you are using mocks incorrectly. Except I couldn't call it "mock", or
"mock mocker", that would be confusing! So I picked a name with a similar
meaning, and starting with a P for that Python feeling.

## Contributing

Thank you for your interest in making a contribution.

Please talk to the maintainer before making a pull request to make sure what you
are adding is wanted.

This project uses the Apache License 2.0. You will be credited in the git
history, but for ease of maintenance copyright stays with the maintainer.
