# CLAUDE.md - Sui DeFi Jarvis 架构文档

## 项目概述

Sui DeFi Jarvis ("The Infinite Money Glitch") — 自主 AI DeFi Agent，运行在 Sui 区块链上。参加 Sui Vibe Hackathon，覆盖 4 个赛道：Cetus、StableLayer、Sui Tech Stack、Mission: OpenClaw。

**技术栈：** TypeScript (Agent) / Python (TG Bot) / Move (智能合约) / React+Vite+Tailwind v4 (前端)

**部署：**
- GitHub: https://github.com/wrx1234/sui-hackathon
- 前端: https://wrx1234.github.io/sui-hackathon/
- Bot: @SuiJarvisBot (token: 7825340169:AAEL5DRdPL6E_zR6-eOSu0ttw-AxaHr0yzI)
- Sui testnet package: 0x737a73b3a146d45694c341a22b62607e5a6e6b6496b91156217a7d2c91f7e65d

---

## 目录结构

```
hackathon-sui/
├── agent/              # TypeScript — 核心 DeFi 逻辑
│   ├── wallet.ts       # Sui 钱包管理（密钥对、余额、转账）
│   ├── swap.ts         # Cetus DEX 聚合器交易
│   ├── social.ts       # Twitter/X 社交狙击（监控+回复）
│   └── logger.ts       # Walrus 去中心化日志存储
├── bot/                # Python — Telegram Bot
│   ├── jarvis_bot.py   # 主 bot（python-telegram-bot v20+ async）
│   ├── i18n.py         # 国际化引擎 _(key, uid, **kwargs)
│   └── locales/        # JSON 语言文件
│       ├── en.json     # 英文（70+ keys）
│       └── cn.json     # 中文
├── contracts/          # Move — 智能合约
│   ├── Move.toml
│   └── sources/
│       └── vault.move  # 链上金库（已部署 testnet）
├── frontend/           # React+Vite+Tailwind v4
│   ├── src/
│   │   ├── App.tsx     # 主页面（9 模块，双语 lang state）
│   │   ├── index.css   # Tailwind v4 @theme + glass-button CSS
│   │   ├── components/ui/  # 14 个组件文件
│   │   └── lib/utils.ts    # cn() 工具函数
│   └── vite.config.ts  # base: '/sui-hackathon/', @/ alias
├── tests/              # 测试（33 单元 + 24 E2E）
├── docs/               # GitHub Pages 部署目录（vite build → cp dist/* docs/）
└── CLAUDE.md           # 本文件
```

## 模块依赖图

```
Frontend (React)
    └── 纯静态，无后端依赖

Bot (Python)
    ├── i18n.py → locales/*.json
    ├── 模拟数据层（gen_whale_data, gen_signals 等，纯英文）
    └── 需要 HTTPS_PROXY=http://172.18.0.1:7890

Agent (TypeScript)
    ├── wallet.ts → @mysten/sui (Sui SDK)
    ├── swap.ts → Cetus Aggregator API
    ├── social.ts → Twitter API (dry-run, 无 API key)
    └── logger.ts → Walrus API

Contracts (Move)
    └── vault.move → 独立部署，Agent 调用
```

## 关键约束 ⚠️

### 前端
- **Tailwind v4**: 无 tailwind.config，用 `@theme {}` 在 index.css 注册变量
- **禁止 shadcn CLI**: 安装会被 SIGKILL（内存不够），所有组件手动编写
- **禁止 Next.js 语法**: 无 `'use client'`、`next/image`、`Image` imports
- **npm 分批安装**: 每次 2-3 个包，避免 SIGKILL
- **framer-motion whileInView**: 无头 Chrome 不触发，截图只显示 Hero

### Bot
- **启动方式**: `HTTPS_PROXY=http://172.18.0.1:7890 setsid python3 jarvis_bot.py`
- **数据层纯英文**: gen_whale_data, gen_signals, gen_pool_data, STRATEGIES 全英文
- **i18n**: `_(key, uid, **kwargs)` 函数，JSON locale，fallback: user_lang → en → key
- **python-telegram-bot v20+**: async，`forward_from` 已废弃用 `forward_origin`

### 部署
- **GitHub Pages**: `docs/` 目录，vite build 后 `cp -r dist/* docs/`
- **git push 需代理**: `git config http.proxy "http://172.18.0.1:7890"`
- **GitHub token**: (see MEMORY.md, do not commit)

## 前端组件清单 (src/components/ui/)

| 文件 | 来源 | 用途 |
|------|------|------|
| spotlight.tsx | Aceternity | Hero 光效 |
| splite.tsx | @splinetool | 3D 模型懒加载 |
| glass-button.tsx | 自定义 | 毛玻璃按钮 |
| feature-hover.tsx | 21st.dev | 8格 Features |
| feature-steps.tsx | 21st.dev | Social Sniper 步骤 |
| bento-grid.tsx | shadcn/magicui | Architecture 卡片 |
| category-list.tsx | 21st.dev | StableLayer |
| features-2.tsx | 21st.dev | Security 三卡 |
| financial-dashboard.tsx | 21st.dev | Dashboard |
| button.tsx | shadcn | CVA button |
| card.tsx | shadcn | Card 组件 |

## 修改指南

1. **改前端**: 先读 `App.tsx` 了解 9 模块结构和双语 `t(en, cn)` 模式
2. **改 Bot**: 先读 `i18n.py` 了解翻译系统，数据层保持纯英文
3. **改 Agent**: 先读 `ARCHITECTURE.md` 了解完整系统设计
4. **加依赖**: 分批 `npm install`（2-3个），别一次装太多
5. **部署**: `npx vite build && cp -r dist/* ../docs/ && git add -A && git commit && git push`

## 禁止事项 🚫

- 不要安装 shadcn CLI（`npx shadcn@latest`）
- 不要用 Next.js 语法（`'use client'`, `next/image`）
- 不要一次 npm install 超过 3 个包
- 不要在 bot 数据层写中文（用 locale 系统）
- 不要用 `nohup` 单独启动 bot（必须 `setsid`）
