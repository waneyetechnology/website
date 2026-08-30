#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
fixture_root="$(mktemp -d)"
trap 'rm -rf -- "$fixture_root"' EXIT

source_root="$fixture_root/source"
destination_root="$fixture_root/destination"

mkdir -p \
  "$source_root/archive" \
  "$source_root/markets/sectors" \
  "$source_root/newsroom/articles" \
  "$source_root/static" \
  "$source_root/cn" \
  "$source_root/au" \
  "$source_root/api" \
  "$destination_root/archive" \
  "$destination_root/markets" \
  "$destination_root/newsroom"

touch \
  "$source_root/index.html" \
  "$source_root/archive/index.html" \
  "$source_root/archive/report.html" \
  "$source_root/markets/index.html" \
  "$source_root/markets/sectors/sector-01.html" \
  "$source_root/newsroom/index.html" \
  "$source_root/newsroom/articles/article-001.html" \
  "$source_root/static/style.css" \
  "$source_root/cn/index.html" \
  "$source_root/au/index.html" \
  "$source_root/api/analysis.json" \
  "$source_root/robots.txt" \
  "$source_root/sitemap.xml" \
  "$source_root/structured-data.json" \
  "$destination_root/archive/stale.html" \
  "$destination_root/markets/stale.html" \
  "$destination_root/newsroom/stale.html"

bash "$repository_root/scripts/stage-generated-site.sh" "$source_root" "$destination_root"

expected_files=(
  index.html
  archive/index.html
  archive/report.html
  markets/index.html
  markets/sectors/sector-01.html
  newsroom/index.html
  newsroom/articles/article-001.html
  static/style.css
  cn/index.html
  au/index.html
  api/analysis.json
  robots.txt
  sitemap.xml
  structured-data.json
)

for path in "${expected_files[@]}"; do
  test -f "$destination_root/$path"
done

test ! -e "$destination_root/archive/stale.html"
test ! -e "$destination_root/markets/stale.html"
test ! -e "$destination_root/newsroom/stale.html"

broken_source="$fixture_root/broken-source"
mkdir -p "$broken_source/archive" "$broken_source/markets" "$broken_source/newsroom" "$broken_source/static"
touch "$broken_source/index.html"

if bash "$repository_root/scripts/stage-generated-site.sh" "$broken_source" "$fixture_root/broken-destination" >/dev/null 2>&1; then
  echo "Staging unexpectedly accepted missing page-family indexes" >&2
  exit 1
fi

echo "Generated-site staging test passed"
