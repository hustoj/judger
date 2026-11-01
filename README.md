# HUST Online Judge Server

## Introduce

This project retrieve task from rabbitmq, get information of solution from hustoj, use [runner](https://github.com/hustoj/runner) to compile and execute solution. Check user program is an accept solution.

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/hustoj/judger/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/?branch=master) 
[![Build Status](https://scrutinizer-ci.com/g/hustoj/judger/badges/build.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/hustoj/judger/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/?branch=master) 
[![Code Intelligence Status](https://scrutinizer-ci.com/g/hustoj/judger/badges/code-intelligence.svg?b=master)](https://scrutinizer-ci.com/code-intelligence)



## Install

**Notice: You should install [runner](https://github.com/hustoj/runner) first on your machine.**

1. You should install python with 3.6 or newer
2. You should install [poetry](https://github.com/python-poetry/poetry)
3. install python dependency:
    
    ```bash
    poetry install
    ```
4. configure 

    ```bash
    cp judge.sample.toml judge.toml
    ```
    
    detail description can see judge.sample.toml, you can modify judge.toml as your actual environment.
    
5. run

    ```bash
    pipenv shell
    python judged.py
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

Run offline regression tests with dependencies installed:

```bash
python -m unittest tests.test_remote tests.test_judged tests.test_result \
    tests.test_datautils tests.test_comparer tests.test_language tests.test_runner
```

Docker compiler/runner tests require a Linux host with the configured
`compiler:v1` and `runner:v1` images:

```bash
python -m unittest tests.docker
```
