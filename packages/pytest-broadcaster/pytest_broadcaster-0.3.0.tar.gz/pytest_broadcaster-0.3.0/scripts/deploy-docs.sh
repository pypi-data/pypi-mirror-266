#!/usr/bin/env bash

set -eu

echo -e "Running command: mike mike deploy --push $VERSION $ALIAS"

mike deploy --push $VERSION $ALIAS
