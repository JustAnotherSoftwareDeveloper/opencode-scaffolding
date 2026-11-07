# Secure Configuration And Data Handling

## Identify The Value And Its Output Boundary

Decide whether a value is sensitive before deciding how to serialize or log it. A
configuration library can parse, validate, or mask a value; those conveniences do not
make it a vault, access-control system, or guarantee that every output path is safe.
Possible exposure paths include logs, tracebacks, error pages, representations,
serializers, fixtures, diagnostics, and build artifacts. OWASP identifies passwords,
tokens, connection strings, keys, and sensitive personal data as values that generally
should not be logged directly; actual classification and handling remain contextual.
(Dossier C16-C17, C29; [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).)

Python's `secrets` module generates security-purpose random values; it does not store
or deliver them. Use it rather than `random` for security-sensitive tokens, but do not
invent a universal token size from the API documentation. (C16; [Python 3.15.2
`secrets`](https://docs.python.org/3.15/library/secrets.html).)

## Trace Configuration Precedence

When two configuration sources disagree, inspect the library's effective source order
and any project customization instead of assuming that a checked-in file wins. In the
default pydantic-settings v2.16.2 source order, constructor values precede environment,
dotenv, and file-secret sources; defaults are added afterward. The current documentation
also says environment values outrank dotenv values. CLI sources may be added and source
hooks can be customized, so this is not a universal Python rule or a target-project
claim. (C28; [pydantic-settings v2.16.2 source hook](https://github.com/pydantic/pydantic-settings/blob/v2.16.2/docs/index.md) and [tagged source implementation](https://github.com/pydantic/pydantic-settings/blob/v2.16.2/pydantic_settings/main.py).)

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
handling also masks it. (C29; [Pydantic v2.14.1 secret types](https://github.com/pydantic/pydantic/blob/v2.14.1/pydantic/types.py) and [serialization](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/concepts/serialization.md).)

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

Keep the deployed configuration source and effective precedence until their exposure
paths are understood. Environment variables, mounted files, and runtime secret-manager
delivery have different risks; no channel is universally safest. For a scoped output
change, a non-production sentinel can test whether the sentinel appears in the specific
captured log, error, serialization, or artifact path. That evidence covers only the
path tested.

Data classification, legal/privacy obligations, approved stores, IAM, host visibility,
retention, key management, rotation cadence, and breach response require local owners.
This module does not establish compliance or whole-system security. Pydantic examples
are version-qualified and no target settings model or deployment has been inspected.

## Related Domains

- Handler, formatter, and record mechanics belong to [Logging and Observability](logging-and-observability.md).
- Build and artifact inspection belong to [Distribution Artifacts](distribution-artifacts.md).
- General exception and retry behavior belongs to [Source and API](source-and-api.md).
