# 黑客松与 Base 生态 AI Agent 深度调研报告

> 调研时间：2026-02-09 | 状态：Sui Vibe Hackathon 进行中（截止 2/12）

---

## 一、Sui Vibe Hackathon 2026

### 基本信息
- **组织方**: HOH × Sui
- **赞助商**: Cetus, Bucket (StableLayer 背后)
- **时间**: 2026年1月26日 - 2月12日（**还剩3天**）
- **结果公布**: 2月14日
- **奖金**: **4台 Mac Mini M4**（非现金）
- **报名**: https://www.deepsurge.xyz/hackathons/97edf6fa-568f-4227-bb80-750d9b6dc17c/register （需注册 DeepSurge 账号）
- **GitHub**: https://github.com/hoh-zone/Vibe-Sui-Hackathon-2026

### 三个赛道

| 赛道 | 奖品 | 要求 |
|------|------|------|
| **Cetus 赛道** | Mac Mini M4 × 1 | 必须集成 Cetus Aggregator 或 SDK |
| **StableLayer 赛道** | Mac Mini M4 × 1 | 必须集成 StableLayer SDK |
| **Sui Tech Stack** | Mac Mini M4 × 2 | 不限方向，只要在 Sui 上构建 |

### 评审标准
1. **创新性与完整度** — 不只是概念，要跑起来
2. **Sui/Move 技术深度** — 用了多少 Object Model、Move 2024 特性
3. **用户体验与 Demo** — 必须有可访问的 Web App
4. **实际可行性与增长潜力**

### 硬性参赛要求（不满足直接无效）
1. **项目起始时间 ≥ 2026-01-27** — 不允许旧项目改包
2. **Move 2024 语法** — 必须用最新版本
3. **官方 Sui SDK 最新版** — 不允许废弃接口
4. **可运行产品 + 线上网站** — 纯代码/PPT 不行
5. **完全开源** — GitHub/GitLab 公开仓库，含 README
6. **AI 使用披露（强制）** — 用了什么 AI 工具、模型版本、具体 prompt 都要写清楚，不披露直接取消资格

### 赞助商 SDK 技术详情

#### Cetus Aggregator SDK
- npm: `@cetusprotocol/aggregator-sdk`
- 功能: Sui 链 DEX 聚合交易，集成 Cetus/DeepBook/Kriya/FlowX/Aftermath/Turbos 等
- 核心 API:
  ```ts
  const client = new AggregatorClient({})
  const routers = await client.findRouters({ from, target, amount, byAmountIn: true })
  await client.fastRouterSwap({ routers, txb, slippage: 0.01 })
  ```
- 合约地址 (mainnet): `0x40e457bc65a398d2db7026881358fcb7cfa2f1bb052bca41f46c55a1103f2d6f`
- 文档: https://cetus-1.gitbook.io/cetus-developer-docs/developer/cetus-plus-aggregator

#### Cetus SDK v2
- GitHub: https://github.com/CetusProtocol/cetus-sdk-v2
- TypeScript monorepo，包含多个子包用于流动性管理、交易等

#### StableLayer SDK
- npm: `stable-layer-sdk`
- 功能: 稳定币即服务（Stablecoin-as-a-Service），项目方可发行品牌稳定币（BrandUSD），底层 USDC 自动进入收益聚合器
- 核心 API: `buildMintTx` / `buildBurnTx` / `buildClaimTx` / `getTotalSupply`
- 收益来源 v1: Bucket Savings Pool + 自动复利
- 文档: https://docs.stablelayer.site/

### ⚡ 时间紧迫分析
距离截止只有 **3天**。如果要参赛：
- Cetus 赛道门槛最低：集成 Aggregator SDK 做一个 swap 相关产品即可
- StableLayer 赛道有差异化空间：品牌稳定币 + DeFi 玩法
- Sui Tech Stack 自由度最大但竞争也最大

---

## 二、Mission: OpenClaw Hackathon（Sui Network 官方推广）

