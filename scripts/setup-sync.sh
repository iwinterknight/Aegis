#!/bin/sh
# Run ONCE per machine (from the repo root): enables Aegis multi-machine sync hooks.
#   sh scripts/setup-sync.sh
set -e
git config core.hooksPath .githooks
chmod +x .githooks/* 2>/dev/null || true
# Do an initial restore so transcripts already in the repo land in ~/.claude.
sh .githooks/post-merge || true
echo "Aegis sync enabled: core.hooksPath=.githooks. Commits now include the </> Code thread."
