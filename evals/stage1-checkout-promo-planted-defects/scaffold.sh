#!/usr/bin/env bash
# Seeds the empty run workspace with the spec under test.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p specs
cp "$here/resources/spec.md" specs/checkout-promo.md
