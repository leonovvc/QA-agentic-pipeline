#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fixture="$here/../stage3-autotests-python-ru/resources"
cp -r "$fixture/project/." .
mkdir -p specs
cp "$fixture/docs/spec-source.md" specs/cart-pricing.md
