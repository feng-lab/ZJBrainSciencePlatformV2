# 之江实验室 Brain Science 平台

## 依赖版本

* Python >= 3.11
* Docker & Docker Compose

详细依赖版本见 [pyproject.toml](./pyproject.toml) 文件。

## 启动应用

### 1 配置开发环境

#### 1.1 安装 Poetry

本项目使用 Poetry 管理项目依赖和虚拟环境，需要 [安装 Poetry](https://python-poetry.org/docs/#installation)。

```shell
# Linux, macOS, Windows (WSL)
curl -sSL https://install.python-poetry.org | python3 -

# Windows (Powershell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 1.2 安装依赖

```shell
poetry install --without alembic --sync
```

### 2 启动 MySQL 数据库

#### 2.1 设置启动参数

```shell
# Linux bash
export DEBUG_MODE='True'
export DATABASE_URL='mysql+pymysql://zjlab:zjlab2022@localhost:8100/zj_brain_science_platform'
export DATABASE_CONFIG='{}'
```

```shell
# Windows PowerShell
$env:DEBUG_MODE='True'
$env:DATABASE_URL='mysql+pymysql://zjlab:zjlab2022@localhost:8100/zj_brain_science_platform'
$env:DATABASE_CONFIG='{}'
```

#### 2.2 启动数据库

建议使用 Docker

```shell
python ./build.py up-database
```

#### 2.3 迁移数据库

```shell
python ./build.py run-alembic-bash

alembic upgrade head
```

### 3 启动应用

#### 3.1 开发环境

```shell
python -m uvicorn app.main:app --reload
```

在浏览器中打开链接 http://127.0.0.1:8000 

#### 3.2 Docker Compose 部署

```shell
python ./build.py up-backend
```