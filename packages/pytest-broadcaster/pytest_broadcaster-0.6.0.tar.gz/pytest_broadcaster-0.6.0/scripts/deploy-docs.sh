#!/usr/bin/env bash

set -eu

echo -e "Running command: mike deploy -u --push $VERSION $ALIAS"

mike deploy -u --push $VERSION $ALIAS
