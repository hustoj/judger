# HUST Online Judge Server

## Introduce

This project retrieve task from rabbitmq, get information of solution from hustoj, use [runner](https://github.com/hustoj/runner) to compile and execute solution. Check user program is an accept solution.

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/hustoj/judger/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/?branch=master) 
[![Build Status](https://scrutinizer-ci.com/g/hustoj/judger/badges/build.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/hustoj/judger/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/?branch=master) 
[![Code Intelligence Status](https://scrutinizer-ci.com/g/hustoj/judger/badges/code-intelligence.svg?b=master)](https://scrutinizer-ci.com/code-intelligence)



## Install

**Notice: You should install [runner](https://github.com/hustoj/runner) first on your machine.**

1. You should install Python 3.10 or newer. [uv](https://docs.astral.sh/uv/) can install it for you.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
3. Install Python dependencies. This creates `.venv`, which `judged.service` runs:

    ```bash
    uv sync --no-dev
    ```

    `uv.lock` records wheels on files.pythonhosted.org, so a mirror
    variable does not redirect `uv sync`. To resolve through Aliyun while
    updating the lock:

    ```bash
    UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple uv lock
    ```

4. Configure:

    ```bash
    cp judge.sample.toml judge.toml
    ```

    See `judge.sample.toml` and edit `judge.toml` for the actual environment.

5. Run:

    ```bash
    uv run --no-dev python judged.py
    ```

## Laravel 13 judge API

The API client uses HMAC-SHA256 authentication (`Token-Version: 2`) with a
fresh nonce for every request. Keep the registered `judge_id` and `code` in
the private `judge.toml`; do not commit production credentials. Use HTTPS
except for a loopback-only API such as `http://localhost:5000/judge/api/`.
The optional `[api].timeout` defaults to 30 seconds. Redirects are rejected
to prevent forwarding authentication headers to another host.

Every new queue task must contain a `judge_token` issued by the website.
The daemon returns it with the result, including `solution_id`, `status`,
`time_cost` and `memory_cost`. Compile/runtime diagnostics use
`compile_info` / `runtime_info`. The task token and source code are not
written to task receipt/error logs. HTTP failures and nonzero API error
codes are not treated as successful reports.

When upgrading, pause website submissions and drain the old queue before
switching both services. The daemon uses `[judged].idle_time`; older
deployments using `sleep_time` must rename that setting. Keep production
language/image configuration and virtual environments when deploying.
Enable submissions only after testing a real task through the queue and
confirming that the website persists its result. Do not enable legacy API
authentication as a substitute for upgrading the daemon.

### v2 sandbox deployment

Build `runner:v2` and `compiler:v2` from the sibling `runner` repository and
set the image names in `languages.toml`. These binaries require Linux
cgroup v2 with delegated `memory` and `pids` controllers. Install the supplied `judged.service` only after `uv sync --no-dev`
in `/srv/hustoj/judger`. The unit runs `.venv/bin/python` and does not
call uv. A Poetry virtualenv is not on that path. `ExecStartPre` prepares
the root-owned `/sys/fs/cgroup/hustoj-judger` subtree on every start.

Only that delegated subtree is mounted into each container, at
`/run/hustoj-cgroup`; the host cgroup root is not exposed writable.
The trusted launcher runs as container root with `SYS_PTRACE`, while both
compiler and runner children explicitly drop to UID/GID 1536 with
`NoNewPrivs`. Containers retain a read-only root filesystem and disabled
networking. Do not use privileged containers, disable syscall checks, or
enable `RUNNER_ALLOW_UNSAFE_TEST_MODE` in production.

Task directories are owned by UID/GID 1536. `case.json` now carries the
language command and argument array explicitly; Java uses a separate
runtime syscall profile, bounded JVM heap/native-memory settings and a
64-thread task budget. Compiler responses must contain `success: true`;
otherwise diagnostics are returned as a compile error. Infrastructure
failures must never leave an Accepted result behind.

Run offline regression tests with dependencies installed:

```bash
uv sync
uv run pytest
```

Docker compiler/runner tests require a Linux host with the configured
`compiler:v2` and `runner:v2` images, root permissions to manage task directories,
and a delegated cgroup v2 parent (the same setup as the daemon):

```bash
sudo sh scripts/prepare-cgroup.sh
sudo .venv/bin/python -m pytest tests/docker -v
```

CI runs offline tests on Python 3.10–3.12 and the four Docker language tests
in a separate Linux job on every push and pull request. That job builds the
sandbox images from the production Dockerfiles in a pinned `hustoj/runner`
commit. Update the runner commit in `.github/workflows/ci.yml` when upgrading
the sandbox. Missing cgroup delegation or failed image builds fail the job;
Docker tests are not silently skipped. Containers use the production isolation
settings, without privileged mode or unsafe test overrides.
