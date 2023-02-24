#! /usr/bin/env bash
set -euo pipefail

print-usage() {
  cat <<EOF
Usage: $0 [OPTIONS] [IMAGE] [IMAGE_VERSION]

Image: platform | database
  Docker image name, default is platform

Image version:
  Used when deploy without build

Options:
  -T             Use TESTING env (default)
  -P             Use PRODUCTION env
  -c on | off    Check workspace is clean (default on)
  -b on | off    Build new docker image (default off)
  -p on | off    Push image to docker hub (default off)
  -d on | off    Deploy docker stack (default off)
  -h             Print this help and exit
EOF
}

set-option() {
  local option=$OPTARG
  if [ "$option" != on ] && [ "$option" != off ]; then
    echo -e "\e[31mInvalid option value for ${1}: ${option}\e[0m" >&2
    exit 1
  fi
  eval "$1=$option"
}

projectDir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
scriptDir=$(cd -- "${projectDir}/deploy_config" &>/dev/null && pwd)
dockerfileDir=$(cd -- "$projectDir/dockerfile" &>/dev/null && pwd)

# 解析参数

IMAGE=platform
IMAGE_VERSION=
CURRENT_ENV=TESTING
CHECK_CLEAN=on
BUILD_IMAGE=off
PUSH_IMAGE=off
DEPLOY_STACK=off

while getopts 'TPc:b:p:d:h' OPT; do
  case $OPT in
  T)
    CURRENT_ENV=TESTING
    ;;
  P)
    CURRENT_ENV=PRODUCTION
    ;;
  c)
    set-option CHECK_CLEAN on
    ;;
  b)
    set-option BUILD_IMAGE off
    ;;
  p)
    set-option PUSH_IMAGE off
    ;;
  d)
    set-option DEPLOY_STACK off
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
shift $(($OPTIND - 1))

if [ "${1:-}" ]; then
  IMAGE=$1
  if [[ ! "$IMAGE" =~ platform|database|cache ]]; then
    echo >&2 invalid image: "$IMAGE"
    exit 1
  fi
fi
if [ "${2:-}" ]; then
  IMAGE_VERSION=$2
else
  IMAGE_VERSION=$(git -C "$projectDir" rev-parse --short=8 HEAD)
fi

# 读取配置
source "${scriptDir}/config.sh"
source "${scriptDir}/config_${CURRENT_ENV}.sh"
echo -e "\e[33mRead config: config.sh, config_${CURRENT_ENV}.sh\e[0m"

if [ "$IMAGE" == cache ]; then
  IMAGE_TAG=$CACHE_IMAGE_TAG
else
  IMAGE_TAG=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-${IMAGE}:${IMAGE_VERSION}
fi

echo -e '\e[33mArguments:'
echo "IMAGE=${IMAGE}"
echo "IMAGE_VERSION=${IMAGE_VERSION}"
echo "IMAGE_TAG=${IMAGE_TAG}"
echo "ENV=${CURRENT_ENV}"
echo "CHECK_CLEAN=${CHECK_CLEAN}"
echo "BUILD_IMAGE=${BUILD_IMAGE}"
echo "PUSH_IMAGE=${PUSH_IMAGE}"
echo "DEPLOY_STACK=${DEPLOY_STACK}"
echo -e '\n\e[0m'

# 构建并推送镜像
if [ "$BUILD_IMAGE" == on ]; then
  if [ "$IMAGE" == cache ]; then
    echo -e "\e[31mcache doesn't need build image" >&2
    exit 1
  fi
  # 检查是否有未提交的文件
  if [ "$CHECK_CLEAN" == on ]; then
    if git -C "$projectDir" diff-index --quiet HEAD; then
      echo -e "\e[33mWorkspace clean\e[0m"
    else
      echo -e "\e[31mWorkspace not clean, commit or stash your changes\e[0m" >&2
      exit 1
    fi
  fi

  baseImageTag=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-base:${BASE_IMAGE_VERSION}
  imageBuildArg=''
  if [ "$IMAGE" == platform ]; then
    imageBuildArg="--build-arg BASE_IMAGE_TAG=${baseImageTag}"
  fi

  echo -e "\e[33mBuilding image \e[35m${IMAGE_TAG}\e[0m"
  docker build \
    --file "${dockerfileDir}/${IMAGE}.Dockerfile" \
    --tag "$IMAGE_TAG" \
    $imageBuildArg \
    "$projectDir"
fi

# 推送镜像
if [ "$PUSH_IMAGE" == on ]; then
  if [ "$IMAGE" == cache ]; then
    echo -e "\e[31mcache doesn't need push image" >&2
    exit 1
  fi
  echo -e "\e[33mPushing image \e[35m${IMAGE_TAG}\e[33m to DockerHub\e[0m"
  docker login --username "$DOCKER_USERNAME" --password "$DOCKER_TOKEN"
  docker push "$IMAGE_TAG"
fi

# 部署 Docker Stack
if [ "$DEPLOY_STACK" == on ]; then
  if [ "$IMAGE" != cache ] && [ -z "$IMAGE_VERSION" ]; then
    echo -e "\e[31mIMAGE_VERSION not provided\e[0m" >&2
    exit 1
  fi
  export IMAGE_TAG
  if [ "$IMAGE" == platform ]; then
    export REPLICAS=$PLATFORM_REPLICAS
  fi
  tmpComposeYaml=$(mktemp)
  trap 'rm -f "$tmpComposeYaml"' EXIT
  envsubst <"${dockerfileDir}/${IMAGE}.compose.yaml" >"$tmpComposeYaml"
  cat "$tmpComposeYaml"

  if [ "$SSH_CONFIG_HOST" ]; then
    sshConfig=$SSH_CONFIG_HOST
  else
    sshConfig=${SSH_USER}@${SSH_IP}
  fi
  echo -e "\e[33mDeploying \e[35m${IMAGE}\e[33m to \e[35m${CURRENT_ENV}\e[0m"
  scp "$tmpComposeYaml" "${sshConfig}:/data/${IMAGE}.compose.yaml"
  ssh "$sshConfig" docker stack deploy -c "/data/${IMAGE}.compose.yaml" "$DOCKER_STACK"
fi
