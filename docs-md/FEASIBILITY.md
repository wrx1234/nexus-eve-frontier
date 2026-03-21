# 🔍 技术可行性分析

## 真实案例背书

> **我们已经用 OpenClaw 运行的 Polymarket 机器人，在不到一周的时间里将 $1,000 变成了 $3,500（+250%）。**
> 这个成绩在 Polymarket 链上完全可查可验证。

这证明了：
1. AI Agent 自主交易是**真实可行**的
2. 我们有**实战经验**，不是纸上谈兵
3. Sui DeFi Jarvis 本质上就是把这套系统**从 Polygon 搬到 Sui**，同时加强透明性和安全性

---

## 各功能技术可行性评估

### ✅ 能做 — 有成熟依赖

| 功能 | 成熟度 | 依赖 | 说明 |
|------|--------|------|------|
| **Sui 钱包管理** | ⭐⭐⭐⭐⭐ | `@mysten/sui` (TS) / `pysui` (Python v0.95) | 官方 SDK，Ed25519 密钥对，完全成熟 |
| **查询余额/链上数据** | ⭐⭐⭐⭐⭐ | `@mysten/sui` GraphQL + gRPC | 官方支持，文档完善 |
| **Token Swap (Cetus)** | ⭐⭐⭐⭐⭐ | `@cetusprotocol/aggregator-sdk` | **最成熟的组件**。一行代码找最优路径，集成了 Cetus/DeepBook/Kriya/FlowX/Aftermath/Turbos 等全部 Sui DEX，npm 直接安装 |
| **TG Bot 交互** | ⭐⭐⭐⭐⭐ | `python-telegram-bot` / `aiogram` | 我们 Polymarket Bot 已在用，完全成熟 |
| **AI 决策引擎** | ⭐⭐⭐⭐⭐ | OpenClaw / Claude API | 我们已在运行，持久记忆+心跳+主动决策 |

### ✅ 能做 — 有依赖但需适配

| 功能 | 成熟度 | 依赖 | 说明 |
|------|--------|------|------|
| **LP 流动性管理** | ⭐⭐⭐⭐ | `@cetusprotocol/sui-clmm-sdk` | Cetus 集中流动性 SDK，有完整 API（add/remove/claim fees），需要理解 tick range 参数 |
| **收益耕作 (Farming)** | ⭐⭐⭐⭐ | `@cetusprotocol/farms-sdk` | Cetus 官方 Farming SDK，stake LP token 赚额外奖励 |
| **限价单** | ⭐⭐⭐⭐ | `@cetusprotocol/limit-sdk` | Cetus 限价单 SDK，可以设定价格自动成交 |
| **Walrus 日志存储** | ⭐⭐⭐ | Walrus HTTP API (Publisher) | Walrus 提供 HTTP API 上传 blob，通过 `PUT /v1/blobs` 存储数据。**但文档结构有变化**，需要测试当前可用的 publisher 端点。Testnet publisher: `https://publisher.testnet.walrus.space` |
| **Moltbook 集成** | ⭐⭐⭐ | Moltbook REST API | 我们已有账号和凭据，可以发帖/评论/搜索，API 基本稳定 |

### ⚠️ 有风险 — 需要评估

| 功能 | 成熟度 | 问题 | 替代方案 |
|------|--------|------|----------|
| **Seal 密钥加密** | ⭐⭐ | Seal 是较新的 Sui 组件，SDK 可能不完善，文档稀少 | **替代：本地 AES-256 加密 + 链上存加密后的 hash**。Demo 中可以展示概念，用简化实现 |
| **Move 智能合约** | ⭐⭐⭐ | 我们没有 Move 开发经验，3天学习+开发有压力 | **简化：用最小合约（vault 存取 + 事件日志），不做复杂逻辑。主要逻辑放在 Agent 端** |
| **自动套利** | ⭐⭐⭐ | Sui 上 DEX 流动性和价差是否足够套利？需要实测 | **替代：做趋势跟踪而非套利。我们 Polymarket 策略就是趋势判断，直接迁移** |
| **前端 Dashboard** | ⭐⭐⭐ | 3天内做前端时间很紧 | **简化：用 Vite + React 做一个极简单页面，主要展示资产+交易记录。或直接用 Walrus Sites 部署静态页** |

