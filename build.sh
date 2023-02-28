#! /usr/bin/env bash
set -euo pipefail

print-usage() {
  cat <<EOF
Usage: $0 [OPTIONS] [service] [imageVersion]

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

# 读取通用配置
source "$(dirname -- "${BASH_SOURCE[0]}")/deploy/config/config.sh"

# 解析参数
service=platform
imageVersion=
currentEnv=TESTING
checkClean=on
buildImage=off
pushImage=off
deployStack=off

while getopts 'TPc:b:p:d:h' OPT; do
  case $OPT in
  T)
    currentEnv=TESTING
    ;;
  P)
    currentEnv=PRODUCTION
    ;;
  c)
    set-option checkClean
    ;;
  b)
    set-option buildImage
    ;;
  p)
    set-option pushImage
    ;;
  d)
    set-option deployStack
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
  service=$1
  if [[ ! "$service" =~ platform|database|cache ]]; then
    echo >&2 invalid image: "$service"
    exit 1
  fi
fi

# 解析镜像版本
imageVersion=${2:-}
if [ -z "$imageVersion" ] && [ "$buildImage" == off ] && [ -f "${imageVersionDir}/${service}.version" ]; then
  imageVersion=$(head -n 1 "${imageVersionDir}/${service}.version")
fi
if [ -z "$imageVersion" ] && [ "$buildImage" == on ]; then
  imageVersion=$(generate-tag-version)
fi

if [ "$service" == cache ]; then
  imageTag=$CACHE_IMAGE_TAG
else
  imageTag=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-${service}:${imageVersion}
fi

echo -e '\e[33mArguments:'
echo "service=${service}"
echo "imageVersion=${imageVersion}"
echo "imageTag=${imageTag}"
echo "env=${currentEnv}"
echo "checkClean=${checkClean}"
echo "buildImage=${buildImage}"
echo "pushImage=${pushImage}"
echo "deployStack=${deployStack}"
echo -e '\n\e[0m'

# 读取环境对应的配置
source "${configDir}/${currentEnv}.config.sh"

# 构建镜像
if [ "$buildImage" == on ]; then
  # 排除不需要构建镜像的服务
  if [ "$service" == cache ]; then
    echo -e "\e[31mcache doesn't need build image" >&2
    exit 1
  fi

  # 检查是否有未提交的文件
  if [ "$checkClean" == on ]; then
    if git -C "$projectDir" diff-index --quiet HEAD; then
      echo -e "\e[33mWorkspace clean\e[0m"
    else
      echo -e "\e[31mWorkspace not clean, commit or stash your changes\e[0m" >&2
      exit 1
    fi
  fi

  baseImageVersion=$(head -n 1 "${imageVersionDir}/base.version")
  baseImageTag=${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-base:${baseImageVersion}
  imageBuildArg=''
  if [ "$service" == platform ]; then
    imageBuildArg="--build-arg BASE_IMAGE_TAG=${baseImageTag}"
  fi
  echo -e "\e[33mBuilding image \e[35m${imageTag}\e[0m"
  docker build \
    --file "${dockerfileDir}/${service}.Dockerfile" \
    --tag "$imageTag" \
    $imageBuildArg \
    "$projectDir"

  echo -e "\e[33mWriting \e[35m${imageVersion}\e[33m into \e[35m${imageVersionDir}/${service}.version\e[0m"
  echo "$imageVersion" >"${imageVersionDir}/${service}.version"
fi

# 推送镜像
if [ "$pushImage" == on ]; then
  if [ "$buildImage" == off ]; then
    echo -e "\e[31mcannot push image without build\e[0m" >&2
    exit 1
  fi
  if [ "$service" == cache ]; then
    echo -e "\e[31mcache doesn't need push image\e[0m" >&2
    exit 1
  fi
  echo -e "\e[33mPushing image \e[35m${imageTag}\e[33m to DockerHub\e[0m"
  docker login --username "$DOCKER_USERNAME" --password "$DOCKER_TOKEN"
  docker push "$imageTag"
fi

# 部署 Docker Stack
if [ "$deployStack" == on ]; then
  if [ "$service" != cache ] && [ -z "$imageVersion" ]; then
    echo -e "\e[31mno imageVersion provided\e[0m" >&2
    exit 1
  fi

  # 根据配置替换 compose.yaml
  export IMAGE_TAG=$imageTag
  if [ "$service" == platform ]; then
    export REPLICAS=$PLATFORM_REPLICAS
  fi
  tmpComposeYaml=$(mktemp)
  trap 'rm -f "$tmpComposeYaml"' EXIT
  envsubst <"${composeDir}/${service}.compose.yaml" >"$tmpComposeYaml"
  cat "$tmpComposeYaml"

  if [ "$SSH_CONFIG_HOST" ]; then
    sshConfig=$SSH_CONFIG_HOST
  else
    sshConfig=${SSH_USER}@${SSH_IP}
  fi
  echo -e "\e[33mDeploying \e[35m${service}\e[33m to \e[35m${currentEnv}\e[0m"
  scp "$tmpComposeYaml" "${sshConfig}:/data/${service}.compose.yaml"
  ssh "$sshConfig" docker stack deploy -c "/data/${service}.compose.yaml" "$DOCKER_STACK_NAME"
fi
