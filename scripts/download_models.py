#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edge-ocr: Unlimited-OCR 与 Apple Silicon (Mac M1) 衍生模型一键下载工具
- 覆盖百度官方原版 baidu/Unlimited-OCR 与社区 Apple Silicon MLX / CoreML / GGUF 量化版
- 支持双下载源：ModelScope (魔搭社区) 与 Hugging Face (默认配置 hf-mirror.com 国内高速镜像)
- 智能跳过：检测到本地 checkpoints/<model_key> 已存在有效权重文件时自动跳过，支持断点续传
- 环境守护：强制在项目本地 .venv 虚拟环境中运行
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional

# ---------------------------------------------------------
# 虚拟环境自动守护：确保强制使用项目 .venv 运行
# ---------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_VENV_PYTHON = _PROJECT_ROOT / ".venv" / "bin" / "python"

if _VENV_PYTHON.exists() and Path(sys.executable).resolve() != _VENV_PYTHON.resolve():
    try:
        import huggingface_hub
        import rich
    except ImportError:
        print(f"⚡ [环境守护] 检测到未在 .venv 中运行，自动切换解释器: {_VENV_PYTHON}")
        os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------
# Unlimited-OCR 模型矩阵配置（针对 Mac M1 Pro 16GB 专项优化）
# ---------------------------------------------------------
MODELS_DOWNLOAD_CONFIG: Dict[str, dict] = {
    "unlimited-ocr-mlx-4bit": {
        "name": "Unlimited-OCR MLX 4-bit (Apple Silicon 极速版)",
        "param_size": "3B (激活 500M)",
        "download_size": "~2.1GB",
        "category": "Mac M1 16GB 首选 · MLX 4-bit",
        "repo_id": "sahilchachra/unlimited-ocr-mxfp4-mlx",
        "ms_repo_id": None,
        "recommended_m1": True,
        "engine": "mlx-vlm",
        "desc": "专为 Apple M 系列芯片转换的 4-bit MLX 权重，内存仅占 ~2.8GB，M1 Pro 16GB 极速流畅运行",
    },
    "unlimited-ocr-mlx-8bit": {
        "name": "Unlimited-OCR MLX 8-bit (Apple Silicon 均衡无损版)",
        "param_size": "3B (激活 500M)",
        "download_size": "~3.1GB",
        "category": "Mac M1 16GB 推荐 · MLX 8-bit",
        "repo_id": "sahilchachra/unlimited-ocr-mxfp8-mlx",
        "ms_repo_id": None,
        "recommended_m1": True,
        "engine": "mlx-vlm",
        "desc": "8-bit MLX 权重，复杂表格与密集小字号公式精度接近 BF16，16GB 统一内存轻松承载",
    },
    "unlimited-ocr": {
        "name": "baidu/Unlimited-OCR (百度官方 BF16 原版)",
        "param_size": "3B (激活 500M)",
        "download_size": "~6.6GB",
        "category": "官方原版基线 · R-SWA 32K",
        "repo_id": "baidu/Unlimited-OCR",
        "ms_repo_id": "baidu/Unlimited-OCR",
        "recommended_m1": False,
        "engine": "transformers",
        "desc": "百度官方开源原版 Safetensors 权重 (OmniDocBench v1.6 93.92%)，含 R-SWA 与 DeepEncoder 源码",
    },
    "unlimited-ocr-mlx-bf16": {
        "name": "Unlimited-OCR MLX BF16 (Apple Silicon 全精度版)",
        "param_size": "3B (激活 500M)",
        "download_size": "~6.5GB",
        "category": "Mac 全精度对照 · MLX BF16",
        "repo_id": "pcuenq/Unlimited-OCR-bf16-mlx",
        "ms_repo_id": None,
        "recommended_m1": False,
        "engine": "mlx-vlm",
        "desc": "全精度 BF16 MLX 转换版，适合 16GB+ 内存对比量化前后极限精度差异",
    },
    "unlimited-ocr-mlx-coreml": {
        "name": "Unlimited-OCR MLX + CoreML 混合加速包",
        "param_size": "3B (激活 500M)",
        "download_size": "~3.9GB",
        "category": "CoreML ANE 编码 + MLX 解码",
        "repo_id": "FluidInference/unlimited-ocr-mlx-coreml",
        "ms_repo_id": None,
        "recommended_m1": False,
        "engine": "coreml-mlx",
        "desc": "使用 CoreML 跑 DeepEncoder 视觉编码 + 8-bit MLX 跑 R-SWA 解码器，支持 16 页单次连跑",
    },
}

