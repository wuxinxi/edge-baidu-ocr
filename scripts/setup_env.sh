#!/usr/bin/env bash

# ==============================================================================
# edge-ocr: 虚拟环境一键初始化脚本 (.venv)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

VENV_DIR="${PROJECT_ROOT}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"
PLATFORM_PYTHON_VERSION="3.12"

echo "=========================================================="
echo "  🛠️  edge-ocr: 虚拟环境初始化 (.venv)"
echo "=========================================================="

if [ -d "${VENV_DIR}" ]; then
    if [ ! -x "${VENV_PYTHON}" ]; then
        echo "错误: 已有 .venv 缺少可用解释器，请先检查该目录。"
        exit 1
    fi
    EXISTING_PYTHON_VERSION="$("${VENV_PYTHON}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    echo "提示: 检测到已有环境 Python ${EXISTING_PYTHON_VERSION}。"
fi

UV_BIN="$(command -v uv || echo "/Users/sensiwu/.local/bin/uv")"

if [ -x "${UV_BIN}" ]; then
    echo "⚡ 检测到 uv (${UV_BIN})，创建虚拟环境..."
    if [ ! -d "${VENV_DIR}" ]; then
        "${UV_BIN}" venv --python "${PLATFORM_PYTHON_VERSION}" "${VENV_DIR}"
    fi
    echo "📦 安装后端与模型下载依赖..."
    "${UV_BIN}" pip install -r "${PROJECT_ROOT}/backend/requirements.txt" --python "${VENV_PYTHON}"
else
    if [ ! -d "${VENV_DIR}" ]; then
        if ! command -v python3.12 >/dev/null 2>&1; then
            echo "错误: 未找到 uv 或 python3.12。"
            exit 1
        fi
        echo "使用 Python 3.12 创建虚拟环境..."
        python3.12 -m venv "${VENV_DIR}"
    fi
    echo "📦 升级 pip 并安装依赖..."
    "${VENV_PYTHON}" -m pip install --upgrade pip
    "${VENV_PYTHON}" -m pip install -r "${PROJECT_ROOT}/backend/requirements.txt"
fi

echo "=========================================================="
echo "  ✅ .venv 初始化完成: ${VENV_PYTHON}"
echo "=========================================================="
