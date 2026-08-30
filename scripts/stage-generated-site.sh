#!/usr/bin/env bash
set -euo pipefail

source_root="${1:-website-core}"
destination_root="${2:-.}"

if [[ ! -d "$source_root" ]]; then
  echo "Generated-site source directory does not exist: $source_root" >&2
  exit 1
fi

mkdir -p "$destination_root"
source_root="$(cd "$source_root" && pwd -P)"
destination_root="$(cd "$destination_root" && pwd -P)"

if [[ "$source_root" == "/" || "$destination_root" == "/" || "$source_root" == "$destination_root" ]]; then
  echo "Refusing unsafe staging roots: source=$source_root destination=$destination_root" >&2
  exit 1
fi

required_paths=(
  index.html
  archive
  markets
  newsroom
  static
)

required_page_files=(
  archive/index.html
  archive/report.html
  markets/index.html
  newsroom/index.html
)

optional_paths=(
  history
  cn
  au
  api
  robots.txt
  sitemap.xml
  structured-data.json
)

for path in "${required_paths[@]}"; do
  if [[ ! -e "$source_root/$path" ]]; then
    echo "Required generated artifact is missing: $source_root/$path" >&2
    exit 1
  fi
done

for path in "${required_page_files[@]}"; do
  if [[ ! -f "$source_root/$path" ]]; then
    echo "Required generated page is missing: $source_root/$path" >&2
    exit 1
  fi
done

stage_path() {
  local path="$1"
  if [[ ! -e "$source_root/$path" ]]; then
    return
  fi

  rm -rf -- "$destination_root/$path"
  mv -- "$source_root/$path" "$destination_root/$path"
  echo "Staged $path"
}

for path in "${required_paths[@]}" "${optional_paths[@]}"; do
  stage_path "$path"
done
