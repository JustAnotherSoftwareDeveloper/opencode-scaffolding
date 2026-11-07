# Testing And Coverage

## Make The Behavior And State Boundary Visible

A test gives behavior evidence through what its assertion checks. Coverage reports
execution within a configured source universe. Neither a passing suite nor a high
percentage proves that assertions cover every requirement or would detect every defect.
Keep the behavior question separate from the coverage measurement. (Dossier C08-C12;
[pytest 9.2.0 fixtures](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst) and [coverage.py 7.17.2 branch coverage](https://coverage.readthedocs.io/en/7.17.2/branch.html).)

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
real service fixture. (C08; [pytest 9.2.0 safe teardown](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst).)

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
external services. (C09; [pytest 9.2.0 parametrization](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/parametrize.rst).)

## Read A Coverage Change Through Its Denominator

A source root can make eligible, importable modules that no test executed appear in a
coverage.py report. Branch mode measures possible destinations in addition to
statements; exclusions can remove statement or branch opportunities. A percentage can
therefore change without a source edit when config discovery, source paths, exclusions,
or branch mode changes.

```toml
[tool.coverage.run]
source = ["my_package"]
branch = true

[tool.coverage.report]
exclude_also = ["if TYPE_CHECKING:"]
```

For coverage.py 7.17.2, placing `source` in config applies it to both collection and
later reporting. Supplying `--source` only to `coverage run` does not carry that option
into a later report. The tool reads the first applicable config file rather than
combining every common config file. An eligible module that was never executed may
appear as uncovered; an excluded branch may no longer count as an opportunity. These
are expected measurement effects, not observed project output. (C10-C11, C25; [coverage.py 7.17.2 configuration](https://coverage.readthedocs.io/en/7.17.2/config.html), [source selection](https://coverage.readthedocs.io/en/7.17.2/source.html), and [exclusions](https://coverage.readthedocs.io/en/7.17.2/excluding.html).)

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
