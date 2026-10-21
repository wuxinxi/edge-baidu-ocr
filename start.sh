#!/usr/bin/env bash

# 根目录便捷启动入口：转发到 scripts/start.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/scripts/start.sh" "$@"
