# 之江实验室 Brain Science 平台

## 依赖版本

* Python >= 3.10
* FastAPI >= 0.86

## 启动应用

### 本地启动（开发）

#### 1. 创建虚拟环境

方法1：Anaconda / Miniconda

```shell
conda create -n ZJBrainSciencePlatform python=3.10
conda activate ZJBrainSciencePlatform
```

方法2：virtualenv

```shell
python -V # 确认 Python 版本高于 3.10 
python -m venv .venv

source ./.venv/bin/activate # Linux bash
.\.venv\Scripts\Activate.ps1 # Windows PowerShell
```

#### 2. 安装依赖

```shell
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 3. 启动应用

```shell
export DEBUG_MODE=True # Linux bash
$env:DEBUG_MODE=True # Windows PowerShell

python -m uvicorn app.main:app --reload
```

在浏览器中打开链接 http://127.0.0.1:8000 

### Docker Compose（部署）

```shell
docker compose up -d
```