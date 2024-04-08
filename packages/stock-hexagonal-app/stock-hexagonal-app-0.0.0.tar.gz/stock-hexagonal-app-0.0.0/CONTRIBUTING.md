# Development Guide

## Package

Package structure follows convetion introduced in following doc:
https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html

Hexagonal Architecture for Python project by AWS:
https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/structure-a-python-project-in-hexagonal-architecture-using-aws-lambda.html


## Create python virutal enviroment

Unix

```sh
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell)

```sh
python -m venv .venv
Set-ExecutionPolicy Unrestricted -Scope Process
.venv\Scripts\activate
```

## Install package

```sh
python -m pip install .
```

## Install package in development mode

```sh
python -m pip install --editable .
```

## Build package source and built distribution

```sh
python -m build
```

## Run CLI app

```sh
stock-cli-app --help
```

## Run pre-commit

```sh
pre-commit run -a
```
