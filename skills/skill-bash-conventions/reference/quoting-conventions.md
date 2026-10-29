# Quoting Conventions

Follow Google Shell Style Guide quoting rules to prevent unintended word splitting and pathname expansion.

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
files=("${dirname}"/*.sh)
# An unmatched glob is literal in Bash; keep an empty list in that case.
[[ -e "${files[0]}" || -L "${files[0]}" ]] || files=()

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
