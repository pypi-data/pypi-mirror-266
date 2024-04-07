# ====================================================================================
# Setup Project
include common.mk
include common_linters.mk

# ====================================================================================
# Actions

.PHONY: all
all: test clean

.PHONY: test
test: lint

.PHONY: lint
lint: lint.checkmake lint.superlinter

.PHONY: clean
clean: lint.clean
