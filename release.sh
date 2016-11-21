#!/usr/bin/env bash
set -e

BUILD_NAME="sxrumble-$1"
OUTPUT_PATH="$HOME/sxdrive/sxrumble/$BUILD_NAME.tar.gz"

git archive \
    --format tgz \
    --prefix "$BUILD_NAME/" \
    --output "$OUTPUT_PATH" \
    "$1"
