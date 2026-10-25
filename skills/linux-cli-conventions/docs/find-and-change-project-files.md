# Find And Change Project Files

Use this page when the job is to locate project paths, collect files, or reason about what a common file operation does to names. The references describe utility behavior; they do not provide an editor, version-control, or configuration-format workflow.

## Find The Relevant Path

POSIX `ls` normally omits names beginning with `.`. GNU Coreutils 9.12 varies listing presentation by terminal and locale, so a human-oriented listing is not a stable inventory format. See [POSIX `ls`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/ls.html) and [GNU `ls`](https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html).

The inspected GNU `find(1)` manual says its default `-P` does not follow symbolic links; `-L` follows them. Newlines are valid in pathnames, so newline-delimited text can merge or split names. GNU `find -print0` paired with GNU `xargs -0` preserves argument boundaries; it does not make traversal a snapshot or eliminate races with a changing tree. The rendered manuals do not identify exact releases. See GNU [`find(1)`](https://man7.org/linux/man-pages/man1/find.1.html) and [`xargs(1)`](https://man7.org/linux/man-pages/man1/xargs.1.html).

Static GNU pattern (not a live-host procedure):

```sh
find sample-tree -type f -print0 | xargs -0 -r stat
```

Here `stat` refers to GNU Coreutils 9.12; the pattern illustrates delimiter handling, not a fixed command path. When a task is specifically about how a shell turns values into arguments, see [Run and debug a command or job](run-and-debug-command-or-job.md#why-a-value-becomes-more-than-one-argument).

## Change A Path Or Its Directory Entry

- POSIX `mkdir -p` creates missing parent directories and treats an existing directory operand as success. The process creation mask affects permissions. See [POSIX `mkdir`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/mkdir.html).
- POSIX `ln` creates hard links by default; `ln -s` creates a symbolic link that stores a path. A hard link adds another name for the same file, while path resolution follows a symbolic link to its target. See [POSIX `ln`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/ln.html).
- Recursive `cp` symlink handling depends on its options; GNU Coreutils 9.12 documents its implementation's behavior. See [POSIX `cp`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/cp.html) and [GNU `cp`](https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html).
- A cross-filesystem GNU `mv` can copy and then remove the source instead of performing one rename. See [POSIX `mv`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/mv.html) and [GNU `mv`](https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html).
- `rm` removes directory entries; GNU Coreutils warns that ordinary removal is not secure erasure and that `--one-file-system` does not protect same-filesystem data. See [POSIX `rm`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/rm.html) and [GNU `rm`](https://www.gnu.org/software/coreutils/manual/html_node/rm-invocation.html).
- GNU Coreutils 9.12 `stat` is a project utility, not a POSIX common utility. See [GNU `stat`](https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html).

These distinctions can inform a file-collection or path-change job, but they do not establish the contents or format of a project setting. For archive-member inspection or extraction, use [Extract, reshape, or package information](extract-reshape-package-information.md#inspect-or-extract-an-archive).
