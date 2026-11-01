#!/bin/sh
set -eu

parent=${JUDGE_CGROUP_PARENT:-/sys/fs/cgroup/hustoj-judger}
mount=/sys/fs/cgroup

[ "$(id -u)" = 0 ] || { echo 'cgroup setup requires root' >&2; exit 1; }
[ "$(stat -f -c %T "$mount")" = cgroup2fs ] || { echo 'cgroup v2 is required' >&2; exit 1; }
grep -qw memory "$mount/cgroup.subtree_control"
grep -qw pids "$mount/cgroup.subtree_control"
mkdir -p "$parent"
[ -z "$(cat "$parent/cgroup.procs")" ] || { echo 'cgroup parent must be empty' >&2; exit 1; }
printf '+memory +pids' > "$parent/cgroup.subtree_control"
chown root:root "$parent"
chmod 0755 "$parent"
