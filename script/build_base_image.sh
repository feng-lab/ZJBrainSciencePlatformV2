set -euo pipefail

script_dir="$(dirname "$0")"
project_root="$(dirname "$script_dir")"
dockerfile_dir="${project_root}/dockerfile"

base_repo='zj-brain-science-platform-base'

docker build \
  --file "${dockerfile_dir}/base.Dockerfile" \
  --tag "$base_repo" \
  "$project_root"
