#!/usr/bin/env bash
# Copyright 2026 Cole Munz
# SPDX-License-Identifier: AGPL-3.0-only
#
# Merge signalapp/Signal-iOS main into the current branch and re-apply the Wren rebrand.
# Usage: tools/merge-upstream.sh
set -euo pipefail

UPSTREAM_URL=https://github.com/signalapp/Signal-iOS.git

die() {
  echo "error: $*" >&2
  exit 2
}

root=$(git rev-parse --show-toplevel)
cd "$root"

[[ -f "$(git rev-parse --git-path MERGE_HEAD)" ]] && die "a merge is already in progress"
[[ -z $(git status --porcelain) ]] || die "working tree is not clean, commit or stash first"

if ! git remote get-url signal > /dev/null 2>&1; then
  echo "adding remote signal -> $UPSTREAM_URL"
  git remote add signal "$UPSTREAM_URL"
fi

git fetch --no-tags signal main
target=$(git rev-parse --short=12 refs/remotes/signal/main)

if git merge-base --is-ancestor refs/remotes/signal/main HEAD; then
  echo "already up to date with signal/main ($target)"
  exit 0
fi

echo "merging signal/main ($target) into $(git branch --show-current)"
merge_rc=0
git merge --no-commit --no-ff refs/remotes/signal/main || merge_rc=$?

python3 tools/rebrand.py

if [[ $merge_rc -eq 0 ]]; then
  git add -A
  git commit -q -m "Merge signal/main at $target"
  echo "merged cleanly and committed: $(git rev-parse --short HEAD)"
  exit 0
fi

translations=()
code=()
project=()
other=()
while IFS= read -r path; do
  case $path in
    *.lproj/*.strings | *.lproj/*.stringsdict) translations+=("$path") ;;
    *.swift | *.m | *.h | *.proto) code+=("$path") ;;
    *.pbxproj | *.plist | *.entitlements | *.xcconfig) project+=("$path") ;;
    *) other+=("$path") ;;
  esac
done < <(git diff --name-only --diff-filter=U)

print_group() {
  local title=$1
  shift
  echo
  echo "$title ($#)"
  for path in "$@"; do
    echo "  $path"
  done
}

echo
echo "conflicts in signal/main ($target):"
print_group "translations" "${translations[@]}"
print_group "swift-objc-proto" "${code[@]}"
print_group "project-and-plist" "${project[@]}"
print_group "other" "${other[@]}"

cat <<'EOT'

The merge is left uncommitted. To finish:
  1. Fix each file above (project-and-plist: take upstream, rebrand puts the prefix and name back).
  2. python3 tools/rebrand.py
  3. git add -A && git commit
To back out: git merge --abort
EOT
exit 1