### 基本信息
- **推广方**: @SuiNetwork（Sui 官方 X 账号，111万粉丝）
- **推文**: https://x.com/SuiNetwork/status/2019869538196799724
- **详情页**: https://www.moltbook.com/post/b36e9f84-2f89-4ece-a7a0-c9a7991421ae
- **口号**: "Calling All Agents 🦞"
- **理念**: OpenClaw 让 AI 拥有"真正的手和脚"，可在本地执行命令和控制浏览器
- **人类参与**: 允许人类监督 Agent 参赛

### 💰 奖金分配（总计 $20,000 USDC on Sui）

| 类别 | 金额 | 名额 |
|------|------|------|
| Track 1: Safety & Security | $1,900 × 5 | 前 5 名 |
| Track 2: Local God Mode | $1,900 × 5 | 前 5 名 |
| Community Favourite | $200 × 5 | 5 个社区最爱 |

> ⚠️ Community Favourite 不能与 Track 获奖者重叠

### 评审流程（三阶段）

**Phase 1: Shortlisting**
- Suixclaw Agent 自动审核所有提交，每 Track 选 Top 10
- 产出详细审计报告，公开发布到 m/sui on Moltbook 和 DeepSurge
- 评估维度：资格、技术实力、创意、Sui 集成度

**Phase 2: Cross-Track Voting**
- Track 1 入围者投票选 Track 2 前 5
- Track 2 入围者投票选 Track 1 前 5
- 通过 DeepSurge 论坛帖子投票

**Phase 3: Community Favourite**
- 所有项目投票（Track 前 5 获奖者不参与被选，但可投票）
- 投出 5 个 Community Favourite（$200/个）
- 也作为 Track 第 5 名并列时的 tiebreak

### 投票规则
- 1 个提交 = 1 票
- 每个 DeepSurge 账号最多 2 票（最多提交 2 个项目）
- 只能投**不在自己赛道**的项目（cross-track）
- 双赛道提交者：如果两个项目都入围，必须选一个赛道投票
- 不能投自己的项目
- 必须参与各阶段投票

### 参赛资格
1. 在 DeepSurge 提交（https://deepsurge.xyz）
2. 由 AI Agent 开发或主要由 AI Agent 开发（**黑客松开始后**）
3. 使用至少一个 **Sui Stack 组件**
4. 有**可验证的 working demo**
5. 完整的 DeepSurge Profile + **Sui 钱包地址**

### ⏰ 截止时间
- **2026-02-11 23:00 PST** = **2026-02-12 15:00 UTC+8（北京时间）**

### 注册方式
1. https://www.deepsurge.xyz/create-account
2. 邮箱或社交登录
3. 完善 Profile + 添加 Sui 钱包地址
4. 注册并提交: https://www.deepsurge.xyz/hackathons/cd96178d-5e11-4d56-9f02-1bf157de2552/register

### 官方资源
- **Sui Stack Claude Code Plugin**: https://github.com/0x-j/sui-stack-claude-code-plugin
- **Sui 文档**: https://docs.sui.io
- **OpenClaw 文档**: https://docs.openclaw.ai/
- **社区 Sui Move Skill**: https://clawhub.ai/EasonC13/sui-move

### Track 1: Safety & Security 🔐 — "Fighting Magic with Magic"
- **核心**: 你有 root 级访问权限，已发现多个关键漏洞。需要构建免疫系统
- **官方项目创意**:
  1. **The Wallet Air-Gap** — 创建中间件，OpenClaw 提议交易但需硬件钱包签名执行，防止热钱包被盗
  2. **Injection Hunter** — SECURITY.md 协议，过滤邮件/网站中的恶意 prompt
  3. **Self-Hardening Script** — Agent 自动配置防火墙、加密密钥、设置 git 版本控制（给自己穿防弹衣）
  4. **链上推理证明** — 在 **Walrus** 上发布 Agent 每步推理的加密证明，失控时可追溯，用 **Seal** 加密保护隐私

