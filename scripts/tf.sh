#!/bin/sh
# Usage: ./scripts/tf.sh init | plan | apply | destroy | output
cd "$(dirname "$0")/.." || exit 1
docker run --rm -it \
  -v "$PWD/terraform":/workspace -w /workspace \
  -v "$HOME/.aws":/root/.aws:ro \
  hashicorp/terraform:1.9.8 "$@"
