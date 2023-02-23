#! /usr/bin/env bash
set -euo pipefail
set -x

print_usage() {
  cat <<EOF
Usage: $0 [OPTIONS] [PROJECT_PATH]

Project path:
  Path of the project, default current directory.

Options:
  -h, --help    Print this help and exit.
EOF
}

# 解析参数

# shellcheck disable=SC2046
set -- $(getopt -o h --long help -n "$0" -- "$@")

while [ "$1" ]; do
  case "$1" in
  -h | --help)
    print_usage
    exit 0
    ;;
  --)
    shift
    break
    ;;
  *)
    echo "unknown options: $1"
    print_usage
    exit 1
    ;;
  esac
done

echo End parsing, remaining arguments: "$@"
