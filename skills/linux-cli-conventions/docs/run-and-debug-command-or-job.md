# Run And Debug A Command Or Job

Use this page when a command or unit fails to start or behaves differently than expected, a pipeline or terminal job has an unclear result, or process/log evidence is being used to investigate a failure. A unit-start investigation belongs here even if its process never launched. Examples are static and source-scoped; this is not a build, application-debugging, or service-repair playbook.

## Which Program Receives A Command Name

Bash can expand an alias or invoke a function before command search selects a builtin or a `PATH` executable. A name containing a slash follows a different search path. Bash POSIX mode does not make Bash identical to every POSIX shell. See Bash 5.3 [Command Search and Execution](https://www.gnu.org/software/bash/manual/html_node/Command-Search-and-Execution.html) and [POSIX Mode](https://www.gnu.org/software/bash/manual/html_node/Bash-POSIX-Mode.html).

POSIX `pwd` distinguishes logical and physical paths. GNU Coreutils 9.12 documents a physical default unless `POSIXLY_CORRECT` changes it; Bash also provides a `pwd` builtin. The command name alone does not identify which implementation or options apply. See [POSIX `pwd`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/pwd.html) and [GNU `pwd`](https://www.gnu.org/software/coreutils/manual/html_node/pwd-invocation.html).

## Why A Value Becomes More Than One Argument

Bash expands words before passing arguments to a command. Unquoted parameter or command substitutions can undergo word splitting and pathname expansion. In the static Bash fragment `"$value"`, the expansion remains one argument; double quotes still allow parameter and command substitution. Quoting controls these word-boundary effects, not every later interpretation. See Bash 5.3 [Quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html) and [Shell Expansions](https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html).

## What A Pipeline Status Or Redirection Represents

In Bash, `first | second` connects the first command's standard output to the second command's standard input. The pipeline status is normally the status of `second`; `set -o pipefail` lets a nonzero status from an earlier command affect the result. This is Bash behavior, not a rule for every shell. See Bash 5.3 [Pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html).

Bash processes redirections from left to right before the command runs. The static fragment `>report.txt` creates a missing destination or truncates an existing regular file when Bash `noclobber` is off; `>|` overrides that option. The shell expands the destination, so the fragment alone does not identify a host path. POSIX `cat` copies input bytes; shell redirection can change the destination before `cat` starts. See Bash [Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html), POSIX [`cat`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/cat.html), and [Extract, reshape, or package information](extract-reshape-package-information.md) for stream operations.

## Why Environment Or Locale Changed A Result

POSIX.1-2024 defines locale categories for collation, character handling, messages, numbers, and time. `LC_ALL` takes precedence over individual locale variables. Whether locale affects a utility depends on locale initialization and that utility's rules. See [POSIX Environment Variables](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/basedefs/V1_chap08.html).

POSIX `sort` uses locale collation, so `LC_COLLATE` can affect its ordering. The static prefix `LC_ALL=C sort` illustrates a per-command environment assignment, not a universal output guarantee. See [POSIX `sort`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/sort.html); for data extraction tasks, see [Extract, reshape, or package information](extract-reshape-package-information.md#separate-matching-from-extracting-fields).

## Why A Terminal Or Foreground Job Behaved Differently

POSIX.1-2024 describes a terminal foreground process group and makes input behavior conditional on terminal modes. With `ISIG` enabled, the configured `INTR` character sends `SIGINT` to that group; the configured `SUSP` character similarly sends `SIGTSTP`. Key mappings are configurable, so a familiar key is not universal. Canonical mode collects input by lines; non-canonical mode does not.

Bash 5.3 describes job control as cooperation between the terminal driver and shell. Bash groups pipelines into jobs; when job control is available, `fg` and `bg` resume jobs in the foreground or background. A background read from the controlling terminal can trigger `SIGTTIN`. The shell, terminal settings, and process-group context determine the interpretation. See POSIX [General Terminal Interface](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/basedefs/V1_chap11.html) §§11.1.2–11.1.9 and Bash [Job Control Basics](https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html).

## What Process And Command-Context Evidence Shows

The procps-ng `ps(1)` manual defines output as a snapshot shaped by selection and formatting rules. The static fragment `ps -eo pid,stat,comm` requests selected fields; it does not promise a complete or lasting process record. The inspected rendering did not expose an exact release. See [`ps(1)`](https://man7.org/linux/man-pages/man1/ps.1.html).

A `kill` name can resolve to a shell builtin or utility. Linux signal dispositions can be default, ignored, or caught, so a signal request does not predict the target's response. See util-linux [`kill(1)`](https://man7.org/linux/man-pages/man1/kill.1.html) and Linux [`signal(7)`](https://man7.org/linux/man-pages/man7/signal.7.html).

Bash 5.3 history can retain command text after history expansion but before parameter and variable expansion; `HISTCONTROL` and `HISTIGNORE` can filter entries. Linux procfs documents `/proc/<pid>/cmdline` and `/proc/<pid>/environ`. Visibility depends on process behavior, access checks, and procfs configuration. These are possible exposure surfaces, not universal visibility rules or a universally safe way to supply secrets. See Bash [History Facilities](https://www.gnu.org/software/bash/manual/bash.html#Bash-History-Facilities), [`proc_pid_cmdline(5)`](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html), and [`proc_pid_environ(5)`](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html).

For a failed unit start, use [Prepare the environment a job needs](prepare-environment-for-a-job.md#check-package-and-unit-states) as supporting context for unit-file, enablement, and runtime-state distinctions. For journal filter semantics, see [Extract, reshape, or package information](extract-reshape-package-information.md#filter-log-records). These references expose state and filtering distinctions, not the cause of a failed start or a general diagnosis or repair sequence. For prerequisite readiness before a run, use [Prepare the environment a job needs](prepare-environment-for-a-job.md).
