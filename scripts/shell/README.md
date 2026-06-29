# Shell Scripts

Shell helpers are invoked through `Makefile` targets from the workspace root.

## Layout

- `src/`: executable shell entry points.
- `lib/`: shared shell functions sourced by scripts in `src/`.

## Dependencies

Install required tools via apt (primary, Linux Mint/Debian/Ubuntu):

```bash
# Core tools
sudo apt install shellcheck shfmt bats

# Bats helper libraries (system-installed assertion libraries)
sudo apt install bats-assert bats-support bats-file

# Coverage (no apt package available — gem is the approved fallback)
sudo gem install bashcov
```

Fallback (cross-platform) via npm if apt is unavailable:

```bash
npm install -g @bats-core/bats @bats-core/assert @bats-core/support @bats-core/file
```

## Verify Dependencies

```bash
make -C scripts/shell deps-check
```

This checks that all required tools and libraries are installed and reports any missing items.

## Examples

```bash
make -C scripts/shell help
make -C scripts/shell example
```

The example target runs `src/example.sh`, which sources `lib/example.sh`.