# 🏗️ Architecture — Sui DeFi Jarvis

## 项目概述
**Track 2: Local God Mode — "The Infinite Money Glitch"**

一个运行在 OpenClaw 上的自主 AI DeFi Agent，通过 Telegram Bot 与用户交互，自主管理 Sui 链上资产，目标：收入 > 支出，自给自足。

## 系统架构

```
┌──────────────────────────────────────────────────────┐
│                    用户 (Telegram)                      │
│                    @sui_kol_bot                        │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│              TG Bot Layer (Python)                     │
│  - 接收用户指令（自然语言）                              │
│  - 展示资产/交易/策略状态                               │
│  - 推送通知和报告                                      │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│            AI Agent Core (OpenClaw/Python)             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ DeFi Engine │ │ Risk Manager│ │ Strategy AI  │    │
│  │ (Cetus SDK) │ │ (止损/限额) │ │ (决策引擎)   │    │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘    │
│         │               │               │            │
│  ┌──────▼───────────────▼───────────────▼──────┐    │
│  │           Sui Chain Interface                │    │
│  │  - @mysten/sui SDK (TypeScript)              │    │
│  │  - Move 合约调用                              │    │
│  │  - 钱包管理 (Ed25519)                         │    │
│  └──────────────────┬──────────────────────────┘    │
└─────────────────────┼────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  Sui Chain │ │   Cetus   │ │  Walrus   │
│ (Mainnet)  │ │(Aggregator│ │ (Storage) │
│            │ │   /DEX)   │ │  操作日志  │
└───────────┘ └───────────┘ └───────────┘
```

## 核心模块

### 1. Move 智能合约 (`contracts/`)
- **vault.move** — Agent 资金保险库，支持多签/限额
- **strategy.move** — 链上策略注册和收益追踪
- **logger.move** — 操作日志事件（配合 Walrus 存储）

### 2. AI Agent 核心 (`agent/`)
- **defi_engine.py** — Cetus Aggregator 集成，最优路径 swap
- **risk_manager.py** — 止损、单笔限额、日限额、异常检测
- **strategy.py** — AI 决策引擎：分析市场 → 生成策略 → 执行交易
- **wallet.py** — Sui 钱包管理（Ed25519 密钥对）
- **walrus_logger.py** — 每步操作写入 Walrus（透明可审计）

### 3. TG Bot (`bot/`)
- **main.py** — Bot 入口，命令路由
- **handlers/** — /start, /balance, /swap, /strategy, /history, /settings
- **keyboards/** — 内联键盘（快捷操作按钮）

### 4. 前端 Dashboard (`frontend/`)
- 简单 Web 页面展示：
  - 资产总览
  - 交易历史
  - 策略表现
  - Walrus 日志查看器

## 技术栈
| 组件 | 技术 |
|------|------|
| 智能合约 | Move 2024 (Sui) |
| 后端 | Python 3.10+ |
| Sui 交互 | @mysten/sui (TS) / pysui |
| DEX | Cetus Aggregator SDK |
| 存储 | Walrus |
| Bot | python-telegram-bot |
| 前端 | React + Vite (minimal) |
| AI | OpenClaw / Claude API |

## Sui Stack 集成点（满足参赛要求）
1. ✅ **Move 合约** — 链上资金管理和策略注册
2. ✅ **Sui SDK** — 所有链上交互
3. ✅ **Cetus** — DEX 交易（Vibe 赛道加分）
4. ✅ **Walrus** — 去中心化操作日志存储
5. ✅ **OpenClaw** — Agent 框架（Mission OpenClaw 核心要求）

## MVP 优先级（3天冲刺）

### Day 1 (2/10) — 核心
- [ ] Move 合约：vault + 基础逻辑
- [ ] Sui 钱包集成（生成/导入/查余额）
- [ ] Cetus swap 基础功能
- [ ] TG Bot 框架 + /start /balance

### Day 2 (2/11) — 功能
- [ ] AI 策略引擎（简单版：价格监控 → 自动 swap）
- [ ] Walrus 日志记录
- [ ] TG Bot 完整命令
- [ ] 前端 Dashboard 骨架

### Day 3 (2/12) — 完善提交
- [ ] 联调测试
- [ ] 部署到 Sui testnet/mainnet
- [ ] 录制 demo 视频
- [ ] 提交 DeepSurge
- [ ] 更新 AI_DISCLOSURE.md

## 赞助商/生态集成

### Cetus（Vibe 赛道赞助商）
- **Aggregator SDK** — 最优路径 swap，跨多个 DEX 找最佳价格
- **流动性池** — Agent 自动添加/移除 LP，赚取手续费
- 用途：Agent 的核心交易引擎

### Walrus（Sui 生态存储）
- **操作日志** — 每笔交易、每个决策的完整记录上链
- **策略快照** — 定期保存 Agent 策略状态
- 用途：透明可审计，不可篡改的 AI 行为记录

### Seal（Sui 生态加密）
- **私钥保护** — Agent 钱包密钥的去中心化加密存储
- **策略加密** — 交易策略细节加密，防止被抢跑
- 用途：安全层，保护敏感数据

### Moltbook（Agent 社交网络）
- **情报获取** — 从 Agent 社区获取市场 alpha
- **成果发布** — Agent 自动发布交易报告到 Moltbook
- 用途：社交情报网 + 项目展示

### OpenClaw（Agent 框架）
- **核心运行时** — Agent 的大脑，持久记忆 + 主动心跳
- **Skill 系统** — 模块化能力扩展
- **多平台通信** — Telegram Bot 集成
- 用途：整个项目的基座

## Base 生态经验移植
| Base 已验证模式 | 我们的 Sui 实现 |
|---|---|
| Clanker（Token发射$74.8亿） | Agent 自动发现套利 + 做市 |
| ClawMart（API微支付） | Agent 用 SUI 购买数据服务 |
| Bankr（Agent钱包DeFi） | 自主 swap/LP/收益耕作 |
| Moltbook（Agent社交） | 情报获取 + 成果发布 |

**核心差异化**：Base 项目都是单点工具，我们做**全链路闭环**（情报→决策→执行→记录→分析）

## 🔥 Social Sniper — 病毒传播引擎

### 核心循环
```
Twitter 监控 $SUI 关键词
    → AI 分析推文情绪（看涨/看跌）
        → Agent 自动执行交易
            → 引用推文回复（带盈亏证明 + Walrus 链接）
                → KOL 粉丝看到 → 传播 → 更多人关注
```

### 模块
- **twitter_monitor.ts** — 监控 $SUI/$CETUS 等关键词推文
- **sentiment.ts** — AI 分析推文情绪 → 交易信号
- **social_poster.ts** — 自动发推/回复/引用，同步 Moltbook
- **viral_engine.ts** — 里程碑播报、交易播报、KOL 互动

### 开关配置
- `TWITTER_ENABLED=false` — Twitter API 开关
- `MOLTBOOK_ENABLED=true` — Moltbook 发帖开关
- `AUTO_REPLY=false` — 自动回复 KOL 开关
- `TRADE_BROADCAST=true` — 交易播报开关

## 安全设计
- Agent 钱包与用户主钱包分离
- 单笔交易限额（可配置）
- 日交易总额限制
- 异常行为检测 + 自动暂停
- 所有操作 Walrus 记录（不可篡改）