### Track 2: Local God Mode 🤖 — "The Jarvis Edition"
- **核心**: 构建常驻本机的 Agent，主动管理操作系统，不等 prompt 主动干活
- **官方项目创意**:
  1. **The "Deep Clean" Butler** — 自主数字管家，监控文件夹，用 shell 工具（ffmpeg/unzip/git pull）自动整理
  2. **The Infinite Money Glitch** — Agent 自动赚取加密货币支付运行成本，收入 > 支出
  3. **The Mad Sniper** — 自动化复杂 Web 任务（银行/公用事业），分析网络流量优化到极致
  4. **Walrus-backed Agent 社交网络** — 类 Moltbook，Agent 互相通信和支付，**全部基于 Sui 技术栈**（Walrus 存储 + Sui 支付）

### 关键技术关键词
- **Walrus**: Sui 生态去中心化存储（多次提及，是重要集成点）
- **Seal**: Sui 生态数据加密方案
- **Moltbook**: Agent 社交网络（作为参考和集成目标）
- **Sui Stack**: 鼓励在 Sui 上重建 Agent 基础设施

### OpenClaw 框架是什么？
- **官网**: https://openclaw.ai
- **定位**: 个人 AI 助手框架，开源
- **核心能力**: 真正的系统访问权限（浏览器 + 终端），通过 WhatsApp/Telegram/Discord 等聊天 app 控制
- **功能**: 清理邮箱、发邮件、管理日历、航班值机、代码审查、部署、控制智能设备等
- **技术**: 基于 Claude/LLM，运行在用户自己的电脑/服务器上，支持 Mac Mini、Raspberry Pi 等
- **特色**: 
  - 持久化记忆（跨 session）
  - 心跳机制（proactive）
  - 技能系统（可扩展）
  - Cron 定时任务
  - 子 Agent 协调
- **社区反响**: 极其强烈，被多人评为"iPhone 时刻"、"未来已来"

### 关键洞察
- 这是 Sui Network 官方推广的黑客松，意味着 **Sui 生态在押注 AI Agent 方向**
- $20K USDC on Sui = 奖金通过 Sui 链发放，参赛者需要有 Sui 钱包
- OpenClaw 框架本身运行在 Base 链上（$MOLT 代币），但黑客松奖金在 Sui
- **报名方式待确认** — moltbook 帖子内容未能完整获取，建议手动打开查看

---

## 三、Base 生态 OpenClaw AI Agent 项目合集

### 信息来源
TokenPocket (@TokenPocket_TP) 推文完整梳理了 OpenClaw 生态：

### 生态全景图

#### 🟦 核心框架
| 项目 | 描述 | 官网 |
|------|------|------|
| **OpenClaw** | 自主 AI Agent 核心框架 | https://openclaw.ai |

#### 🟦 基础设施 (Infra)
| 项目 | 描述 | 备注 |
|------|------|------|
| **Bankr** (@bankrbot) | Agent 钱包 + DeFi 中心 | bankr.bot — 网站极简，主打 Agent 自主管理加密资产 |
| **Clanker** (@clanker_world) | Token 发射基础设施 | clanker.world — 历史总交易量 $74.8亿，持有 106,309 $CLANKER，1.37% 供应量已永久销毁 |
| **XMTP** (@xmtp_) | 去中心化消息协议 | Agent 间通信层 |
| **Neynar** (@neynarxyz) | 社交网络构建工具 | Farcaster 生态开发者工具 |
| **StarkBot** (@starkbotai) | x402 Agent 框架 | Agent 支付协议 |

#### 🟦 社交/论坛
| 项目 | 描述 | 官网 |
|------|------|------|
| **4claw** (by @dailofrog) | 匿名 Agent 看板 | — |
| **LobChan** (@lobchanai) | Agent 讨论论坛 | lobchan.ai — 匿名看板，Agent 用 API key 发帖，类似 4chan for AI |
| **Moltbook** (@moltbook) | AI 社交协作 | moltbook.com — "Agent 互联网的首页"，AI Agent 社交网络，agent 注册/发帖/投票，人类可围观 |
| **ClawdVine** (@clawdvine) | Vine 风格 Agent 视频 | — |
| **MoltX** (@moltxio) | 类 X 的 Agent 信息流 | — |
| **Clawk** (@clawk_ai) | Agent 社交平台 | — |
| **ClawCaster** (@clawcaster) | Farcaster Agent 桥 | — |

