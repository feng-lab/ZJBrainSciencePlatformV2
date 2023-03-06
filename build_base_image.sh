#! /usr/bin/env bash
set -euo pipefail

# 读取配置
source "$(dirname -- "${BASH_SOURCE[0]}")/deploy/config/config.sh"

# 构建镜像
imageRepo="${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-base"
imageVersion="$(generate-tag-version)"
imageTag="${imageRepo}:${imageVersion}"
echo -e "\e[33mBuilding image \e[35m${imageTag}\e[0m"
docker build \
  --file "${dockerfileDir:?}/base.Dockerfile" \
  --tag "$imageTag" \
  --build-arg "PYTHON_VERSION=${PYTHON_VERSION}" \
  --build-arg "POETRY_VERSION=${POETRY_VERSION}" \
  --build-arg "PIP_INDEX_OPTION=-i ${PIP_INDEX_URL}" \
  "${projectDir:?}"

# 推送镜像到Docker Hub
echo -e "\e[33mPushing image \e[35m${imageTag}\e[0m\e[33m to DockerHub\e[0m"
docker login --username "$DOCKER_USERNAME" --password "$DOCKER_TOKEN"
docker push "$imageTag"

# 把版本号写入base.version
echo "$imageVersion" >"${imageVersionDir:?}/base.version"
echo -e "\e[32mBuild base image ${imageVersion} succeed!\e[0m"
