# Docker配置
export DOCKER_USERNAME='caitaozjlab'
export DOCKER_TOKEN='dckr_pat_3vHgyUohktPfh6AkThPE88CUzIs'
export DOCKER_STACK_NAME='platform'
export COMPOSE_PROJECT_NAME='platform'

# 镜像配置
export IMAGE_REPO_PREFIX='zjbs'
export CACHE_IMAGE_TAG='redis:7-alpine'
export PYTHON_VERSION='3.11'
export POETRY_VERSION='1.8.2'
export PIP_INDEX_URL='https://pypi.tuna.tsinghua.edu.cn/simple'

# 目录结构
configDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
projectDir="$(cd -- "${configDir}/../.." &>/dev/null && pwd)"
dockerfileDir="$(cd -- "${projectDir}/deploy/dockerfile" &>/dev/null && pwd)"
imageVersionDir="$(cd -- "${projectDir}/deploy/image-version" &>/dev/null && pwd)"
composeDir="$(cd -- "${projectDir}/deploy/compose" &>/dev/null && pwd)"
export configDir projectDir dockerfileDir imageVersionDir composeDir

# SSH配置
export SSH_CONFIG_HOST=''

# 工具函数
generate-tag-version() {
  local dateTime gitHash
  dateTime="$(date +'%Y%m%d-%H%M%S')"
  gitHash="$(git -C "$projectDir" rev-parse --short=8 HEAD)"
  echo "${dateTime}-${gitHash}"
}