### ❌ 不做 — 时间不够或不现实

| 功能 | 原因 | 处理 |
|------|------|------|
| 多链监控 | 超出 MVP 范围 | 写进 Roadmap 即可 |
| Agent 付费购买 API 服务 | 需要第三方服务配合 | 写进 Roadmap |
| Token 发行/做市 | 法律风险 + 复杂度高 | 不做 |

---

## 技术架构决策

基于可行性分析，**调整后的技术方案**：

### 语言选择
- **主体用 TypeScript**（不是 Python）
  - 原因：Cetus SDK 全部是 TS，Sui 官方 SDK 也是 TS 优先，pysui 虽然有但和 Cetus 不通
  - TG Bot 用 `grammy`（TS 版 telegram bot 框架）或 `node-telegram-bot-api`
  - 这样 Sui 交互 + Cetus 交互 + Bot 都在一个语言里，不用跨语言桥接
- **Move 合约**用 Move 2024（必须）
- **AI 决策**通过 HTTP 调用 Claude API（或通过 OpenClaw）

### 核心依赖清单

```json
{
  "@mysten/sui": "最新版",
  "@cetusprotocol/aggregator-sdk": "swap 最优路径",
  "@cetusprotocol/sui-clmm-sdk": "LP 管理",
  "@cetusprotocol/farms-sdk": "收益耕作",
  "grammy": "TG Bot 框架 (TS)",
  "walrus-sdk": "或直接 HTTP API 调用 publisher"
}
```

### 简化版 Move 合约
```
vault.move:
  - deposit(coin) → 存入资金
  - withdraw(amount) → 取出资金（需 Agent 签名）
  - emit TradeEvent → 记录交易事件
```
不做复杂策略逻辑在链上，所有智能决策在 Agent 端。

---

## 3天开发计划（修订版）

### Day 1 (2/10) — 基础设施 + 核心交易
| 时间 | 任务 | 交付 |
|------|------|------|
| 上午 | 安装 Sui CLI + 初始化 TS 项目 | 可编译运行的项目 |
| 上午 | 钱包模块：生成/导入/查余额 | wallet.ts |
| 下午 | Cetus Aggregator 集成：swap 功能 | swap.ts + 实测 testnet swap |
| 下午 | TG Bot 框架：/start /balance /swap | bot 可响应 |
| 晚上 | 简单 Move 合约：vault deposit/withdraw | 合约部署到 testnet |

### Day 2 (2/11) — AI 策略 + Walrus + 完善
| 时间 | 任务 | 交付 |
|------|------|------|
| 上午 | AI 策略引擎：市场分析 → 交易决策 | strategy.ts |
| 上午 | Walrus 集成：操作日志上传 | logger.ts + 可查询的日志 |
| 下午 | LP 管理基础功能 | liquidity.ts |
| 下午 | TG Bot 完善：/strategy /history /log | 完整 Bot |
| 晚上 | 风控模块：限额/止损 | risk.ts |

### Day 3 (2/12) — 测试 + 部署 + 提交
| 时间 | 任务 | 交付 |
|------|------|------|
| 上午 | 端到端测试（testnet） | 完整流程跑通 |
| 上午 | 前端简单页面（资产+交易记录） | 可访问的 URL |
| 下午 | 录制 Demo 视频 | 2-3分钟演示 |
| 下午 | 提交 DeepSurge（⏰ 15:00 截止） | 提交成功 |

---

## 风险和对策

| 风险 | 概率 | 对策 |
|------|------|------|
| Cetus SDK API 变化 | 低 | SDK 文档完善，npm 最新版 |
| Walrus publisher 不可用 | 中 | 备选：直接在 Sui 上 emit 事件存日志 |
| Move 合约 bug | 中 | 合约尽量简单，复杂逻辑放 Agent 端 |
| Testnet 资金不够 | 低 | Sui faucet 免费领测试币 |
| 3天时间不够 | 高 | **用 multi-agent 并行开发**，合约/Agent/Bot 同时推进 |
| Seal SDK 不好用 | 高 | 用本地加密替代，概念性展示即可 |
