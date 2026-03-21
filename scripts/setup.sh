#!/bin/bash
# Sui DeFi Jarvis — 一键安装脚本

echo "🤖 Sui DeFi Jarvis Setup"
echo "========================"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js v18+"
    exit 1
fi
echo "✅ Node.js $(node -v)"

# 安装依赖
echo "📦 Installing dependencies..."
npm install

# 创建 .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env from .env.example"
    echo "⚠️  Please edit .env with your config"
fi

# 创建日志目录
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Sui wallet private key"
echo "  2. Run the agent:  npm start"
echo "  3. Run the bot:    npm run bot"
echo "  4. Or both:        npm start & npm run bot"
