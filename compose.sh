#! /usr/bin/env bash
set -euo pipefail

print-usage() {
  cat <<EOF
Usage: $0 [OPTIONS] [COMMAND]

Options:
  -L                 Use LOCAL environment (default)
  -T                 Use TESTING environment
  -P                 Use PRODUCTION environment
  -h                 Print this usage

Command:
  up-depends         Up database & cache (default command)
  alembic            Run 'alembic upgrade head' in environment
  <other command>    Other command
EOF
}

env=
check-and-set-env() {
  if [ "$env" ]; then
    echo >&2 "more than one environment flags were set"
    exit 1
  else
    env=$1
  fi
}

# 读取通用配置
source "$(dirname -- "${BASH_SOURCE[0]}")/deploy/config/config.sh"

while getopts 'LTPh' OPT; do
  case "$OPT" in
  L)
    check-and-set-env LOCAL
    ;;
  T)
    check-and-set-env TESTING
    ;;
  P)
    check-and-set-env PRODUCTION
    ;;
  h)
    print-usage
    exit 0
    ;;
  ?)
    print-usage
    exit 1
    ;;
  esac
done
shift $((OPTIND - 1))

command="${1:-up-depends}"
args=()
DATABASE_URL=

case "$command" in
up-depends)
  args=(up -d --force-recreate database cache)
  ;;
alembic)
  args=(run --rm platform alembic upgrade head)
  ;;
*)
  args=("$@")
  ;;
esac

if [ -z "$env" ] || [ "$env" == LOCAL ]; then
  databaseHost=database
  databasePort=3306
else
  # shellcheck source=deploy/config/TESTING.config.sh
  source "${configDir:?}/${env}.config.sh"
  databaseHost=$SSH_IP
  databasePort=8100
fi
export DATABASE_URL="mysql+pymysql://zjlab:zjlab2022@${databaseHost}:${databasePort}/zj_brain_science_platform"

export PLATFORM_IMAGE_TAG="${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-platform"
export DATABASE_IMAGE_TAG="${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-database"

docker compose \
  --file "${composeDir:?}/dev.compose.yaml" \
  "${args[@]}"
