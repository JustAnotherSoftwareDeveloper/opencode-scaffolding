# Secure Configuration And Data Handling

## Identify The Value And Its Output Boundary

Decide whether a value is sensitive before deciding how to serialize or log it. A
configuration library can parse, validate, or mask a value; those conveniences do not
make it a vault, access-control system, or guarantee that every output path is safe.
Possible exposure paths include logs, tracebacks, error pages, representations,
serializers, fixtures, diagnostics, and build artifacts. OWASP identifies passwords,
tokens, connection strings, keys, and sensitive personal data as values that generally
should not be logged directly; actual classification and handling remain contextual.
([OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).)

Python's `secrets` module generates security-purpose random values; it does not store
or deliver them. Use it rather than `random` for security-sensitive tokens, but do not
invent a universal token size from the API documentation. ([Python 3.15.2
`secrets`](https://docs.python.org/3.15/library/secrets.html).)

## Trace Configuration Precedence

When two configuration sources disagree, inspect the library's effective source order
and any project customization instead of assuming that a checked-in file wins. In the
default pydantic-settings v2.16.2 source order, constructor values precede environment,
dotenv, and file-secret sources; defaults are added afterward. The current documentation
also says environment values outrank dotenv values. CLI sources may be added and source
hooks can be customized, so this is not a universal Python rule or a target-project
claim. ([pydantic-settings v2.16.2 source hook](https://github.com/pydantic/pydantic-settings/blob/v2.16.2/docs/index.md) and [tagged source implementation](https://github.com/pydantic/pydantic-settings/blob/v2.16.2/pydantic_settings/main.py).)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeSettings(BaseSettings):
    api_token: str

    model_config = SettingsConfigDict(secrets_dir="/run/secrets")
```

Assumption: the application has selected pydantic-settings and mounted a secret file
for this setting. The `secrets_dir` option identifies a source; it does not establish
that this channel is safest, that a mounted file exists, or that production uses this
configuration. Verify the installed release and custom source order before applying
the example.

## Treat Masking As Local To One Serializer

Pydantic v2.14.1 documents `SecretStr` masking in its `repr()`/`str()` and default JSON
output, while `get_secret_value()` and a custom field serializer can reveal plaintext.
Python-mode `model_dump()` may still contain a secret object whose representation is
masked. Do not infer that later logging, export, custom serialization, or exception
handling also masks it. ([Pydantic v2.14.1 secret types](https://github.com/pydantic/pydantic/blob/v2.14.1/pydantic/types.py) and [serialization](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/concepts/serialization.md).)

The following illustrates the distinction, not a safe-output guarantee for a whole
settings model:

```python
from pydantic import SecretStr

token = SecretStr("test-sentinel")
masked_display = repr(token)
clear_value = token.get_secret_value()
```

Expected from the documented Pydantic 2.14.1 type: the nonempty value is masked in
`masked_display`, while `clear_value` is the original string. The values are not
printed, and this example was not executed. The Pydantic and pydantic-settings versions
above are separately scoped evidence, not a tested compatibility pair.

## Compare Secret Delivery At The Runtime Boundary

An environment variable keeps a value out of a checked-in source file, but it is not
automatically private from the process or its operational environment. OWASP's
container-injection guidance warns that environment values may be accessible to
processes and may appear in logs or system dumps. A mounted secret file instead makes
filesystem ownership, mode, mount scope, backup/diagnostic handling, and rotation or
replacement behavior part of the boundary. Runtime retrieval can narrow delivery to an
identity with least-privilege access, but introduces dependencies on identity
provisioning, network/service availability, authorization, caching, and refresh. These
are threat-model comparisons, not a universal ranking: environment configuration is
also a supported framework mechanism (Django documents environment and file inputs),
and the actual host/container controls determine exposure.
([OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html#51-injection-of-secrets-into-containers), [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).)

When access is compromised, distinguish **rotation** (issuing/replacing a credential)
from **revocation/expiry** (making the exposed credential unusable). Rotation alone
does not invalidate a stolen old value; the issuing system must revoke or expire it.
Prefer short-lived/dynamic credentials only when the issuer, consumer identity, renewal
path, and outage behavior are understood. Do not place production credentials in image
build arguments, layers, source archives, wheels, or other build artifacts. The secret
manager guidance supports these lifecycle dimensions, not a fixed rotation interval or
vendor choice. ([OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).)

## Keep Logging Configuration And Untrusted Data Within Their Trust Boundaries

Python's `logging.config` is not merely passive data parsing: configuration mechanisms
that import or invoke user-defined objects can execute code, and the socket listener
documentation describes configuration portions passed through `eval()`. Accept such
configuration only from a trusted source or protect the listener with its documented
verification boundary; this warning is about configuration paths, not ordinary calls
to `logger.info()`.
([Python 3.15.2 logging configuration security considerations](https://docs.python.org/3.15/library/logging.config.html#security-considerations).)

Treat values from another trust zone as untrusted even when they are destined only for
diagnostics. Validate shape and bound length; then encode for the actual sink (for
example, JSON string encoding for JSON output, or the appropriate escaping for a
line-oriented format). If a field fails validation, omit it or replace it with safe,
bounded context while preserving the useful security event. Do not concatenate raw
newlines/delimiters into a log line or attach the whole rejected payload to an error.
([OWASP Logging Cheat Sheet — event collection](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#event-collection).)

Test the real output boundary, not just a masking type or helper: feed a non-production
sentinel secret and an untrusted value containing a newline/delimiter through the
configured formatter/handler, capture emitted output, and assert the secret and forged
second record are absent while the intended event and safe fields remain. Repeat for
error/traceback, serialization, diagnostic, and artifact routes that the change affects;
each test establishes only that specific path. Keep which fields are sensitive and
which destinations are approved as local policy decisions.

For example, when the selected output is the JSON formatter from [Logging and
Observability](logging-and-observability.md), an output-boundary test can assert both
that only selected fields are serialized and that a hostile newline stays inside one
JSON string:

```python
import json
import logging


def test_json_log_keeps_untrusted_id_in_one_record_and_omits_secret():
    record = logging.LogRecord("example", logging.INFO, "", 0, "request.finished", (), None)
    record.request_id = 'r-1\nINFO forged'
    record.api_token = "test-secret-sentinel"

    rendered = JsonFormatter().format(record)
    parsed = json.loads(rendered)

    assert parsed["request_id"] == 'r-1\nINFO forged'
    assert rendered.count("\n") == 0
    assert "test-secret-sentinel" not in rendered
```

Assumption: `JsonFormatter` selects only `level`, `logger`, `message`, and `request_id`
as shown in the linked reference. This checks formatter output, not downstream collector
transforms, traceback content, or whether the ID itself is an approved field; add those
paths to tests only when they are part of the changed contract.

For required production settings, prefer a clear failure that names the missing key
without echoing its value:

```python
import os

api_token = os.environ.get("API_TOKEN")
if not api_token:
    raise RuntimeError("required API_TOKEN is missing")
```

This illustrative boundary treats both absent and empty values as missing; that choice
must match the project's configuration contract. The observable failure names the
missing setting but never interpolates its value. Do not silently fall back to a known
or empty production credential. A safe message here does not prove that every other
output route is safe.

## Brownfield And Policy Limits

Keep the deployed configuration source and effective precedence until its exposure,
availability, permissions, identity, and recovery paths are understood. The examples
above identify questions to compare; they do not determine the target platform's
security or availability trade-off. A non-production sentinel test provides evidence
only for the captured paths exercised.

Data classification, legal/privacy obligations, approved stores, IAM, host visibility,
retention, key management, rotation cadence, and breach response require local owners.
This module does not establish compliance or whole-system security. Pydantic examples
are version-qualified and no target settings model or deployment has been inspected.

## Related Domains

- Handler, formatter, and record mechanics belong to [Logging and Observability](logging-and-observability.md).
- Build and artifact inspection belong to [Distribution Artifacts](distribution-artifacts.md).
- General exception and retry behavior belongs to [Source and API](source-and-api.md).
