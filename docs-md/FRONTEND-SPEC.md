# 🎨 前端落地页设计规格

## 页面类型
单页 Landing Page，展示项目 + 实时数据

## 整体风格
- 深色主题（科技/DeFi 风格）
- 主色：Sui 蓝 (#4DA2FF) + 渐变紫
- 辅色：绿色（盈利）、红色（亏损）
- 字体：现代无衬线（Inter / Space Grotesk）

---

## Section 1: Hero
**内容：**
- Logo + 项目名：**Sui DeFi Jarvis**
- 副标题：*The Infinite Money Glitch — An AI Agent that earns its own keep on Sui*
- 简介：一行中文 + 一行英文
  - "自主 AI 交易员，在 Sui 链上自动做 DeFi 赚钱"
  - "Autonomous AI Agent for DeFi on Sui — powered by OpenClaw"
- CTA 按钮：
  - [💬 Try on Telegram] → t.me/sui_kol_bot
  - [📂 View Source] → github.com/wrx1234/sui-hackathon
- 背景：粒子动画 / 网格线条

## Section 2: Features（4 个卡片横排）
| 图标 | 标题 | 描述 |
|------|------|------|
| 🤖 | AI-Powered Trading | Agent 分析市场数据，自主决策交易策略，24/7 全自动运行 |
| 🔄 | Cetus Optimal Routing | 集成全部 Sui DEX（Cetus/DeepBook/Kriya/FlowX/Turbos），找最优 swap 路径 |
| 📝 | Walrus Transparency | 每笔交易、每个决策完整记录在 Walrus 去中心化存储，公开可审计 |
| 🛡️ | Risk Management | 可配置止损/限额，异常行为自动暂停，Agent 钱包与主钱包隔离 |

## Section 3: Live Dashboard
**实时数据面板**（可以是模拟数据用于 Demo，或真实 API 拉取）

左侧：
- 💰 Agent 钱包余额（SUI / USDC / 其他 token）
- 📊 总资产价值 (USD)
- 📈 今日 P&L（盈亏金额 + 百分比）

右侧：
- 最近 5 笔交易列表
  - 时间 | 操作 | Token | 金额 | 状态
  - 例: 14:22 | Swap | 50 SUI → 75 USDC | ✅
- [查看 Walrus 完整日志 →] 链接

## Section 4: Proof（真实案例）
**标题**: "Battle-Tested: Real Results"

展示卡片：
- 📊 **Polymarket Bot** 
  - $1,000 → $3,500 in < 1 week (+250%)
  - Running on OpenClaw since [日期]
  - [Verify on-chain →] 链接
- 💡 文字说明：
  - "This is not a concept. We've been running autonomous trading bots profitably. Sui DeFi Jarvis brings this proven approach to the Sui ecosystem."

## Section 5: Architecture（简化架构图）
**视觉化的系统架构**

```
[You] ──TG──→ [🤖 AI Agent] ──→ [Sui Chain]
                   │                    │
              [OpenClaw]          [Cetus DEX]
                   │                    │
              [Strategy]          [Walrus Logs]
```

用 SVG 或 CSS 动画表现数据流方向

## Section 6: Sui Stack（赞助商/集成展示）
**标题**: "Built on the Sui Stack"

横排 Logo + 名称 + 一句话：
| Logo | 名称 | 集成说明 |
|------|------|----------|
| 🐋 | Cetus | DEX Aggregator — 最优交易路径 |
| 🐘 | Walrus | 去中心化存储 — 不可篡改操作日志 |
| 🔐 | Seal | 密钥加密管理 |
| 🦞 | OpenClaw | AI Agent 框架 |
| 📱 | Moltbook | Agent 社交情报网 |
| ⛓️ | Sui | 底层区块链 |

## Section 7: Footer
- GitHub | DeepSurge | Telegram Bot | AI Disclosure
- "Built with 🤖 by AI agents, supervised by humans"
- Mission OpenClaw Hackathon 2026

---

## 技术实现
- **框架**: React + Vite（或纯 HTML/CSS/JS 如果更快）
- **部署**: Walrus Sites（去中心化）或 Vercel（快速）
- **数据**: API 拉取 Agent 状态，或静态 demo 数据
- **响应式**: 必须适配移动端

## 设计素材需求（给 Xuan）
1. Logo — Sui DeFi Jarvis（一个 AI 机器人 + Sui 水波元素？）
2. Hero 背景图 — 科技/区块链风格
3. 功能图标 — 如果不用 emoji 的话需要 SVG 图标
4. 配色确认 — 深色 + Sui 蓝为主？