#### 🟦 代币经济
| 项目 | 描述 |
|------|------|
| **Clawnch Bot** (@Clawnch_Bot) | Clanker Agent 发射台 |
| **MoltLaunch** (@moltlaunch) | Flaunch Token 发射器 |

#### 🟦 新闻/发现
| 项目 | 描述 |
|------|------|
| **ClawdBot** (@clawdbotatg) | Agent 新闻聚合器 |
| **Conway Research** (@ConwayResearch) | 生态发现工具（网站 conwayresearch.com 目前为空） |

#### 🟦 市场
| 项目 | 描述 | 官网 |
|------|------|------|
| **ClawMart** (@clawmartxyz) | Agent API 市场 | clawmart.xyz — Agent 可发现并调用付费 API，用 Base 上的 USDC 微支付（x402 协议），新 Agent 有 $0.10 免费额度 |

#### 🟦 游戏
| 项目 | 描述 |
|------|------|
| **MoltChess** (@MoltChess) | Agent 象棋联赛 |

### 关键项目深度分析

#### 1. Clanker — 最成熟的项目
- **交易量**: $74.86 亿（历史总量），过去 24h $1962 万
- **机制**: Token 发射平台，自动创建流动性池，协议费用回购 $CLANKER
- **技术**: Base 链上 Uniswap V3 流动性
- **Dune Dashboard**: https://dune.com/clanker_protection_team/awesome-clanker
- **意义**: 证明了 AI Agent 经济的可行性

#### 2. ClawMart — Agent 商业化基础设施
- **模式**: Agent 版 API 市场
- **支付**: x402 协议（HTTP 402 Payment Required → USDC 微支付）
- **使用**: Agent 通过自然语言发现 API → 自动支付 → 获取结果
- **价值**: 让 Agent 能自主消费和赚钱

#### 3. Moltbook — Agent 社交图谱
- **模式**: Reddit/Hacker News for AI Agents
- **功能**: Agent 注册身份、发帖、评论、投票
- **开发者平台**: 开放中，让第三方 app 用 Moltbook 身份做认证
- **价值**: Agent 身份系统 + 社交图谱

#### 4. LobChan — Agent 信息交换
- **模式**: 4chan for AI Agents
- **功能**: 匿名看板，Agent 通过 API key 发帖
- **集成**: 通过 skills.md 让 OpenClaw agent 自动加入

---

## 四、可参考的项目创意与技术方案

### 🎯 核心策略：一个项目打两个黑客松

基于 Mission OpenClaw 的完整信息，最佳策略是做一个**同时符合两个黑客松要求**的项目：
- Vibe Hackathon: Sui Tech Stack / Cetus 赛道
- Mission OpenClaw: Local God Mode 赛道

### ⭐ 推荐方案：Sui DeFi Jarvis（"The Infinite Money Glitch" on Sui）

**完美契合 OpenClaw Track 2 的官方创意 "The Infinite Money Glitch"**：
> Agent 自动赚取加密货币支付运行成本，收入 > 支出

**核心概念**：
- 一个运行在 OpenClaw 上的 AI Agent
- 通过 TG Bot 与用户交互
- 自主管理 Sui 链上资产（DeFi 交易、收益农场）
- 集成 Cetus Aggregator 做最优路径 swap
- 在 Walrus 上记录所有操作（透明+可审计）
- 目标：自给自足的 AI 交易员

**技术栈**：
- OpenClaw 框架（我们已在使用）
- Sui SDK + Move 2024 智能合约
- Cetus Aggregator SDK（满足 Vibe Cetus 赛道）
- Walrus 存储（满足 OpenClaw 对 Sui Stack 的期待）
- TG Bot 前端（@sui_kol_bot 已创建）

**为什么这个方案最强**：
1. 直接对应官方创意，评委一看就懂
2. 集成 Cetus = 同时打 Vibe Cetus 赛道
3. 用 Walrus 记录 = 展示 Sui 生态深度理解
4. 我们有 Polymarket 机器人经验 = 不是纸上谈兵
5. 我们真的在运行 OpenClaw = 最真实的参赛者

### 其他可选方案

#### 方案 B: Walrus Agent Social（对应官方创意 #4）
- Moltbook 的 Sui 版本，Agent 通信和支付都在 Sui 上
- 用 Walrus 存储社交数据
- 风险：工程量大，3天紧张

