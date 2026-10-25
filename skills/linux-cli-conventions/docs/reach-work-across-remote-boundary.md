# Reach Or Work Across A Remote Boundary

Use this page when the requested job crosses an explicit remote-host, network-namespace, or remote-service boundary. A reported route, socket, or SSH option describes a selected view or request; it does not establish reachability, authorization, or a working connection.

## Distinguish A Route View From A Socket View

The iproute2 `ip(8)` interface covers objects such as addresses, links, and routes; `ss(8)` reports socket statistics. Its no-option view omits listeners and shows open non-listening sockets with established connections. These static patterns ask different questions:

```text
ip route show
ss -ltn
```

The first requests route information; the second selects listening TCP sockets. A route view does not prove reachability, and a listener does not prove remote access. The inspected man7-rendered iproute2 manuals did not expose an exact release. See [`ip(8)`](https://man7.org/linux/man-pages/man8/ip.8.html) and [`ss(8)`](https://man7.org/linux/man-pages/man8/ss.8.html).

Linux network namespaces isolate network resources, so identical syntax can refer to different process-scoped views. Some `ip` object commands change configuration, and `ss --kill` closes sockets; neither utility is inherently read-only. See Linux [`netlink(7)`](https://man7.org/linux/man-pages/man7/netlink.7.html) and [`network_namespaces(7)`](https://man7.org/linux/man-pages/man7/network_namespaces.7.html). For other process and mount context, see [Prepare the environment a job needs](prepare-environment-for-a-job.md#read-system-process-and-resource-views).

## Tell A Remote Command From Port Forwarding

OpenBSD-current's [`ssh(1)` manual](https://man.openbsd.org/ssh.1) describes a command argument as running on the remote host instead of a login shell. Its `-N` option requests no remote command, while `-L` forwards connections from a local listening port to a destination reached from the remote side.

Static OpenBSD-current patterns (not a connection procedure):

```text
ssh host.example uname -s
ssh -N -L 127.0.0.1:8443:service.example:443 gateway.example
```

The first names a remote command; the second requests local port forwarding without a remote command. Configuration and server policy affect whether either request succeeds. The OpenBSD manual does not identify a Linux host's installed build, target authorization, or forwarding setup.

## Package Files For A Remote Job

When a job combines packaging files with delivery to a remote host, this page is the primary route because the task crosses a remote boundary. [Extract, reshape, or package information](extract-reshape-package-information.md#inspect-or-extract-an-archive) provides supporting archive listing, extraction, and compression distinctions. That support does not describe file transfer or an end-to-end delivery workflow.

These distinctions do not cover authentication, firewall diagnosis, or an end-to-end connection workflow. When the job is instead to run or debug a local command, use [Run and debug a command or job](run-and-debug-command-or-job.md).
