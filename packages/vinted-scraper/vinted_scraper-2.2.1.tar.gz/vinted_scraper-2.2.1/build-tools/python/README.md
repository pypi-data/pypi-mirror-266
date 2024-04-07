# Build - Python

A collection of useful [Python](https://www.python.org/) make command.

## Prerequisites

- [Python 3.10](https://www.python.org/);
- Check [requirements.txt](./requirements.txt).

### Install

Create your `Makefile`. An example of a minimal configuration is:

```makefile
# ====================================================================================
# Setup Project
ROOT := $(shell pwd)/
PROJECT_FOLDER := $(ROOT)/src
BUILD_TOOLS_FOLDER := $(ROOT)/build
TECHNOLOGY := python

include $(BUILD_TOOLS_FOLDER)/common.mk
include $(BUILD_TOOLS_FOLDER)/common_linters.mk
include $(BUILD_TOOLS_FOLDER)/$(TECHNOLOGY)/python.mk

# ====================================================================================
# Actions

.PHONY: all
all: run

.PHONY: run
run: py.run

.PHONY: init
init: py.init

.PHONY: update
update: py.update

.PHONY: test
test: py.test

.PHONY: coverage
coverage: py.coverage

.PHONY: docs
docs: py.docs

.PHONY: fmt
fmt: py.fmt

.PHONY: lint
lint: lint.checkmake lint.superlinter

.PHONY: clean
clean: py.clean lint.clean
```

Then you can initialize the project by executing the following command:

```shell
    make init
```

## Run Unit Test with Docker

This folder contains a `Dockerfile`, `test.Dockerfile` and a `.dockerignore` files to support the `img.test.build`
and `img.test.run` actions.
Learn more about this on the [../image/docker.mk](../image/docker.mk) file!
