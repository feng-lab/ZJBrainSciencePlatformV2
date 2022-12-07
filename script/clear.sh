set -euo pipefail

script_dir="$(dirname "$0")"
project_root="$(dirname "$script_dir")"

cd "$project_root"

docker compose down --rmi all --remove-orphans

docker system prune

docker image rm zj-brain-science-platform-base