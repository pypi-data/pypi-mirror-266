#!/bin/bash

# Run the formatters
make fmt

# Add the changed files in the current commit
git add -A

# Run the linters
make lint
