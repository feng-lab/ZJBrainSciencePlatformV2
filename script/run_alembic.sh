set -euo pipefail

script_dir="$(dirname "$0")"
project_root="$(dirname "$script_dir")"

docker compose --file "${project_root}/docker-compose.yaml" \
  up --detach --no-recreate database

bash "${script_dir}/build_base_image.sh"

docker compose --file "${project_root}/docker-compose.yaml" \
  run --build --rm alembic \
  bash
