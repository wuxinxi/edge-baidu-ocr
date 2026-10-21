#!/usr/bin/env bash

# 根目录便捷入口：转发到 scripts/download.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/scripts/download.sh" "$@"
