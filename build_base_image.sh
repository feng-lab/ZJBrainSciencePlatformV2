#! /usr/bin/env bash
set -euo pipefail

# 读取配置
projectDir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
scriptDir=$(cd -- "${projectDir}/deploy_config" &>/dev/null && pwd)
dockerfileDir=$(cd -- "$projectDir/dockerfile" &>/dev/null && pwd)
echo -e '\e[33mReading config...\e[0m'
source "${scriptDir}/config.sh"

# 构建镜像
imageVersion=$(git -C "$projectDir" rev-parse --verify --short HEAD)
imageTag="${BASE_IMAGE_REPO}:${imageVersion}"
echo -e "\e[33mBuilding image \e[35m${imageTag}\e[0m\e[33m...\e[0m"
docker build \
  --file "$dockerfileDir/base.Dockerfile" \
  --tag "$imageTag" \
  --build-arg "PYTHON_VERSION=${PYTHON_VERSION}" \
  --build-arg "POETRY_VERSION=${POETRY_VERSION}" \
  --build-arg "PIP_INDEX_OPTION=-i ${PIP_INDEX_URL}" \
  "$projectDir"

# 推送镜像到Docker Hub
echo -e "\e[33mPushing image \e[35m${imageTag}\e[0m\e[33m to DockerHub...\e[0m"
docker login --username "$DOCKER_USERNAME" --password "$DOCKER_TOKEN"
docker push "$imageTag"

# 提示把imageVersion写入到config.sh里
echo -e '\e[32mBuild base image succeed!\e[0m'
echo -e "\e[31mReplace \e[36;4mBASE_IMAGE_VERSION\e[0m\e[31m's default value to \e[36;4m${imageVersion}\e[0m\e[31m in \e[36;4m${scriptDir}/config.sh\e[0m"
