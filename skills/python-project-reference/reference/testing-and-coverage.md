# Testing And Coverage

## Make The Behavior And State Boundary Visible

A test gives behavior evidence through what its assertion checks. Coverage reports
execution within a configured source universe. Neither a passing suite nor a high
percentage proves that assertions cover every requirement or would detect every defect.
Keep the behavior question separate from the coverage measurement. (
[pytest 9.2.0 fixtures](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst) and [coverage.py 7.17.2 branch coverage](https://coverage.readthedocs.io/en/7.17.2/branch.html).)

### Check A Result And A Rejection Contract

Pytest's [test anatomy](https://docs.pytest.org/en/stable/explanation/anatomy.html)
separates Arrange, Act, Assert, and Cleanup. The action and observed expectation are
the core behavioral evidence; merely invoking a function or returning a Boolean
from a test does not assert its result. Pytest ignores non-`None` test returns and
warns about them. These assertion/anatomy pages were recorded in November 2026 as
mutable stable documentation, not as new evidence about an installed runner.

Assume `my_package.counts.parse_count` converts integer strings (including surrounding
whitespace) to non-negative counts and raises `ValueError` for invalid input. A
related set of positive and rejection cases can share an intelligible assertion:

```python
import pytest

from my_package.counts import parse_count


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("12", 12), (" 7 ", 7)])
def test_parse_count_returns_count(raw, expected):
    result = parse_count(raw)

    assert result == expected


@pytest.mark.parametrize("raw", ["-1", "bad", ""])
def test_parse_count_rejects_invalid_input(raw):
    with pytest.raises(ValueError):
        parse_count(raw)
```

The first test checks a value, not just absence of an exception. The second fails
if the call returns normally or raises the wrong exception type; it does not prove
that rejection left external state unchanged. Keep only the intended failing action
inside `raises`, and assert any required no-write/no-send behavior separately. Use
`match=` when message text is part of the contract, not to freeze incidental wording.
([Pytest assertions and expected exceptions](https://docs.pytest.org/en/stable/how-to/assert.html)
and [pytest 9.2.0 parametrization](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/parametrize.rst).)

### Pair State Changes With Cleanup

Pytest 9.2.0 runs a yield fixture's cleanup after the yield and unwinds fixtures in
reverse setup order. If setup in a fixture raises before it reaches its `yield`, that
fixture's after-yield cleanup is not reached. Keep the acquired resource's cleanup
paired with that fixture, and put later failure-prone setup in a dependent fixture:

```python
import pytest


@pytest.fixture
def session():
    value = open_session()
    try:
        yield value
    finally:
        value.close()


@pytest.fixture
def ready_session(session):
    session.wait_until_ready()
    return session
```

Assumption: `open_session()` returns a resource with `close()` and
`wait_until_ready()`. If readiness setup raises, the already-established `session`
fixture still has its teardown. If acquisition itself fails before returning a value,
there is no acquired `value` to close. These function names are illustrative, not a
real service fixture. Function scope is the default; a broader scope deliberately
reuses the fixture object and its state across tests, rather than creating greater
isolation. ([pytest 9.2.0 safe teardown](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst).)

Parameter values are passed as-is, not copied. This case can contaminate later cases:

```python
import pytest


shared_items = []


@pytest.mark.parametrize("items", [shared_items, shared_items])
def test_append_item(items):
    assert items == []
    items.append("x")
```

Both parameter entries refer to the same list object. The first case appends `"x"`;
the second then fails its initial empty-list assertion. Prefer immutable test inputs
when possible, or provide a fresh mutable value for each case. `tmp_path` and
`monkeypatch` control bounded state; they do not isolate arbitrary processes or
external services. `tmp_path` gives each test function its own temporary directory;
`monkeypatch` restores only the attributes/mappings/environment/path changes it made
after the requesting test or fixture. Neither removes a database row created by an
unpatched client. ([pytest 9.2.0 parametrization](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/parametrize.rst),
[temporary paths](https://docs.pytest.org/en/stable/how-to/tmp_path.html), and
[monkeypatch](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/monkeypatch.rst).)

## Read A Coverage Change Through Its Denominator

A source root can make eligible, importable modules that no test executed appear in a
coverage.py report. Branch mode measures possible destinations in addition to
statements; exclusions can remove statement or branch opportunities. A percentage can
therefore change without a source edit when config discovery, source paths, exclusions,
or branch mode changes.

For the hypothetical `my_package`, keep the run's source and branch choices in one
configuration:

```toml
[tool.coverage.run]
source = ["my_package"]
branch = true
```

Then collect and inspect the same run, using coverage.py 7.17.2's command interface:

```sh
coverage run -m pytest
coverage report -m
coverage html
```

`run` collects execution data while pytest executes; `report -m` displays missing
locations; HTML makes line/partial-branch annotations inspectable. Investigate a
missing behavior, add a test that asserts it, then rerun collection and reporting.
Regenerating only the report cannot measure a newly added test. These are commands
for an illustrative installed package/test environment, not a run performed here.
([Execution](https://coverage.readthedocs.io/en/7.17.2/commands/cmd_run.html)
and [reporting](https://coverage.readthedocs.io/en/7.17.2/commands/cmd_reporting.html).)

For coverage.py 7.17.2, placing `source` in config applies it to both collection and
later reporting. Supplying `--source` only to `coverage run` does not carry that option
into a later report. The tool reads the first applicable config file rather than
combining every common config file. An eligible module that was never executed may
appear as uncovered; an excluded branch may no longer count as an opportunity. These
are expected measurement effects, not observed project output. ([coverage.py 7.17.2 configuration](https://coverage.readthedocs.io/en/7.17.2/config.html), [source selection](https://coverage.readthedocs.io/en/7.17.2/source.html), and [exclusions](https://coverage.readthedocs.io/en/7.17.2/excluding.html).)

### A Covered Line Can Still Have A Missing Branch

Consider this separate illustrative function:

```python
def choose_label(enabled):
    label = "off"
    if enabled:
        label = "on"
    return label
```

Calling only `choose_label(True)` executes every statement, yet never takes the
false destination from the `if` directly to `return`. Branch measurement can mark
that conditional as partial even when statement coverage has no missing lines.
A test asserting `choose_label(False) == "off"` exercises and checks the other
behavior. Neither reaching both destinations nor line coverage proves that all
input classes or meaningful assertions were covered. In branch mode, the total
includes statement and branch-destination opportunities. ([coverage.py 7.17.2
branch model](https://coverage.readthedocs.io/en/7.17.2/branch.html).)

### Measurement Filters And Report Exclusions Are Different

`[run] source/include/omit` control measurement; configured `source` also enables
eligible unexecuted-file discovery, and overrides `[run] include` rather than
combining with it. `[report] include/omit` and report command subsets narrow what
is presented. Hiding a file at report time does not erase its collected data, while
later widening the report cannot recover executed-line data that was never measured.

Line/block exclusions are another reporting choice, not a reason for tests to stop
executing that code. A `# pragma: no cover` on a block-introducing line can exclude
the whole block; excluding one conditional destination can remove that branch
opportunity. Prefer narrowly justified patterns over broad names that accidentally
hide unrelated code. `exclude_also` adds patterns while preserving built-ins;
`exclude_lines` replaces the built-in list. For example, a project with a deliberately
unreachable abstract adapter might add its own pattern:

```toml
[tool.coverage.report]
exclude_also = ["raise NotImplementedError"]
```

That is a conditional project choice, not advice to exclude every untested failure.
The earlier `if TYPE_CHECKING:` pattern is already a built-in exclusion in the
recorded coverage.py 7.17.2 context (introduced in 7.10.0); adding it is redundant
there, not a prerequisite for typed code. ([Exclusion semantics](https://coverage.readthedocs.io/en/7.17.2/excluding.html)
and [additive versus replacement options](https://coverage.readthedocs.io/en/7.17.2/config.html).)

The report's purpose determines whether test files belong in its denominator. Coverage.py
recommends including tests because it does not distinguish tests from code under test
([coverage.py 7.17.2 quick start](https://coverage.readthedocs.io/en/7.17.2/)); a
production-only report answers another question. Neither choice is a universal quality
result. A threshold such as `fail_under` is a configured report target, not evidence
that its percentage is suitable. Keep source set, test inclusion, exclusions, mode,
and threshold visible when comparing reports.

## Brownfield Reading

Keep the project's test runner, fixture scopes, plugins, collection, coverage source
set, exclusions, branch mode, thresholds, and CI conventions unless a requested change
justifies altering them. If coverage falls with no source change, compare the effective
config and report scope before diagnosing lost test behavior. A different denominator
or mode is not a like-for-like trend. The cited pytest details are pinned to 9.2.0 and
coverage.py to 7.17.2; verify the target versions and config when those details matter.

## Related Domains

- Test file placement and imports belong to [Project Context and Layout](project-context-and-layout.md).
- Ruff/Pyright results belong to [Static Quality](static-quality.md).
- General failure and retry contracts belong to [Source and API](source-and-api.md).
