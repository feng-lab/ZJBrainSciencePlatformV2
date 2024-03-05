# 之江实验室 Brain Science 平台

## 依赖版本

* Python 3.11
* Linux / WSL 操作系统
* Docker & Docker Compose
* [Poetry](https://python-poetry.org/docs/#installation)
* [GitHub CLI](https://cli.github.com/)

详细依赖版本见 [pyproject.toml](./pyproject.toml) 文件。

## 1 配置开发环境

### 1.1 安装依赖

```shell
poetry env use <Python 3.11 路径>
poetry install --sync
```

### 1.2 启动 MySQL 和 Redis 依赖

如果在 Linux 环境下，或者有 WSL，可以直接运行

```bash
bash compose.sh
# 首次启动，或者更新 alembic 迁移命令后，需要运行下面的命令
bash compose.sh alembic
```

如果是在纯 Windows 环境下，可以手动运行配置命令

```powershell
$env:DATABASE_URL = "mysql+pymysql://zjlab:zjlab2022@database:3306/zj_brain_science_platform"
$env:PLATFORM_IMAGE_TAG = "caitaozjlab/zjbs-platform"
$env:DATABASE_IMAGE_TAG = "caitaozjlab/zjbs-database"
$env:CACHE_IMAGE_TAG = "redis:7.0"
docker compose -f .\deploy\compose\dev.compose.yaml up -d --force-recreate database cache
# 首次启动，或者更新 alembic 迁移命令后，需要运行下面的命令
docker compose -f .\deploy\compose\dev.compose.yaml run --rm platform alembic upgrade head
```

### 1.4 启动应用

```shell
poetry run python -m uvicorn app.main:app --reload
```

在浏览器中打开链接 http://127.0.0.1:8000/docs

## 2 部署

### 2.1 GitHub CI

项目推送到 GitHub 会触发自动构建，运行下面的命令打开最近的构建结果

```shell
gh run view --web
```

### 2.2 测试和环境部署

GitHub CI 报告中有最新的镜像版本，记下来。Linux / WSL 环境下运行

```bash
bash build.sh -T -d on platform <镜像版本>
```

`-T` 部署到测试环境，`-P` 部署到生产环境。
