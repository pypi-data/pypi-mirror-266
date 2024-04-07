# ====================================================================================
# Setup Project

# remove default suffixes as we dont use them
.SUFFIXES:

# set the shell to bash always
SHELL := /bin/bash

ROOT := $(shell pwd)


ifneq ($(origin GITHUB_WORKSPACE), undefined)
ROOT := $(GITHUB_WORKSPACE)
endif

# set the project folder if not defined
ifeq ($(origin PROJECT_FOLDER), undefined)
PROJECT_FOLDER := $(ROOT)
endif

# set the project folder if not defined
ifeq ($(origin BUILD_TOOLS_FOLDER), undefined)
BUILD_TOOLS_FOLDER := $(ROOT)/build
endif

# set the project name if not defined
ifeq ($(origin PROJECT_NAME), undefined)
PROJECT_NAME := $(shell basename `git -C $(PROJECT_FOLDER) rev-parse --show-toplevel`)
endif

# set the documentation folder if not defined
ifeq ($(origin DOC_FOLDER), undefined)
# check if there are any existing `git tag`
DOC_FOLDER := $(ROOT)/docs
endif

# set the test folder if not defined
ifeq ($(origin TEST_FOLDER), undefined)
TEST_FOLDER := $(ROOT)/tests
endif

# set the project technology if not defined
ifeq ($(origin TECHNOLOGY), undefined)
TECHNOLOGY := shell
endif

# ====================================================================================
# Version and Tagging

# set the version number if not defined
ifeq ($(origin VERSION), undefined)
# check if there are any existing `git tag`
ifeq ($(shell git -C $(PROJECT_FOLDER) tag),)
# no tags found - default to initial tag `v0.0.0`
VERSION := $(shell echo "0.0.0-$$(git -C $(PROJECT_FOLDER) rev-list HEAD --count)")
else
# use tags
VERSION := $(shell git -C $(PROJECT_FOLDER) describe --dirty --always --tags )
endif
endif

# ====================================================================================
# Common Actions

.DEFAULT_GOAL := help

.PHONY: all
all: ## Build and run the main application
	@:

.PHONY: lint
lint: ## Run the static analysis tool to scan the codebase
	@:

.PHONY: fmt
fmt: ## Properly format the codebase
	@:

.PHONY: docs
docs: ## Auto-generates documentation
	@:

.PHONY: setup
setup: ## Setup the main application
	@:

.PHONY: build
build: ## Compile the main application
	@:

.PHONY: run
run: ## Run the main application
	@:

.PHONY: test
test: ## Run all the unit test.
	@:

.PHONY: clean
clean: ## Clean up build project files
	@:

# ====================================================================================
# Utils Actions

# https://stackoverflow.com/a/47107132
.PHONY: help
help: ## Show the basic command help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

.PHONY: help.all
help.all: ## Show the advanced command help.
	@sed -ne '/@sed/!s/#! //p' $(MAKEFILE_LIST)


