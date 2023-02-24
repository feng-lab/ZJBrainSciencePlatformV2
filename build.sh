#! /usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<EOF
Usage: $0 [OPTIONS] [IMAGE] [IMAGE_VERSION]

Image: platform | database
  Docker image name, default is platform

Image version:
  Used when deploy without build

Options:
  -T    Use TESTING env (default)
  -P    Use PRODUCTION env
  -b    Build new docker image and push to docker hub
  -p    Push image to docker hub
  -d    Deploy docker stack
  -h    Print this help and exit
EOF
}

projectDir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
scriptDir=$(cd -- "${projectDir}/deploy_config" &>/dev/null && pwd)
dockerfileDir=$(cd -- "$projectDir/dockerfile" &>/dev/null && pwd)

# 解析参数

CURRENT_ENV=TESTING
IMAGE=platform
IMAGE_VERSION=
BUILD_IMAGE=off
PUSH_IMAGE=off
DEPLOY_STACK=off

while getopts 'TPbpdh' OPT; do
  case $OPT in
  T)
    CURRENT_ENV=TESTING
    ;;
  P)
    CURRENT_ENV=PRODUCTION
    ;;
  b)
    BUILD_IMAGE=on
    ;;
  p)
    PUSH_IMAGE=on
    ;;
  d)
    DEPLOY_STACK=on
    ;;
  h)
    print_usage
    exit 0
    ;;
  ?)
    print_usage
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
fi

echo -e '\e[33mArguments:'
echo "ENV=${CURRENT_ENV}"
echo "IMAGE=${IMAGE}"
echo "IMAGE_VERSION=${IMAGE_VERSION}"
echo "BUILD_IMAGE=${BUILD_IMAGE}"
echo "PUSH_IMAGE=${PUSH_IMAGE}"
echo "DEPLOY_STACK=${DEPLOY_STACK}"
echo -e '\n\e[0m'

# 读取配置
source "${scriptDir}/config.sh"
source "${scriptDir}/config_${CURRENT_ENV}.sh"
echo -e "\e[33mRead config: config.sh, config_${CURRENT_ENV}.sh\e[0m"

# 构建并推送镜像
if [ "$BUILD_IMAGE" == on ]; then
  if [ "$IMAGE" == cache ]; then
    echo -e "\e[31mcache doesn't need build image" >&2
    exit 1
  fi
  # 检查是否有未提交的文件
  if git -C "$projectDir" diff-index --quiet HEAD; then
    echo -e "\e[33mWorkspace clean\e[0m"
  else
    echo -e "\e[31mWorkspace not clean, commit or stash your changes\e[0m" >&2
    exit 1
  fi

  imageRepo=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-${IMAGE}
  IMAGE_VERSION=$(git -C "$projectDir" rev-parse --short=8 HEAD)
  imageTag=${imageRepo}:${IMAGE_VERSION}
  baseImageTag=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-base:${BASE_IMAGE_VERSION}
  imageBuildArg=''
  if [ "$IMAGE" == platform ]; then
    imageBuildArg="--build-arg BASE_IMAGE_TAG=${baseImageTag}"
  fi

  echo -e "\e[33mBuilding image \e[35m${imageTag}\e[0m"
  docker build \
    --file "${dockerfileDir}/${IMAGE}.Dockerfile" \
    --tag "$imageTag" \
    $imageBuildArg \
    "$projectDir"
fi

# 推送镜像
if [ "$PUSH_IMAGE" == on ]; then
  if [ "$IMAGE" == cache ]; then
    echo -e "\e[31mcache doesn't need push image" >&2
    exit 1
  fi
  echo -e "\e[33mPushing image \e[35m${imageTag}\e[33m to DockerHub\e[0m"
  docker login --username "$DOCKER_USERNAME" --password "$DOCKER_TOKEN"
  docker push "$imageTag"
fi

# 部署 Docker Stack
if [ "$DEPLOY_STACK" == on ]; then
  if [ -z "$IMAGE_VERSION" ]; then
    echo -e "\e[31mIMAGE_VERSION not provided\e[0m" >&2
    exit 1
  fi
  if [ "$IMAGE" == cache ]; then
    export IMAGE_TAG=${CACHE_IMAGE_TAG}
  else
    export IMAGE_TAG=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-${IMAGE}:${IMAGE_VERSION}
  fi
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
  ssh sshConfig docker stack deploy -c "/data/${IMAGE}.compose.yaml" "$DOCKER_STACK"
fi
