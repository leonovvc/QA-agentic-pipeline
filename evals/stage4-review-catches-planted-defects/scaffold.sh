#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p docs/qa/cart-orders
cp "$here"/resources/docs/*.md docs/qa/cart-orders/