CHECKPOINTS_DIR = _PROJECT_ROOT / "checkpoints"


def is_model_downloaded(model_key: str) -> bool:
    """检查模型目录是否存在有效权重文件"""
    target_dir = CHECKPOINTS_DIR / model_key
    if not target_dir.exists():
        return False

    weight_patterns = ["*.safetensors", "*.bin", "*.gguf", "*.f16"]
    for pat in weight_patterns:
        if list(target_dir.glob(pat)) or list(target_dir.glob(f"**/{pat}")):
            return True
    return False


def get_downloaded_size_mb(model_key: str) -> float:
    """计算本地模型目录已下载文件大小 (MB)"""
    target_dir = CHECKPOINTS_DIR / model_key
    if not target_dir.exists():
        return 0.0
    total_bytes = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())
    return round(total_bytes / (1024 * 1024), 1)


def download_from_modelscope(ms_repo_id: str, target_dir: Path) -> bool:
    """从魔搭社区下载"""
    if not ms_repo_id:
        return False
    try:
        from modelscope import snapshot_download
        print(f"🇨🇳 [ModelScope] 正在从魔搭社区直连拉取: {ms_repo_id}")
        target_dir.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            model_id=ms_repo_id,
            local_dir=str(target_dir),
        )
        return True
    except Exception as e:
        print(f"❌ [ModelScope] 下载失败: {e}")
        return False


def download_from_huggingface(repo_id: str, target_dir: Path, use_mirror: bool = True) -> bool:
    """从 HuggingFace (或国内镜像源) 下载"""
    try:
        from huggingface_hub import snapshot_download
        if use_mirror and "HF_ENDPOINT" not in os.environ:
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        endpoint = os.environ.get("HF_ENDPOINT", "https://huggingface.co")
        print(f"🌐 [Hugging Face] 正在拉取 (源: {endpoint}): {repo_id}")
        target_dir.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_dir),
            endpoint=endpoint,
        )
        return True
    except Exception as e:
        print(f"❌ [Hugging Face] 源 {os.environ.get('HF_ENDPOINT', 'official')} 下载异常: {e}")
        if use_mirror and os.environ.get("HF_ENDPOINT") == "https://hf-mirror.com":
            print("🔄 正在尝试切换至 Hugging Face 官方直连源 (https://huggingface.co)...")
            os.environ["HF_ENDPOINT"] = "https://huggingface.co"
            try:
                from huggingface_hub import snapshot_download
                snapshot_download(
                    repo_id=repo_id,
                    local_dir=str(target_dir),
                    endpoint="https://huggingface.co",
                )
                return True
            except Exception as e2:
                print(f"❌ [Hugging Face Official] 下载失败: {e2}")
        return False


def download_model(model_key: str, source: str = "hf", force: bool = False) -> bool:
    """下载单个指定模型"""
    if model_key not in MODELS_DOWNLOAD_CONFIG:
        print(f"❌ 未知模型 key: {model_key}")
        print(f"💡 可选模型 key: {', '.join(MODELS_DOWNLOAD_CONFIG.keys())}")
        return False

    cfg = MODELS_DOWNLOAD_CONFIG[model_key]
    target_dir = CHECKPOINTS_DIR / model_key

    print(f"\n=======================================================")
    print(f"📦 开始处理: {cfg['name']}")
    print(f"📊 参数规模: {cfg['param_size']} | 预计体积: {cfg['download_size']}")
    print(f"📁 目标目录: {target_dir}")
    print(f"=======================================================")

    if not force and is_model_downloaded(model_key):
        size_mb = get_downloaded_size_mb(model_key)
        print(f"✅ 检测到本地已存在有效权重 ({size_mb} MB)，自动跳过 (如需重下请加 --force)")
        return True

    success = False
    if source == "ms" and cfg.get("ms_repo_id"):
        success = download_from_modelscope(cfg["ms_repo_id"], target_dir)
        if not success:
            print("⚠️ ModelScope 拉取未成功，自动回退至 Hugging Face...")
            success = download_from_huggingface(cfg["repo_id"], target_dir)
    else:
        success = download_from_huggingface(cfg["repo_id"], target_dir)
        if not success and cfg.get("ms_repo_id"):
            print("⚠️ Hugging Face 拉取未成功，自动回退至 ModelScope...")
            success = download_from_modelscope(cfg["ms_repo_id"], target_dir)

    if success:
        print(f"🎉 成功完成: {model_key} 权重就绪！保存位置: {target_dir}")
    else:
        print(f"💥 下载失败: {model_key}")

    return success


