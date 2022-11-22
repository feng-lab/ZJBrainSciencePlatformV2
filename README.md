# 之江实验室 Brain Science 平台

## 依赖版本

* Python >= 3.10

其他依赖版本见 requirements.txt 文件

## 启动应用

### 1 配置开发环境

#### 1.1 创建虚拟环境

方法1：Anaconda / Miniconda

```shell
conda create -n ZJBrainSciencePlatform python=3.10
conda activate ZJBrainSciencePlatform
```

方法2：virtualenv

```shell
python -V # 确认 Python 版本高于 3.10 
python -m venv .venv

# Linux bash
source ./.venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 1.2 安装依赖

```shell
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
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
docker compose up -d --build database
```

#### 2.3 迁移数据库

```shell
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
docker-compose up -d --build
```