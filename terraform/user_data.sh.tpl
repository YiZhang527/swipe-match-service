#!/bin/bash
set -euxo pipefail

apt-get update -y
apt-get install -y docker.io docker-compose-v2 git
systemctl enable --now docker

git clone ${repo_url} /opt/swipe-match
cd /opt/swipe-match

cat > .env <<ENV
AWS_REGION=${region}
SWIPES_TABLE=${swipes_table}
MATCHES_TABLE=${matches_table}
ENV

docker compose -f docker-compose.prod.yml up -d --build