def print_model_list():
    """打印模型矩阵状态表格"""
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()
        table = Table(
            title="edge-ocr: Unlimited-OCR 模型矩阵与本地状态 (Mac M1 Pro 16GB 适配)",
            border_style="bright_blue",
        )
        table.add_column("Key (--model)", style="cyan", no_wrap=True)
        table.add_column("模型名称", style="white")
        table.add_column("参数规模", style="magenta")
        table.add_column("体积", style="yellow")
        table.add_column("定位与引擎", style="green")
        table.add_column("本地状态", style="bold")

        for key, cfg in MODELS_DOWNLOAD_CONFIG.items():
            downloaded = is_model_downloaded(key)
            if downloaded:
                size_mb = get_downloaded_size_mb(key)
                status = f"[green]✅ 已就绪 ({size_mb}MB)[/green]"
            else:
                status = "[red]❌ 未下载[/red]"
            table.add_row(
                key,
                cfg["name"],
                cfg["param_size"],
                cfg["download_size"],
                cfg["category"],
                status,
            )

        console.print(table)
        console.print(
            "\n💡 [bold cyan]Mac M1 Pro (16GB) 快捷下载命令:[/bold cyan]\n"
            "  1. 下载 M1 极速 4-bit MLX 版 (~2.1GB，推荐): [yellow]./download.sh --model unlimited-ocr-mlx-4bit[/yellow]\n"
            "  2. 下载 M1 无损 8-bit MLX 版 (~3.1GB):       [yellow]./download.sh --model unlimited-ocr-mlx-8bit[/yellow]\n"
            "  3. 下载百度官方 BF16 原版 (~6.6GB):          [yellow]./download.sh --model unlimited-ocr[/yellow]\n"
            "  4. 一键下载 M1 推荐版:                       [yellow]./download.sh --recommended[/yellow]\n"
        )
    except ImportError:
        print(f"{'Key':<26} | {'体积':<8} | {'状态'}")
        print("-" * 55)
        for key, cfg in MODELS_DOWNLOAD_CONFIG.items():
            downloaded = is_model_downloaded(key)
            status = "✅ 已就绪" if downloaded else "❌ 未下载"
            print(f"{key:<26} | {cfg['download_size']:<8} | {status}")


def main():
    parser = argparse.ArgumentParser(description="edge-ocr: Unlimited-OCR 模型一键下载工具")
    parser.add_argument("--list", action="store_true", help="查看所有支持的模型及本地下载状态")
    parser.add_argument("--model", type=str, help="指定要下载的模型 key (如 unlimited-ocr-mlx-4bit 或 unlimited-ocr)")
    parser.add_argument("--recommended", action="store_true", help="下载 Mac M1 Pro 16GB 首选轻量模型 (unlimited-ocr-mlx-4bit)")
    parser.add_argument("--all", action="store_true", help="下载全部模型")
    parser.add_argument("--source", choices=["hf", "ms"], default="hf", help="首选下载源: hf (HuggingFace) 或 ms (ModelScope)")
    parser.add_argument("--force", action="store_true", help="强制重新下载")

    args = parser.parse_args()

    if args.list:
        print_model_list()
        return

    if args.model:
        download_model(args.model, source=args.source, force=args.force)
    elif args.recommended:
        download_model("unlimited-ocr-mlx-4bit", source=args.source, force=args.force)
    elif args.all:
        for key in MODELS_DOWNLOAD_CONFIG.keys():
            download_model(key, source=args.source, force=args.force)
    else:
        print_model_list()


if __name__ == "__main__":
    main()
