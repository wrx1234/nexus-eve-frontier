# 🚀 EVE Frontier AI Commander - Hackathon 改造计划

## 项目概念

**EVE Frontier AI Commander** - 一个运行在 OpenClaw 上的自主 AI Agent，帮助玩家管理 EVE Frontier 中的 Smart Assemblies（智能建筑），包括：
- 🚪 **Smart Gate 管理** - AI 控制跳跃门权限（基于部落/声望/付费）
- 📦 **Smart Storage Unit 管理** - AI 驱动的自动交易站/仓库
- 🔫 **Smart Turret 管理** - AI 优化炮台目标优先级
- ⚡ **Network Node 监控** - 燃料/能量自动管理
- 📊 **全局情报** - 通过链上事件监控跳跃流量、击杀记录、库存变动

## 技术栈

| 组件 | 原项目 (SuiJarvis) | 新项目 (EVE Commander) |
|------|-------------------|----------------------|
| 智能合约 | vault.move (资金管理) | gate_extension.move + ssu_extension.move (Assembly 扩展) |
| 链交互 | @mysten/sui + Cetus SDK | @mysten/sui + @evefrontier/dapp-kit |
| Agent 核心 | strategy.ts (DeFi 策略) | commander.ts (Assembly 管理策略) |
| 风控 | risk.ts (止损/限额) | defense.ts (防御策略/威胁评估) |
| 数据源 | Cetus 价格 | Sui GraphQL + EVE Events (JumpEvent 等) |
| 存储 | Walrus (交易日志) | Walrus (操作日志 + 情报报告) |
| Bot | Telegram (@sui_kol_bot) | Telegram (EVE Commander Bot) |
| 前端 | React Dashboard | React Assembly Dashboard |

---

## Step 1: 文件复用分析

### ✅ 可直接复用的文件

| 文件 | 原因 |
|------|------|
| `agent/wallet.ts` | Sui 钱包管理逻辑完全通用（Ed25519、余额查询） |
| `agent/logger.ts` | Walrus 日志系统不变，仅改 action 类型 |
| `frontend/src/components/ui/*` | UI 组件库（button, card, bento-grid 等）通用 |
| `frontend/src/lib/utils.ts` | 工具函数通用 |
| `frontend/vite.config.ts` | 构建配置通用 |
| `frontend/tsconfig*.json` | TypeScript 配置通用 |
| `tools/ai-logger.py` | AI 日志工具通用 |
| `tests/wallet.test.ts` | 钱包测试通用 |
| `tests/logger.test.ts` | 日志测试通用 |

### ✏️ 需要修改的文件

| 文件 | 修改内容 |
|------|---------|
| `agent/main.ts` | 启动流程改为 EVE Commander，接入 Assembly 管理 |
| `agent/risk.ts` → `agent/defense.ts` | 从 DeFi 风控改为防御威胁评估 |
| `agent/strategy.ts` → `agent/commander.ts` | 从 DeFi 策略改为 Assembly 管理策略 |
| `agent/social.ts` | 从推文播报改为 EVE 情报播报 |
| `package.json` | 项目名、依赖更新（移除 Cetus，加入 @evefrontier/dapp-kit） |
| `README.md` | 全新项目说明 |
| `ARCHITECTURE.md` | 新架构文档 |
| `frontend/src/App.tsx` | 从 DeFi Dashboard 改为 Assembly Dashboard |

### 🆕 全新文件

| 文件 | 说明 |
|------|------|
| `contracts/sources/gate_commander.move` | Smart Gate 扩展 - AI 控制跳跃权限 |
| `contracts/sources/ssu_commander.move` | Smart Storage Unit 扩展 - AI 交易站 |
| `contracts/sources/commander_config.move` | 共享配置模块 |
| `agent/assembly.ts` | Assembly 管理模块（CRUD 操作） |
| `agent/events.ts` | EVE 链上事件监听（JumpEvent、InventoryEvent） |
| `agent/intelligence.ts` | 情报分析模块（流量分析、威胁检测） |
| `agent/graphql.ts` | Sui GraphQL 查询封装 |
| `frontend/src/components/AssemblyDashboard.tsx` | Assembly 监控面板 |
| `frontend/src/components/GateStatus.tsx` | Gate 状态显示 |
| `frontend/src/components/IntelReport.tsx` | 情报报告页面 |

