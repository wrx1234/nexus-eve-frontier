# 🏗️ Architecture - EVE Frontier AI Commander

## 项目概述

一个运行在 OpenClaw 上的自主 AI Agent，管理 EVE Frontier 中的 Smart Assemblies（智能建筑）。
通过 Telegram Bot 与用户交互，自主分析链上事件，优化门禁策略、防御配置和仓库管理。

## 系统架构

```
┌──────────────────────────────────────────────────────┐
│                    用户 (Telegram)                      │
│                  EVE Commander Bot                     │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│            AI Commander Core (TypeScript)              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ Assembly    │ │ Intelligence│ │   Defense    │    │
│  │ Manager    │ │  Analyst    │ │  Strategy    │    │
│  │ (assembly) │ │ (intel)     │ │ (defense)    │    │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘    │
│         │               │               │            │
│  ┌──────▼───────────────▼───────────────▼──────┐    │
│  │           Sui Chain Interface                │    │
│  │  - @mysten/sui SDK (TypeScript)              │    │
│  │  - Sui GraphQL API (读取)                     │    │
│  │  - Move 合约调用 (写入)                        │    │
│  │  - suix_queryEvents (事件监听)                 │    │
│  └──────────────────┬──────────────────────────┘    │
└─────────────────────┼────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  Sui Chain │ │ EVE World │ │  Walrus   │
│ (Move TX)  │ │ Contracts │ │ (Storage) │
│            │ │(Gate/SSU/ │ │  操作日志  │
│            │ │Turret/NWN)│ │  情报报告  │
└───────────┘ └───────────┘ └───────────┘
```

## 核心模块

### 1. Move 智能合约 (`contracts/`)
- **commander_config.move** - 共享配置 (AdminCap + CAuth witness + Dynamic Fields)
- **gate_commander.move** - Smart Gate AI 扩展 (多规则门禁 + 事件统计)

### 2. AI Agent 核心 (`agent/`)
- **main.ts** - 入口: 初始化钱包/扫描 Assembly/启动循环
- **wallet.ts** - Sui 钱包管理 (Ed25519 密钥对)
- **assembly.ts** - Assembly 管理 (上线/下线/元数据/扩展授权)
- **graphql.ts** - Sui GraphQL 查询 (按类型/按钱包/事件)
- **intelligence.ts** - 情报分析 (流量/威胁/趋势)
- **logger.ts** - Walrus 日志 (操作审计)

### 3. TG Bot (`bot/`)
- /status - Assembly 总览
- /gate - Gate 管理
- /storage - 仓库管理
- /defense - 防御策略
- /intel - 情报报告
- /fuel - 燃料状态
- /config - 配置管理

### 4. 前端 Dashboard (`frontend/`)
- Assembly 状态面板
- 事件时间线
- 情报可视化

## 技术栈
| 组件 | 技术 |
|------|------|
| 智能合约 | Move (Sui) |
| Agent | TypeScript (Node.js) |
| Sui 交互 | @mysten/sui SDK |
| EVE 数据 | @evefrontier/dapp-kit + GraphQL |
| 存储 | Walrus |
| Bot | grammY (Telegram) |
| 前端 | React + Vite |
| AI | OpenClaw / Claude API |
| 运行时 | OpenClaw Agent Framework |

## EVE Frontier Extension Pattern

```
1. 发布 eve_commander 包 (含 CAuth witness)
2. 调用 gate::authorize_extension<CAuth>(gate, owner_cap) 注册
3. Gate 自动启用扩展模式: jump 需要 JumpPermit
4. AI Agent 通过 gate_commander::issue_jump_permit 签发通行证
5. 所有操作发出事件 → Agent 监听 → 分析 → 调整策略
```

## 数据流

### 写入路径 (Agent → Chain)
```
AI 决策 → 构建 Transaction → signAndExecute → Move 函数调用
  ├── gate_commander::set_gate_config (更新规则)
  ├── gate_commander::issue_jump_permit (签发通行证)
  ├── assembly::online/offline (上下线)
  └── metadata::update_name/description (更新元数据)
```

### 读取路径 (Chain → Agent)
```
Sui GraphQL → 查询对象状态
  ├── objects(filter: {type: "world::gate::Gate"})
  ├── address.objects(filter: {type: "character::PlayerProfile"})
  └── getAssemblyWithOwner(id)

suix_queryEvents → 监听事件
  ├── JumpEvent (跳跃流量)
  ├── PermitIssuedEvent (通行证签发)
  ├── AccessDeniedEvent (拒绝记录)
  └── GateLinkedEvent / GateUnlinkedEvent
```
