#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$here/resources/project/." .
mkdir -p specs
cp "$here/resources/cart-pricing.md" specs/cart-pricing.md
