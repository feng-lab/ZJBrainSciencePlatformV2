# Docker配置
export DOCKER_USERNAME='cnife'
export DOCKER_TOKEN='dckr_pat_IJKxGMNI_c-n54Fral-saNmZv-A'
export DOCKER_STACK_NAME='platform'
export COMPOSE_PROJECT_NAME='platform'

# 镜像配置
export IMAGE_REPO_PREFIX='zj-brain-science-platform'
export CACHE_IMAGE_TAG='redis:7.0'
export PYTHON_VERSION='3.11'
export POETRY_VERSION='1.4.2'
export PIP_INDEX_URL='https://pypi.tuna.tsinghua.edu.cn/simple'

# 目录结构
configDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
projectDir="$(cd -- "${configDir}/../.." &>/dev/null && pwd)"
dockerfileDir="$(cd -- "${projectDir}/deploy/dockerfile" &>/dev/null && pwd)"
imageVersionDir="$(cd -- "${projectDir}/deploy/image-version" &>/dev/null && pwd)"
composeDir="$(cd -- "${projectDir}/deploy/compose" &>/dev/null && pwd)"
export configDir projectDir dockerfileDir imageVersionDir composeDir

# 工具函数
generate-tag-version() {
  local dateTime gitHash
  dateTime="$(date +'%Y%m%d-%H%M%S')"
  gitHash="$(git -C "$projectDir" rev-parse --short=8 HEAD)"
  echo "${dateTime}-${gitHash}"
}
