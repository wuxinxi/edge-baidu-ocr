#!/usr/bin/env bash

# ==============================================================================
# edge-ocr: 一键启动脚本 (FastAPI:8084 + Vite:5176)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

VENV_DIR="${PROJECT_ROOT}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

if [ ! -f "${VENV_PYTHON}" ]; then
    echo "⚠️  未找到本地虚拟环境 ${VENV_DIR}，正在自动执行 setup_env.sh..."
    bash "${SCRIPT_DIR}/setup_env.sh"
fi

# 生成内置测试 PDF（如尚未生成）
if [ ! -f "${PROJECT_ROOT}/testset/unlimited_ocr_benchmark_3pages.pdf" ]; then
    echo "📄 正在生成内置多页测试 PDF 样本..."
    "${VENV_PYTHON}" "${SCRIPT_DIR}/create_sample_pdf.py"
fi

echo "=========================================================="
echo "  📄  正在启动 edge-ocr (Unlimited-OCR 端侧工作台)..."
echo "  💻 运行环境: $("${VENV_PYTHON}" --version)"
echo "=========================================================="

echo "⚡ 启动双进程开发模式 (FastAPI:8084 + Vite:5176)..."

# 启动 FastAPI 后端
"${VENV_PYTHON}" -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8084 --reload &
BACKEND_PID=$!

# 启动 Vite 前端
cd "${PROJECT_ROOT}/frontend"
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装前端依赖 (npm install)..."
    npm install
fi
npm run dev -- --port 5176 &
FRONTEND_PID=$!

echo ""
echo "🎉 edge-ocr 服务启动成功！"
echo "   🔗 前端界面 (Vue 3):    http://localhost:5176"
echo "   🔗 后端接口 (FastAPI):  http://localhost:8084"
echo "   📖 交互式 API 文档:     http://localhost:8084/docs"
echo ""
echo "按 Ctrl+C 即可退出所有服务..."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
