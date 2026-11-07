#!/bin/sh
# Usage: ./scripts/aws.sh sts get-caller-identity
docker run --rm -it \
  -v "$HOME/.aws":/root/.aws:ro \
  amazon/aws-cli "$@"
