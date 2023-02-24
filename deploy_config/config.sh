# Docker配置
export DOCKER_USERNAME=${DOCKER_USERNAME:-zjlabbrainscience}
export DOCKER_TOKEN=${DOCKER_TOKEN:-dckr_pat_2PDLJLgitGJ6zztpsVtGVgGCz3s}
export DOCKER_STACK=${DOCKER_STACK:-platform}

# 镜像配置
export IMAGE_REPO_PREFIX=${IMAGE_REPO_PREFIX:-zj-brain-science-platform}
export BASE_IMAGE_REPO=${BASE_IMAGE_REPO:-"${DOCKER_USERNAME}/${IMAGE_REPO_PREFIX}-base"}
export BASE_IMAGE_VERSION=${BASE_IMAGE_VERSION:-eb96912}
export PYTHON_VERSION=${PYTHON_VERSION:-3.11}
export POETRY_VERSION=${POETRY_VERSION:-1.3.2}
export PIP_INDEX_URL=${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}
