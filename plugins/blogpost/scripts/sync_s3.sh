#!/usr/bin/env bash
# sync_s3.sh — sync a blog folder to/from S3.
#
# Usage:
#   sync_s3.sh up   <folder>    # local <blog_folder> -> s3://bucket/prefix/folder/
#   sync_s3.sh down <folder>    # s3://bucket/prefix/folder/ -> local <blog_folder>
#
# Settings:
#   ~/.claude/blogpost.local.md must contain a YAML frontmatter block at the top:
#
#     ---
#     bucket: <S3 bucket name>
#     prefix: <path prefix, e.g. "wogus">
#     ---
#
# Workspace root defaults to ~/blog/. Override with BLOGPOST_WORKSPACE env var.

set -euo pipefail

usage() {
  cat >&2 <<EOF
사용법:
  sync_s3.sh up   <folder>    로컬 폴더를 S3로 업로드
  sync_s3.sh down <folder>    S3에서 로컬로 다운로드
EOF
  exit 2
}

if [[ $# -lt 2 ]]; then
  usage
fi

direction="$1"
folder="$2"

if [[ "$direction" != "up" && "$direction" != "down" ]]; then
  usage
fi

# Validate folder name (no slashes, no spaces, no .. )
if [[ "$folder" == *"/"* || "$folder" == *" "* || "$folder" == ".."* ]]; then
  echo "ERROR: 잘못된 폴더 이름: '$folder' (슬래시, 공백, 상대경로 금지)" >&2
  exit 2
fi

settings_file="${HOME}/.claude/blogpost.local.md"
if [[ ! -f "$settings_file" ]]; then
  cat >&2 <<EOF
ERROR: 설정 파일이 없습니다: $settings_file

다음 형식으로 만들어주세요:

---
bucket: <S3 버킷>
prefix: <경로 prefix>
---
EOF
  exit 1
fi

# Parse YAML frontmatter (simple sed extraction; only top frontmatter block)
frontmatter="$(awk 'NR==1 && /^---$/ {flag=1; next} flag && /^---$/ {exit} flag {print}' "$settings_file")"
if [[ -z "$frontmatter" ]]; then
  echo "ERROR: $settings_file 에 YAML frontmatter 블록(--- ... ---)이 없습니다." >&2
  exit 1
fi

extract_value() {
  # extract_value <key>
  echo "$frontmatter" | sed -nE "s/^[[:space:]]*$1[[:space:]]*:[[:space:]]*\"?([^\"]*)\"?[[:space:]]*$/\1/p" | head -n 1
}

bucket="$(extract_value bucket)"
prefix="$(extract_value prefix)"

if [[ -z "$bucket" ]]; then
  echo "ERROR: $settings_file 에 'bucket' 키가 없거나 비어 있습니다." >&2
  exit 1
fi
if [[ -z "$prefix" ]]; then
  echo "ERROR: $settings_file 에 'prefix' 키가 없거나 비어 있습니다." >&2
  exit 1
fi

# Strip leading/trailing slashes from prefix
prefix="${prefix#/}"
prefix="${prefix%/}"

workspace_root="${BLOGPOST_WORKSPACE:-${HOME}/blog}"
mkdir -p "$workspace_root"
local_folder="${workspace_root}/${folder}"

s3_uri="s3://${bucket}/${prefix}/${folder}/"

if ! command -v aws >/dev/null 2>&1; then
  echo "ERROR: aws CLI가 설치되어 있지 않습니다. https://aws.amazon.com/cli/ 참고." >&2
  exit 1
fi

case "$direction" in
  up)
    if [[ ! -d "$local_folder" ]]; then
      echo "ERROR: 로컬 폴더가 없습니다: $local_folder" >&2
      exit 1
    fi
    echo "📤 업로드: $local_folder/  ->  $s3_uri"
    aws s3 sync "$local_folder/" "$s3_uri" \
      --exclude "_render/*" \
      --exclude "review-history/*" \
      --exclude "_source/*"
    echo "✅ 완료: $s3_uri"
    ;;
  down)
    mkdir -p "$local_folder"
    echo "📥 다운로드: $s3_uri  ->  $local_folder/"
    aws s3 sync "$s3_uri" "$local_folder/"
    if [[ -z "$(ls -A "$local_folder" 2>/dev/null)" ]]; then
      echo "ERROR: $s3_uri 에서 받아올 파일이 없습니다. 폴더 이름을 확인하세요." >&2
      exit 1
    fi
    echo "✅ 완료: $local_folder/"
    ;;
esac
