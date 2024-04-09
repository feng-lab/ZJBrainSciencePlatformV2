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

MySQL in Docker 在 Windows 下配置比较麻烦，因此放在 Linux / WSL 环境中

```bash
bash compose.sh
# 首次启动，或者更新 alembic 迁移命令后，需要运行下面的命令
bash compose.sh alembic
```

### 1.3 启动应用

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

### 2.2 测试和生产环境部署

GitHub CI 报告中有最新的镜像版本，记下来。Linux / WSL 环境下运行

```bash
bash build.sh -T -d on platform <镜像版本>
```

`-T` 部署到测试环境，`-P` 部署到生产环境。

## 3 迁移数据库

更新数据库模块定义（orm.py）后，需要用 alembic 迁移数据库。

### 3.1 生成 alembic 迁移文件

本地运行

```bash
alembic revision --autogenerate -m '<更新信息>'
```

alembic 会自动对比新旧数据库定义，自动生成迁移脚本，放在 `./alembic/versions` 目录下。

### 3.2 生成 SQL 迁移脚本

为了适配自定义的迁移操作，避免 alembic 自动操作的风险，本项目不使用 alembic 自动执行迁移操作的功能。

运行

```bash
alembic upgrade --sql '<前一个版本号>:<最新版本号>' > ./alembic/sql/upgrade/<前一个版本号>_<最新版本号>.sql
alembic downgrade --sql '<最新版本号>:<前一个版本号>' > ./alembic/sql/downgrade/<最新版本号>_<前一个版本号>.sql
```

生成升级和降级两个 SQL 脚本，并根据需求修改这两个脚本。

alembic 迁移文件和 SQL 脚本都需要提交到 git 中。

### 3.3 执行 SQL 迁移脚本

可以通过 `mycli` 等工具连接到本地、测试和生产环境的数据库，执行 SQL 脚本完成迁移。

```bash
cat './alembic/sql/upgrade/<前一个版本号>:<最新版本号>.sql' | mycli mysql://zjlab:zjlab2022@localhost:8100/zj_brain_science_platform
```

测试和生产环境数据库，只需要更换 IP 即可。