---

## Step 2: Move 合约改造

### 原合约: `vault.move`
- 功能: 资金管理（存取 SUI、交易记录、策略信号）
- 模式: 简单的 Coin 保险库 + 事件日志

### 新合约 1: `commander_config.move`
基于 builder-scaffold 的 `config.move` 模式：
```move
module eve_commander::config {
    // AdminCap + ExtensionConfig (shared object)
    // 动态字段存储各种配置
    // CAuth witness type 用于 authorize_extension
}
```

### 新合约 2: `gate_commander.move`
基于 `tribe_permit.move` 模式，扩展为 AI 驱动的门禁：
```move
module eve_commander::gate_commander {
    // 规则类型：
    // - TribeRule: 按部落过滤
    // - ReputationRule: 按声望过滤
    // - TollRule: 收费通行（EVE token）
    // - TimeRule: 时间段控制
    // - AIRule: AI 动态决策（链下签名验证）
    
    // issue_jump_permit: 根据规则组合判断是否发放通行证
    // 事件: PermitIssuedEvent, PermitDeniedEvent (情报数据)
}
```

### 新合约 3: `ssu_commander.move`
Storage Unit 扩展 - AI 自动化交易站：
```move
module eve_commander::ssu_commander {
    // 规则类型：
    // - TradeRule: 自动交易规则（存入 X 获得 Y）
    // - DepositRule: 限制存入物品类型/数量
    // - WithdrawRule: 限制取出条件
    
    // deposit_item / withdraw_item: 通过 Auth witness 控制
    // 事件: TradeExecutedEvent, InventoryAlertEvent
}
```

### 关键技术点
1. **Extension Pattern**: 使用 `authorize_extension<CAuth>` 注册到 world 合约
2. **Dynamic Fields**: 用 `ExtensionConfig` + dynamic fields 存储可配置规则
3. **Sponsored Transactions**: 需要 AdminACL 授权（EVE 的赞助交易模式）
4. **Events**: 所有操作发出事件，供 Agent 链下监听

---

## Step 3: Agent 核心改造

### `agent/main.ts` 改造
```
启动流程:
1. 初始化 Sui 客户端 + 钱包
2. 连接 EVE Frontier World (加载 world package ID + 对象 ID)
3. 查询拥有的 Assemblies (Gate/SSU/Turret/NetworkNode)
4. 启动事件监听 (JumpEvent, InventoryEvent, KillmailEvent)
5. 启动 Commander 策略循环
6. 启动 Telegram Bot
7. 定时 flush 日志到 Walrus
```

### `agent/commander.ts` (新核心)
```typescript
// 策略循环:
// 1. 查询所有 Assembly 状态 (GraphQL)
// 2. 检查 Network Node 燃料 → 自动补充警告
// 3. 分析 Gate 跳跃流量 → 调整门禁策略
// 4. 分析 SSU 库存变动 → 调整交易价格
// 5. 分析附近威胁 → 调整 Turret 优先级
// 6. 生成情报报告 → Walrus + Telegram
```

### `agent/assembly.ts` (新模块)
```typescript
// Assembly 管理:
// - listAssemblies(): 通过 GraphQL 查询拥有的 assemblies
// - getAssemblyStatus(id): 获取单个 assembly 详情
// - bringOnline(id): 上线 assembly
// - bringOffline(id): 下线 assembly
// - updateMetadata(id, name, desc): 更新元数据
// - authorizeExtension(assemblyId, extensionType): 注册扩展
```

### `agent/events.ts` (新模块)
```typescript
// 事件监听:
// - subscribeJumpEvents(): 监听 JumpEvent
// - subscribeInventoryEvents(): 监听存取事件
// - subscribeKillmailEvents(): 监听击杀事件
// - getRecentEvents(type, limit): 查询历史事件
```

### `agent/graphql.ts` (新模块)
```typescript
// GraphQL 查询封装:
// - getObjectsByType(type): 按类型查询对象
// - getAssemblyWithOwner(id): 获取 assembly + 拥有者
// - getCharacterByWallet(address): 通过钱包查 character
// - getOwnedAssemblies(address): 查询拥有的 assemblies
```

