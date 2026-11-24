#!/usr/bin/env bash
# Собирает zip текущей версии репозитория (последний коммит) для передачи.
# Использование: scripts/make_zip.sh <путь-к-zip>
set -euo pipefail
cd "$(dirname "$0")/.."
out="${1:-netupi.zip}"
git archive --format=zip --prefix=netupi/ -o "$out" HEAD
echo "$out ($(du -h "$out" | cut -f1)), коммит $(git rev-parse --short HEAD)"
