# Extract, Reshape, Or Package Information

Use this page when the requested result is selected records, fields, counts, filtered logs, or archive contents. The examples are static illustrations of documented behavior, not a complete data-processing workflow.

## Separate Matching From Extracting Fields

GNU Grep 3.12 prints matching lines by default; a match does not mean the output contains only the matched substring. POSIX `grep` defines basic, extended, and fixed-string pattern modes. Search and extraction are different tasks. See [GNU Grep 3.12](https://www.gnu.org/software/grep/manual/html_node/Introduction.html) and [POSIX `grep`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/grep.html).

POSIX `sed` transforms a text stream and writes to standard output; that alone does not rewrite the input pathname. POSIX `awk` processes records and fields, but ordinary splitting is not a parser for every structured format. GNU Awk Edition 5.4 adds CSV input mode for quoted commas and embedded newlines. Its static GNU-specific pattern is limited to that named implementation and does not claim to accept every CSV dialect:

```sh
gawk --csv 'NR == 1 { print $1 }' data.csv
```

See [POSIX `sed`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/sed.html), [POSIX `awk`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/awk.html), and [GNU Awk CSV input](https://www.gnu.org/software/gawk/manual/html_node/Comma-Separated-Fields.html).

POSIX `sort` uses locale collation. POSIX `uniq` compares adjacent lines only, so the static pattern `sort names | uniq` groups equal lines for that comparison; locale still affects ordering. POSIX `cut` selects bytes, characters, or delimited fields; `tr` transforms characters; `tee` copies a stream and can write named destinations. These are distinct stream operations. See POSIX [`sort`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/sort.html), [`uniq`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/uniq.html), [`cut`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/cut.html), [`tr`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/tr.html), and [`tee`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/tee.html). For locale and pipeline interpretation, see [Run and debug a command or job](run-and-debug-command-or-job.md#why-environment-or-locale-changed-a-result).

For pathnames passed into a processing pipeline, see [Find and change project files](find-and-change-project-files.md#find-the-relevant-path); its GNU `find`/`xargs` contrast is about preserving argument boundaries, not parsing record formats.

## Filter Log Records

systemd 262 `journalctl` filters records by unit, boot, time, priority, or structured fields. The static pattern below combines a unit filter with a time bound. Different-field matches combine conjunctively; repeated matches for one field are alternatives. Output comes from journal files the caller can read. A manual does not establish that a journal, unit, or record exists. See the rolling [`journalctl` manual](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html).

```text
journalctl --unit=api.service --since='1 hour ago'
```

When log records are evidence in a launched-job investigation, the primary route is [Run and debug a command or job](run-and-debug-command-or-job.md). This page explains filter and extraction distinctions, not a complete log-aggregation recipe. The supplied sources also do not establish general JSON/YAML parsing or arbitrary CSV-dialect handling.

## Inspect Or Extract An Archive

GNU tar 1.35.90 treats listing and extraction as different operations; extraction writes archive members into a filesystem. See the [GNU tar 1.35.90 manual](https://www.gnu.org/software/tar/manual/tar.html) for the listing and extraction operations. Compression is a separate option. These static GNU tar fragments illustrate the distinction, not a procedure for a live path:

```sh
tar -tf bundle.tar
tar -xf bundle.tar
```

GNU Gzip 1.15 documents compression and decompression as stream operations; POSIX `pax` specifies an archive-interchange interface. ZIP permits a container with no compression, so a suffix alone does not prove its contents or method. See [GNU Gzip](https://www.gnu.org/software/gzip/manual/gzip.html), [POSIX `pax`](https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/pax.html), and [PKWARE APPNOTE 6.3.8](https://pkwaredownloads.blob.core.windows.net/pkware-general/Documentation/APPNOTE-6.3.8.TXT).

Archive listing does not perform extraction, and extraction is a filesystem write. This reference distinguishes the operations without prescribing an extraction workflow. For a general pathname operation, see [Find and change project files](find-and-change-project-files.md#change-a-path-or-its-directory-entry).