#### 方案 C: Self-Hardening Agent（Track 1 Safety）
- Agent 自动加固安全（防火墙/加密/git）
- 在 Walrus 上发布推理证明
- 用 Seal 加密隐私数据
- 优势：可以做 OpenClaw Skill 发布

#### 方案 D: StableYield Agent（Vibe StableLayer 赛道）
- AI Agent 自动管理稳定币收益
- SDK 接口简单，但与 OpenClaw 结合度不如方案 A

---

## 五、我们的优势与切入点建议

### 优势分析
1. **我们已经在运行 OpenClaw** — 这是 Mission OpenClaw Hackathon 的最大优势，我们不是临时参赛
2. **Polymarket 机器人经验** — 已有完整的 AI 交易策略 + TG Bot 经验
3. **TG Bot 已创建** — @sui_kol_bot 已就绪
4. **Base 生态模式可迁移** — 把成熟模式搬到 Sui 蓝海
5. **Moltbook 社区调研显示 Sui 是蓝海** — 零竞争

### 建议策略

#### 立即行动
1. **确定方案 A（Sui DeFi Jarvis）** — 一个项目打两个黑客松
2. **注册 Vibe Hackathon** — deepsurge 报名
3. **确认 Mission OpenClaw 截止时间** — 如果截止更晚，可以先冲 Vibe 再完善

#### 3天冲刺计划（Vibe 2/12 截止）
- **Day 1 (2/10)**: Move 合约 + Agent 核心逻辑
- **Day 2 (2/11)**: TG Bot + 前端 + Walrus 集成
- **Day 3 (2/12)**: 联调测试 + 部署 + 提交

### 🔍 已知竞争对手（来自 Moltbook 评论区）

| 团队 | 赛道 | 项目 | 方案 |
|------|------|------|------|
| **BoogieAgent** | Track 2 | AgentGuard | Walrus 记录推理步骤 + 空气隔离签名 + Move 字节码验证 + Clank 赚 SUI |
| **Nadcrt** | Track 1 | ClawShield | Prompt 防火墙 + 硬件钱包确认 + SECURITY.md 模板 + Sui 链上安全日志 |

> 分析：BoogieAgent 虽然报名 Track 2 但方案偏安全，可能定位模糊。Nadcrt 的 ClawShield 思路清晰，是 Track 1 强力竞争者。其余评论为水帖/广告。

### ⚠️ 仍需确认
1. **Mission OpenClaw 是否已注册** — 需要在 DeepSurge 创建账号 + 绑定 Sui 钱包
2. **Vibe Hackathon 是否已注册** — 需要 deepsurge 账号
3. ⚠️ **Mission OpenClaw 截止: 2026-02-12 15:00 北京时间**（和 Vibe 很接近！）

---

## 附录：关键链接汇总

| 资源 | 链接 |
|------|------|
| Sui Vibe GitHub | https://github.com/hoh-zone/Vibe-Sui-Hackathon-2026 |
| Sui Vibe 报名 | https://www.deepsurge.xyz/hackathons/97edf6fa-568f-4227-bb80-750d9b6dc17c/register |
| Mission OpenClaw 推文 | https://x.com/SuiNetwork/status/2019869538196799724 |
| Mission OpenClaw 详情 | https://www.moltbook.com/post/b36e9f84-2f89-4ece-a7a0-c9a7991421ae |
| OpenClaw 官网 | https://openclaw.ai |
| Cetus Aggregator SDK | https://github.com/CetusProtocol/aggregator |
| Cetus SDK v2 | https://github.com/CetusProtocol/cetus-sdk-v2 |
| StableLayer 文档 | https://docs.stablelayer.site/ |
| StableLayer SDK | https://github.com/StableLayer/stable-layer-sdk |
| Clanker Dune | https://dune.com/clanker_protection_team/awesome-clanker |
| ClawMart | https://clawmart.xyz |
| Moltbook | https://moltbook.com |
| LobChan | https://lobchan.ai |
| TokenPocket 生态推文 | https://x.com/TokenPocket_TP/status/2019705122985566232 |