### `agent/intelligence.ts` (新模块)
```typescript
// 情报分析:
// - analyzeGateTraffic(): 分析跳跃门流量模式
// - analyzeThreatLevel(): 根据 killmail 评估威胁
// - analyzeMarketTrends(): 根据 SSU 交易分析供需
// - generateIntelReport(): 生成综合情报报告
```

---

## Step 4: Telegram Bot 命令调整

### 原命令 → 新命令
| 原命令 | 新命令 | 功能 |
|--------|--------|------|
| /start | /start | 欢迎 + 连接钱包 |
| /balance | /status | Assembly 总览（Gate/SSU/Turret/NWN 状态） |
| /swap | /gate | 管理 Smart Gate（查看流量、调整规则） |
| /strategy | /defense | 防御策略（Turret 优先级、威胁等级） |
| /history | /intel | 情报报告（事件日志、流量分析） |
| /settings | /config | 配置管理（规则、限额、开关） |
| - | /storage | 管理 Storage Unit（库存、交易规则） |
| - | /fuel | Network Node 燃料状态 |
| - | /alert | 告警设置（燃料低、攻击、异常流量） |

---

## Step 5: 前端改造

### 原 Dashboard → 新 Dashboard
| 原模块 | 新模块 |
|--------|--------|
| 资产总览 | Assembly 总览（类型分布、在线状态） |
| 交易历史 | 事件时间线（Jump/Trade/Kill） |
| 策略表现 | 防御报告（Gate 通行量、Turret 击杀） |
| Walrus 日志 | 情报面板（热力图、威胁地图） |

---

## 实施优先级

### P0 - MVP (Day 1)
1. ✅ Clone + 项目结构调整
2. Move 合约: `commander_config.move` + `gate_commander.move`
3. Agent: `graphql.ts` + `assembly.ts` + `events.ts`
4. 修改 `main.ts` 启动流程
5. Telegram Bot: /start + /status + /gate

### P1 - Core Features (Day 2)
1. Move 合约: `ssu_commander.move`
2. Agent: `commander.ts` 策略循环 + `intelligence.ts`
3. Telegram Bot: 完整命令
4. Walrus 集成（情报报告上链）

### P2 - Polish (Day 3)
1. 前端 Dashboard
2. 联调测试
3. Demo 视频
4. 文档完善

---

## EVE Frontier 关键技术参考

### World Contracts Package
- Gate: `world::gate` - 跳跃门（link/unlink/jump/issue_jump_permit）
- Storage Unit: `world::storage_unit` - 存储单元（deposit/withdraw + extension）
- Turret: `world::turret` - 炮台（get_target_priority_list + extension）
- Network Node: `world::network_node` - 网络节点（fuel/energy）
- Assembly: `world::assembly` - 通用建筑基类

### Extension Pattern
1. 发布包含 `Auth` witness type 的 Move 包
2. 调用 `gate::authorize_extension<Auth>(gate, owner_cap)` 注册
3. 之后 `jump` 需要 `JumpPermit`，由扩展的 `issue_jump_permit` 签发
4. 可选 `freeze_extension_config` 锁定扩展（不可更改）

### 读取数据
- **GraphQL**: `https://graphql.testnet.sui.io/graphql`
- **@evefrontier/dapp-kit**: `useSmartObject()`, `getAssemblyWithOwner()`, `getObjectsByType()`
- **Events**: `suix_queryEvents` with `MoveEventType` filter

### 事件类型
- `world::gate::JumpEvent` - 跳跃事件
- `world::gate::GateLinkedEvent` / `GateUnlinkedEvent`
- `world::storage_unit::StorageUnitCreatedEvent`
- `world::turret::PriorityListUpdatedEvent`
- `world::network_node::NetworkNodeCreatedEvent`
- `world::gate::ExtensionAuthorizedEvent`

### Sponsored Transactions
EVE 的很多操作需要 `admin_acl.verify_sponsor(ctx)`:
- `jump()`, `link_gates()`, `anchor()`, `share_object()`
- 需要 EVE 的 admin 作为 gas sponsor
- 本地测试使用 builder-scaffold 的 Docker 环境
