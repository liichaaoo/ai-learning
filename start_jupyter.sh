#!/bin/bash
# 一键启动 JupyterLab（在项目根目录下）
# 用法：bash start_jupyter.sh

cd "$(dirname "$0")"
echo "🚀 启动 JupyterLab ..."
echo "📂 项目目录：$(pwd)"
echo "🌐 启动后会自动打开浏览器，地址通常是 http://localhost:8888/lab"
echo "⛔ 关闭服务：在此终端按两次 Ctrl+C"
echo ""
python3 -m jupyter lab
