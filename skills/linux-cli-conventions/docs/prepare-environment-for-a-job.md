# Prepare The Environment A Job Needs

Use this page to distinguish prerequisite and context reports before a job starts: package availability versus installation, unit-file versus runtime state, access and identity views, resource context, or storage reports. These are documented distinctions, not installation, configuration, permission-repair, or cleanup procedures.

## Check Package And Unit States

Debian Bookworm APT 2.6.1 documents `apt search` over available-package data and `apt list --installed` for installed packages. Its `apt` command targets end users, and behavior can change between versions. DNF5 stable documentation separately distinguishes `dnf5 list --installed` from `dnf5 list --available --showduplicates`. Search results describe configured package data, not necessarily installed state; available versions depend on repository metadata. These are distribution-specific interfaces, not universal Linux syntax. See [Debian Bookworm `apt(8)`](https://manpages.debian.org/bookworm/apt/apt.8.en.html) and [DNF5 stable `list`](https://dnf5.readthedocs.io/en/stable/commands/list.8.html); the DNF5 page did not expose an exact release.

```text
apt search example-name
apt list --installed example-name
dnf5 list --available --showduplicates example-name
```

The upstream [`systemctl` manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) uses systemd meanings, not generic service-manager states. `list-units` shows units currently in manager memory; `list-unit-files` shows installed unit files and enablement state. Enabling a unit does not start it, and starting it does not enable it. `status` gives human-readable runtime output; `show` supplies machine-readable properties. The rolling page displayed systemd 262 when inspected.

For a unit that fails to start, including before its process launches, [Run and debug a command or job](run-and-debug-command-or-job.md) is the primary failure-investigation route; this section is supporting context for unit-file, enablement, and runtime-state distinctions. Journal filtering is described under [Extract, reshape, or package information](extract-reshape-package-information.md#filter-log-records). For checking prerequisite readiness rather than investigating a failure, this page remains the primary route.

## Interpret Identity And Access Context

GNU Coreutils `id` reports user and group identifiers; Linux `credentials(7)` describes process credentials. Neither display alone decides access to a path. Linux `acl(5)` describes named user and group entries plus a mask; when present, the mask supplies the group-class permission bits, rather than the owning-group entry alone. Linux capabilities are separate per-thread privilege units. File capabilities can participate in transitions across `execve()`.

An identity string or mode-bit display therefore does not establish an effective access result. The manuals do not establish that a path has an extended ACL, an executable has file capabilities, or a process has particular credentials. `sudo` runs a permitted command as another user under configured policy; its environment, argument matching, and effective scope depend on that policy and implementation. See GNU [`id(1)`](https://www.gnu.org/software/coreutils/manual/html_node/id-invocation.html), Linux [`credentials(7)`](https://man7.org/linux/man-pages/man7/credentials.7.html), [`acl(5)`](https://man7.org/linux/man-pages/man5/acl.5.html), [`capabilities(7)`](https://man7.org/linux/man-pages/man7/capabilities.7.html), and the [`sudo`](https://www.sudo.ws/docs/man/sudo.man/) and [`sudoers`](https://www.sudo.ws/docs/man/sudoers.man/) manuals.

## Read System, Process, And Resource Views

Linux pathname resolution starts at the process root for an absolute path and its working directory for a relative path. Symbolic links and mount points affect traversal. Mount namespaces can give processes different mount lists, so a process view is not automatically system-wide. See Linux [pathname resolution](https://man7.org/linux/man-pages/man7/path_resolution.7.html) and [mount namespaces](https://man7.org/linux/man-pages/man7/mount_namespaces.7.html).

Linux cgroup v2 organizes processes in a hierarchy and distributes resources through controllers. The kernel guide says restrictions closer to the hierarchy root cannot be overridden farther down. A process's resource context can therefore reflect ancestor settings as well as its own cgroup, rather than one flat number. The kernel's mutable [`cgroup v2` guide](https://docs.kernel.org/admin-guide/cgroup-v2.html) displays an embedded date of October 2015; it does not establish which cgroup version, controller, hierarchy, or limit a system supports or uses.

Kernel documentation describes `/proc` as an interface to kernel data and `/proc/sys` as runtime configuration for selected kernel aspects. Sysfs exports kernel objects and attributes; some details expose internal implementation and can change between releases. These descriptions do not establish that a path exists, remains stable, or has a particular value. See kernel [procfs](https://docs.kernel.org/filesystems/proc.html), [`/proc/sys`](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/index.html), [sysfs](https://docs.kernel.org/filesystems/sysfs.html), and [sysfs access rules](https://docs.kernel.org/admin-guide/sysfs-rules.html).

Linux [`os-release(5)`](https://man7.org/linux/man-pages/man5/os-release.5.html) defines distribution-style identification fields. GNU Coreutils [`uname(1)`](https://www.gnu.org/software/coreutils/manual/html_node/uname-invocation.html) reports kernel and machine fields. They describe different identity layers; neither manual supplies values for an uninspected system.

## Distinguish Space And Mount Reports

POSIX `df` reports filesystem-space information; `du` estimates space for a file hierarchy. A static contrast is `df .` versus `du -s .`: the first describes the filesystem containing the operand, while the second summarizes the hierarchy. GNU Coreutils 9.12 documents additional distinctions: `du` counts hard-linked content once under its rules, operand order can affect which link it counts, and `--apparent-size` reports logical file length rather than comparable allocated usage. A directory estimate is not a filesystem-capacity report, and `df` is not a physical-device inventory. GNU Coreutils also warns that reported space can differ from underlying-device use, including on copy-on-write or compressed filesystems. See [POSIX `df`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/df.html), [POSIX `du`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/du.html), and GNU Coreutils 9.12 [`df`](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html) and [`du`](https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html).

The inspected util-linux 2.43 development manuals describe separate views; those versions identify development builds, not a distribution release. `lsblk` describes block devices using sysfs and udev data; a device and filesystem need not have a one-to-one relationship, and its default output can change. `findmnt` can report the process's kernel mount view from `/proc/self/mountinfo` or search configured entries such as `/etc/fstab`; those answer different questions, and its default output can change. The manual renderings do not establish installed tools or live devices and mounts. See [`lsblk(8)`](https://man7.org/linux/man-pages/man8/lsblk.8.html) and [`findmnt(8)`](https://man7.org/linux/man-pages/man8/findmnt.8.html).

For an explicit remote host or network-service boundary, use [Reach or work across a remote boundary](reach-work-across-remote-boundary.md). For shell lookup, quoting, and job behavior, see [Run and debug a command or job](run-and-debug-command-or-job.md).
