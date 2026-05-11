# Jupyter + Conda 环境搭建教程（macOS / Linux / Windows）

> 本教程目标：**为 AI 学习项目搭建一个干净、可复用、可隔离的 Python 环境**，并配置好 JupyterLab 与常用扩展。
>
> 适用场景：本仓库 `ai-learning/` 全程通用。

---

## 一、为什么用 Conda + Jupyter

| 痛点 | Conda 的解法 |
|------|-------------|
| 不同项目依赖版本冲突 | **虚拟环境隔离** |
| pip 装某些库报错（如 numpy/scipy 编译） | Conda 提供**预编译二进制包** |
| 需要切换 Python 版本（3.8 / 3.10 / 3.11） | `conda create -n xxx python=3.10` |
| 团队需要复现环境 | `environment.yml` 一键还原 |

**结论**：AI 学习强烈推荐 **Miniconda + JupyterLab**。

---

## 二、安装 Miniconda（推荐，比 Anaconda 轻量）

### macOS（Apple Silicon / Intel 通用）

```bash
# 1. 下载（Apple Silicon 选 arm64，Intel 选 x86_64）
# Apple Silicon (M1/M2/M3):
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
# Intel:
# curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh

# 2. 安装
bash Miniconda3-latest-MacOSX-arm64.sh

# 3. 重启终端，验证
conda --version
```

### Linux

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### Windows

去 https://docs.conda.io/en/latest/miniconda.html 下载 `.exe` 安装包，双击安装。安装后用 **Anaconda Prompt** 执行后续命令。

### 替代方案：Mamba（更快的 Conda）

```bash
conda install -n base -c conda-forge mamba
# 之后所有 conda 命令都可以换成 mamba，速度快 5~10 倍
```

---

## 三、配置国内镜像（强烈推荐，提速 10 倍）

### Conda 镜像（清华源）

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --set show_channel_urls yes
```

### pip 镜像（清华源）

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

验证：
```bash
conda config --show channels
pip config list
```

---

## 四、创建 AI 学习专用环境

```bash
# 1. 新建环境（Python 3.10 是兼容性最好的版本）
conda create -n ai-learning python=3.10 -y

# 2. 激活环境
conda activate ai-learning

# 3. 安装核心数据科学包
conda install -c conda-forge numpy pandas scipy matplotlib seaborn scikit-learn jupyterlab -y

# 4. 安装深度学习框架（按需选择）
# CPU 版本：
pip install torch torchvision torchaudio
# 或者 TensorFlow:
# pip install tensorflow

# 5. 其他常用工具
pip install ipywidgets tqdm rich plotly
```

> ⚠️ macOS Apple Silicon 用户装 PyTorch 直接 `pip install torch`，自动支持 MPS GPU 加速。

---

## 五、把环境注册成 Jupyter 内核（关键！）

不做这一步，JupyterLab 看不到你的环境。

```bash
# 在已激活的 ai-learning 环境中
pip install ipykernel
python -m ipykernel install --user --name=ai-learning --display-name "Python (ai-learning)"
```

验证：
```bash
jupyter kernelspec list
# 应该能看到 ai-learning
```

之后在 Notebook 右上角可以切换到 `Python (ai-learning)` 内核。

---

## 六、启动 JupyterLab

```bash
# 进入项目根目录
cd /Users/fletcherli/CodeBuddy/20260228220331/ai-learning

# 激活环境
conda activate ai-learning

# 启动
jupyter lab
```

浏览器会自动打开 `http://localhost:8888/lab`。

### 后台运行（可选）

```bash
nohup jupyter lab --no-browser --port=8888 > jupyter.log 2>&1 &
```

---

## 七、推荐 JupyterLab 扩展

```bash
# Git 集成（在 Lab 里直接 commit/diff）
pip install jupyterlab-git

# 代码补全 / 语法跳转 / 文档悬浮（LSP）
pip install jupyterlab-lsp python-lsp-server

# Notebook diff 工具（让 Git 比较 .ipynb 更友好）
pip install nbdime
nbdime config-git --enable --global

# 黑色主题、变量查看器等可在 JupyterLab 内 Extension Manager 中搜索安装
```

---

## 八、导出可复现的环境文件

### 导出
```bash
conda env export --from-history > environment.yml   # 推荐：只记录显式安装的包
# 或完整导出（含所有依赖版本）：
conda env export > environment.full.yml
```

### 还原（在新机器上）
```bash
conda env create -f environment.yml
conda activate ai-learning
```

### 推荐放进 `ai-learning/environment.yml`

最小可运行示例：
```yaml
name: ai-learning
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy
  - pandas
  - scipy
  - matplotlib
  - seaborn
  - scikit-learn
  - jupyterlab
  - ipykernel
  - pip
  - pip:
      - torch
      - torchvision
      - tqdm
```

---

## 九、VS Code / CodeBuddy 中使用 Jupyter（更推荐）

如果你不想用浏览器界面，IDE 内置体验更好：

1. 装好 conda 环境（同上）
2. 在 IDE 中打开 `.ipynb` 文件
3. 右上角"选择内核" → 选 `Python (ai-learning)`
4. 直接在编辑器里写代码、运行 cell、看图表

**好处**：和你现有项目同一个窗口，Git 集成更顺，AI 助手也能直接帮你写。

---

## 十、常见问题（FAQ）

### Q1：`conda activate` 报错 "CommandNotFoundError"
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda init zsh   # 或 bash
# 重启终端
```

### Q2：JupyterLab 里看不到我新建的环境
没注册内核。回到第五节执行 `python -m ipykernel install ...`。

### Q3：装包巨慢
1. 先配镜像（第三节）
2. 用 `mamba` 替代 `conda`
3. 简单的包用 `pip` 也行（不要 conda + pip 装同一个包）

### Q4：M 系列 Mac 装包失败
- 优先用 `conda-forge` 频道：`conda install -c conda-forge xxx`
- 实在不行用 `pip`

### Q5：怎么删除环境
```bash
conda deactivate
conda env remove -n ai-learning
jupyter kernelspec uninstall ai-learning
```

### Q6：每次开终端都自动进 base 环境，烦人
```bash
conda config --set auto_activate_base false
```

---

## 十一、5 分钟极速搭建（懒人版）

```bash
# 一条龙
conda create -n ai-learning python=3.10 -y
conda activate ai-learning
conda install -c conda-forge numpy pandas matplotlib seaborn scikit-learn jupyterlab ipykernel -y
python -m ipykernel install --user --name=ai-learning --display-name "Python (ai-learning)"
cd /Users/fletcherli/CodeBuddy/20260228220331/ai-learning
jupyter lab
```

完事，开撸。

---

## 十二、目录建议

```
ai-learning/
├── environment.yml              # 环境定义（建议提交到 Git）
├── 02-阶段2-机器学习与深度学习/
│   ├── 笔记/                    # Markdown 理论
│   ├── 代码/                    # .ipynb 实战
│   │   └── 01_鸢尾花分类入门.ipynb
│   └── 资料/
│       └── Jupyter与Conda环境搭建.md  ← 你现在看的就是它
```

理论 `.md` + 实战 `.ipynb` + 一键还原的 `environment.yml`，AI 学习项目最佳实践。
