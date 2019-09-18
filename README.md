# HUST Online Judge Server

## Introduce

This project retrieve task from rabbitmq, get imformation of sulution from hustoj, use [runner](https://github.com/hustoj/runner) to compile and execute solution. Check user program is a accept solution.

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/hustoj/judger/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/?branch=master) 
[![Build Status](https://scrutinizer-ci.com/g/hustoj/judger/badges/build.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/hustoj/judger/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/hustoj/judger/?branch=master) 
[![Code Intelligence Status](https://scrutinizer-ci.com/g/hustoj/judger/badges/code-intelligence.svg?b=master)](https://scrutinizer-ci.com/code-intelligence)



## Install

**Notice: You should install [runner](https://github.com/hustoj/runner) first on your machine.**

1. You should install python with 3.6 or newer
2. You should install [pipenv](https://github.com/pypa/pipenv)
3. install python dependency:
    
    ```bash
    pipenv --python 3.6 # use 3.6 or higher
    pipenv install
    ```
4. configure 

    ```bash
    cp judge.sample.toml judge.toml
    ```
    
    detail description can see judge.sample.toml, you can modify judge.toml as your actual enviroment.
    
5. run

    ```bash
    pipenv shell
    python judged.py
    ```

