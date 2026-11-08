# Test Design And Isolation

## Make The Behavior And Oracle Visible

Derive expected results from the requested behavior and established contract, not
merely from what the current implementation happens to do. A useful test makes the
behavior-changing action and observable assertion easy to identify; setup supplies
context and cleanup limits interference. This is not a requirement for exactly one
assertion, one fixture, or a fixed number of test layers
([pytest test anatomy](https://docs.pytest.org/en/stable/explanation/anatomy.html)).

Use ordinary assertions and the suite's existing helpers for expected exceptions or
approximate values where they express the contract. Returning a truthy value from a
test does not assert success: pytest ignores non-None return values and warns about
them ([pytest assertions](https://docs.pytest.org/en/stable/how-to/assert.html)).

When testing a dependency boundary, prefer enough fidelity to catch the interaction
that matters. A fake can make an uncommon failure deterministic; a mock can verify a
specific interaction but can also diverge from the real API. Google's testing guidance
describes these trade-offs in its own environment, not a universal ban on mocks or a
required unit/integration ratio
([test fidelity](https://testing.googleblog.com/2024/02/increase-test-fidelity-by-avoiding-mocks.html)).

## Assert Success And Rejection Contracts

For a successful operation, assert the promised value or externally visible effect;
calling the function without checking its result is not behavior evidence. For a
rejected operation, assert the documented exception (or result/error shape) and any
separate guarantee such as “no message was sent.” Keep only the action expected to
raise inside `pytest.raises`, so an unrelated setup or assertion failure cannot satisfy
the exception check:

```python
with pytest.raises(ValueError):
    parse_count("not-a-count")

assert sent_messages == []
```

The example assumes rejection promises not to send a message; omit that assertion if
the contract says nothing about sending. Check exception text only when it is itself a
supported contract, not to freeze incidental wording. These examples assume pytest;
use the existing runner's equivalent assertion conventions when a project uses another
framework. A passing assertion establishes only the stated outcome for that collected
case, not every input or side effect.

## Choose Fixture Scope By State Lifetime

Pytest's default function scope provides a fixture instance for each requesting test
function. Wider scopes deliberately reuse an instance: module- or session-scoped
mutable state can therefore retain changes across tests. Fixture dependencies also
affect execution: a failed setup prevents dependent tests from reaching their actions.
Reuse setup when it clarifies intent; do not add dependencies solely to make unrelated
tests share machinery ([pytest 9.2.0 fixture lifecycle](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst)).

The resource lifetime should explain the scope choice. An immutable expensive catalog
may be reasonable to share; a mutable transaction or per-case working directory often
needs a shorter lifetime. Shared external services may need explicit reset/transaction
boundaries even when a fixture itself is function-scoped. Scope alone is not isolation.

## Worked Failure: Setup Raises Before Yield

Suppose a fixture opens a file, performs additional initialization, and then yields it:

```python
@pytest.fixture
def prepared_log(tmp_path):
    stream = (tmp_path / "events.log").open("w", encoding="utf-8")
    initialize_log(stream)
    yield stream
    stream.close()
```

Assumptions: `pytest` is imported, and `initialize_log` is the project's setup helper.
If initialization raises, this fixture never reaches `yield`, so its after-yield
`close()` does not run. A successful test of ordinary writes would not expose that
failure. Pytest unwinds already-established fixtures, not unfinished after-yield code
([pytest 9.2.0 safe teardown](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst)).

Separate acquisition from the later failure-prone step:

```python
import pytest


@pytest.fixture
def log_stream(tmp_path):
    with (tmp_path / "events.log").open("w", encoding="utf-8") as stream:
        yield stream


@pytest.fixture
def prepared_log(log_stream):
    initialize_log(log_stream)
    return log_stream
```

Now `log_stream` is established before `prepared_log` initializes it. If initialization
fails, teardown of the established fixture exits the context manager and closes the
file. For several dependent resources, reason through reverse setup order and ensure
each successful acquisition has a cleanup path. Do not assume this pattern can undo
an external operation whose outcome is itself uncertain.

Validate the fixture's actual cleanup contract where relevant: induce initialization
failure through the suite's supported seam, observe closure/release, and check that a
subsequent case starts clean. Do not use unreliable timing or rely on test order to
make the failure appear.

## Parametrize Related Cases Without Sharing Mutation

Parametrization is useful when cases share a meaningful action/assertion shape, not
merely because several functions look similar. Pytest passes parameter objects as-is;
it does not copy a list or dictionary for each invocation
([pytest 9.2.0 parametrization](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/parametrize.rst)).

```python
shared_options = {"attempts": 0}


@pytest.mark.parametrize("options", [shared_options, shared_options])
def test_first_attempt(options):
    assert options["attempts"] == 0
    options["attempts"] += 1
```

The first case mutates the same object the second case receives. Prefer immutable
input descriptions and construct mutable state per invocation, or use separate fresh
objects when that accurately models the case. Do not copy blindly if object identity
or deliberate shared state is itself the behavior under test.

## Know What Isolation Helpers Do Not Control

`tmp_path` provides a path unique to each test function; it does not isolate a global
database, process, remote service, or clock. `monkeypatch` undoes its supported changes
after the requesting test/fixture, but patch the reference actually used by the code.
Changing one module's binding does not necessarily replace another module's already
imported binding ([temporary paths](https://docs.pytest.org/en/stable/how-to/tmp_path.html),
[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)).

When a test passes alone but fails with neighbors, inspect shared mutable fixture
state, unclosed resources, environment/cwd changes, background work, and assumptions
about execution order. A global-state-changing test may be unsafe in parallel even
when its assertions are deterministic in serial. Waiting a fixed arbitrary interval
can mask rather than fix uncontrolled asynchronous completion
([pytest flaky-test guidance](https://docs.pytest.org/en/stable/explanation/flaky.html)).

## Validate Collection Before Interpreting Results

Preserve the project's test layout, discovery naming, import mode, runner, and plugin
configuration. Pytest documents multiple layouts; `src/` and `importlib` recommendations
are not permission to migrate an existing suite
([integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)).

For the authorized changed targets, use the project's collection-only invocation first
when collection is in question; then run relevant tests using its established command.
Confirm that the intended cases and parametrized variants were collected. “No tests
collected,” deselected cases, or a skipped fixture-dependent path is not a behavioral
pass. Record targets and relevant environment/plugin context rather than reporting only
an exit status.

If a valid expectation exposes a production defect, retain the observed mismatch;
do not change production source or weaken the assertion to hide it. Report the contract,
reproduction, and blocked test work for the production owner.

## Read Coverage Changes Through The Measurement Scope

Coverage.py records execution, not whether the assertion checked the right behavior.
Selecting `source` can reveal eligible importable modules never executed; report-time
filters cannot add uncollected data. With `source` set, measurement `include` is ignored.
Line exclusions can remove whole blocks, and excluding a conditional destination can
remove a branch opportunity
([coverage.py 7.17.2 source](https://coverage.readthedocs.io/en/7.17.2/source.html),
[exclusions](https://coverage.readthedocs.io/en/7.17.2/excluding.html)).

For example, a report can fall after adding a source root because previously invisible,
unexecuted modules now enter the denominator. That is not by itself evidence that a
test stopped working. Conversely, a higher total after an exclusion is not necessarily
better testing. Compare source universe, test-file inclusion, report filters, exclusions,
line/branch mode, tool/plugin versions, and cross-process data collection before
attributing a percentage change to the test edits.

Use missing lines/branches as investigation leads: identify the unexercised behavior,
write an assertion for its contract when it is in scope, then collect a fresh run before
comparing. A report regenerated from old execution data cannot show what a newly added
test executed. Conversely, a covered line only shows execution; a test that enters one
side of an `if` does not establish the other side or an adequate oracle. Do not add an
exclusion or change the source denominator merely to improve a total in a test-only
task; preserve the project report contract and explain its measured scope.

Coverage.py recommends including tests; a production-only report serves a different
purpose, not the publisher's universal recommendation. A configured threshold is a
gate for that measurement, not an externally established quality target
([coverage.py 7.17.2](https://coverage.readthedocs.io/en/7.17.2/),
[configuration](https://coverage.readthedocs.io/en/7.17.2/config.html)). Keep existing
coverage settings; this test-only operation does not introduce a denominator or gate.

The coverage/effectiveness study in the source material examined five large Java
systems and 31,000 generated suites. Its size-controlled correlations varied and were
low-to-moderate; that supports caution, not a Python-specific effect estimate or a
reason to discard coverage as an execution diagnostic
([Inozemtseva and Holmes, ICSE 2014](https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf)).

## Further Context And Version Limits

Explicitly load `python-project-reference` before reading
`python-project-reference -> reference/testing-and-coverage.md` for deeper measurement
context or `python-project-reference -> reference/project-context-and-layout.md` for
test placement/import questions. Keep shared adoption policy in
`python-project-reference -> reference/project-baseline-and-adoption.md`.

The concrete fixture and parameter contracts above use pytest 9.2.0; coverage links
use 7.17.2. Earlier inspected coverage docs showed 7.17.1, whose decimal threshold
comparison fix matters when comparing old reports. Mutable stable/latest links do not
identify the target's versions. Use the project's resolved versions and established
commands, and report unavailable coverage as unavailable rather than implied success.
