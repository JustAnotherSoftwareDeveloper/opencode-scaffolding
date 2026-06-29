# Quoting Conventions

Follow Google Shell Style Guide quoting rules.

- Always quote variables: `"$var"`, `"${array[@]}"`.
- Always quote command substitutions: `"$(command)"`.
- Always use `"$@"` — never `$*` or unquoted `$@`.
- Use arrays for list data: `files=("$dir"/*.sh); for f in "${files[@]}"; do ...`.
- Prefer `$(command)` over backticks.

Examples:

```bash
# Good
local dirname="${1:?directory is required}"
printf '%s\n' "Processing: ${dirname}"
mapfile -t files < <(ls -1 "${dirname}"/*.sh 2>/dev/null) || true

# Bad
dirname=$1
echo Processing: $dirname
files=`ls $dirname/*.sh`

# Good — array usage
args=("$@")
for arg in "${args[@]}"; do
  printf '%s\n' "${arg}"
done
```