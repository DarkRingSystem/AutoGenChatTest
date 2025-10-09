#!/bin/bash

# 修复 libgobject-2.0-0 错误的一键脚本

echo "🔧 开始修复 libgobject-2.0-0 错误..."
echo ""

# 检查是否安装了 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未检测到 Homebrew"
    echo "📦 正在安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew 已安装"
fi

echo ""
echo "📦 安装系统依赖..."

# 安装系统依赖
brew install glib cairo pango gdk-pixbuf libffi gobject-introspection gtk+3

echo ""
echo "🐍 安装 Python 依赖..."

# 切换到 backend 目录
cd "$(dirname "$0")/backend" || exit 1

# 安装 Python 依赖
pip3 install weasyprint mammoth PyGObject

echo ""
echo "✅ 验证安装..."

# 验证安装
echo -n "检查 GLib: "
python3 -c "import gi; print('✅ OK')" 2>/dev/null || echo "❌ 失败"

echo -n "检查 weasyprint: "
python3 -c "import weasyprint; print('✅ OK')" 2>/dev/null || echo "❌ 失败"

echo -n "检查 mammoth: "
python3 -c "import mammoth; print('✅ OK')" 2>/dev/null || echo "❌ 失败"

echo ""
echo "📚 检查库文件..."

# 获取 Homebrew 路径
BREW_PREFIX=$(brew --prefix)
echo "Homebrew 安装在: $BREW_PREFIX"

# 检查库文件
if ls "$BREW_PREFIX"/lib/libgobject-2.0* 1> /dev/null 2>&1; then
    echo "✅ 找到 libgobject-2.0 库:"
    ls "$BREW_PREFIX"/lib/libgobject-2.0*
else
    echo "❌ 找不到 libgobject-2.0 库"
    echo "尝试重新安装 GLib..."
    brew reinstall glib
fi

echo ""
echo "🔧 环境变量设置..."
echo "请将以下内容添加到你的 shell 配置文件 (~/.zshrc 或 ~/.bash_profile):"
echo ""
echo "export DYLD_LIBRARY_PATH=\"$BREW_PREFIX/lib:\$DYLD_LIBRARY_PATH\""
echo "export PKG_CONFIG_PATH=\"$BREW_PREFIX/lib/pkgconfig:\$PKG_CONFIG_PATH\""
echo "export GI_TYPELIB_PATH=\"$BREW_PREFIX/lib/girepository-1.0:\$GI_TYPELIB_PATH\""
echo ""

echo "✅ 修复完成！"
echo ""
echo "📝 下一步："
echo "1. 使用 ./start.sh 启动后端服务"
echo "2. 上传 DOCX 文件测试"
echo ""
echo "如果问题仍然存在，请查看 docs/FIX_LIBGOBJECT_ERROR.md"

