#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 激活虚拟环境
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    echo "🔧 激活虚拟环境..."
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✅ 虚拟环境已激活: $(which python)"
else
    echo "⚠️  未找到虚拟环境，使用系统 Python"
fi

# 获取 Homebrew 路径
BREW_PREFIX=$(brew --prefix 2>/dev/null || echo "/opt/homebrew")

# 设置 Homebrew 库路径，让 weasyprint 能找到系统依赖
export DYLD_LIBRARY_PATH="$BREW_PREFIX/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$BREW_PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
export GI_TYPELIB_PATH="$BREW_PREFIX/lib/girepository-1.0:$GI_TYPELIB_PATH"

# 启动后端服务
echo "🚀 启动后端服务..."
echo "📦 Homebrew 路径: $BREW_PREFIX"
echo "📦 DYLD_LIBRARY_PATH: $DYLD_LIBRARY_PATH"
echo "📦 Python: $(which python)"
python main.py

