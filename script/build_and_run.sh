set -euo pipefail

script_dir="$(dirname "$0")"
project_root="$(dirname "$script_dir")"

bash "${script_dir}/build_base_image.sh"

mkdir -p ~/log/ZJBrainSciencePlatform/app
mkdir -p ~/log/ZJBrainSciencePlatform/mysql
mkdir -p ~/data/ZJBrainSciencePlatform/file
mkdir -p ~/mysql/ZJBrainSciencePlatform/data

docker compose --file "${project_root}/docker-compose.yaml" \
  up --detach --build
