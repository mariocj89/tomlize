MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

PYTHON ?= python
WORKDIR ?= .

package := tomlize
packagedir := src/$(package)
testsdir := tests
python_files := $(shell find * -name \*.py -not -path '*/\.*')

.PHONY: check
check:
	$(PYTHON) -m pytest $(testsdir)

.PHONY: coverage
coverage:
	$(PYTHON) -m pytest \
           --cov=$(package) \
           --cov-report term-missing \
           --no-cov-on-fail \
           --cov-fail-under=100 \
           $(testsdir)

.PHONY: format
format:
	$(PYTHON) -m black $(python_files)
	$(PYTHON) -m isort $(python_files)


.PHONY: lint
lint:
	$(PYTHON) -m ruff $(python_files)
	$(PYTHON) -m black --check $(python_files)
	$(PYTHON) -m isort --check $(python_files)


.PHONY: lint
fix: format
	$(PYTHON) -m ruff $(python_files) --fix
