# 🔒 安全审计报告 — Sui DeFi Jarvis

审计日期: 2026-02-09
审计人: AI Agent (自审)

## 1. 私钥管理 ⚠️ 中风险

### 发现
- 私钥存储在 `.env` 文件中（明文）
- `generateWallet()` 在控制台输出私钥前缀

### 建议
- [ ] 使用 keystore 加密存储（如 Sui keystore 格式）
- [ ] 生产环境使用环境变量注入，不存文件
- [ ] 删除控制台私钥日志输出
- [ ] 添加 `.env` 到 `.gitignore`（✅ 已有）

### 修复优先级: P0

---

## 2. Move 合约安全

### vault.move 审计

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 权限控制 | ✅ | VaultCap 模式，只有持有者可操作 |
| 整数溢出 | ✅ | Move 内置溢出检查 |
| 重入攻击 | ✅ | Move 无重入问题（所有权模型） |
| 余额检查 | ✅ | withdraw 前检查 `EInsufficientBalance` |
| 暂停功能 | ✅ | `set_paused` + `EPaused` 检查 |
| 对象共享 | ⚠️ | Vault 是共享对象，任何人可 deposit |

### 建议
- [ ] 考虑添加 deposit 白名单（或认为 anyone-can-deposit 是 feature）
- [ ] 添加事件索引以便审计追踪
- [x] owner 不可变更（安全，但也意味着无法迁移）

---

## 3. API 安全

### Cetus Aggregator
- 使用公开 API `api-sui.cetus.zone` → 无认证风险
- 滑点保护: ✅ 已实现（默认 1%）
- 路由验证: ⚠️ 依赖 Cetus 返回，未本地验证

### Walrus
- 使用 testnet publisher → 无认证
- 数据公开可读 → 不应存储敏感信息
- ✅ logger.ts 不记录私钥/密钥

### Moltbook
- API key 仅发送到 `www.moltbook.com`
- ✅ 凭据存在 `~/.config/moltbook/credentials.json`

### TG Bot
- Bot token 在 `.env` 中
- ⚠️ 任何人可与 bot 交互
- [ ] 建议添加 admin whitelist（只允许 owner 执行交易命令）

---

## 4. 风控安全 ✅ 低风险

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 单笔限额 | ✅ | 默认 10 SUI |
| 日限额 | ✅ | 默认 50 SUI |
| 止损 | ✅ | 默认 2% |
| 紧急停止 | ✅ | `emergencyStop()` 可用 |
| 回撤限制 | ✅ | 默认 10% |
| 频率限制 | ✅ | 每小时最多 10 笔 |

---

## 5. 依赖安全

```
@mysten/sui               — 官方 SDK，活跃维护 ✅
@cetusprotocol/aggregator  — 官方 SDK，活跃维护 ✅
grammy                     — 流行 TG 框架，活跃维护 ✅
dotenv                     — 标准库 ✅
bn.js                      — 标准库 ✅
```

### 建议
- [ ] 定期 `npm audit` 检查漏洞
- [ ] 锁定依赖版本（package-lock.json）

---

## 6. 信息泄露

| 检查项 | 状态 | 说明 |
|--------|------|------|
| .env 不在 git | ✅ | .gitignore 已配置 |
| 私钥不在日志 | ⚠️ | wallet.ts 输出前缀，应移除 |
| API key 不在代码 | ✅ | 通过环境变量 |
| 社交推文无敏感信息 | ✅ | 只发交易结果 |

---

## 7. 安全评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 私钥管理 | 6/10 | 明文 .env，建议加密 |
| 合约安全 | 9/10 | Move 天然安全，VaultCap 权限 |
| API 安全 | 7/10 | 需加 bot admin whitelist |
| 风控 | 9/10 | 完善的多层保护 |
| 依赖 | 8/10 | 全部官方/知名库 |
| 总体 | **7.8/10** | Demo 级别安全，生产需加强 |

---

## 8. 待修复事项（按优先级）

### P0 — 必须修复
1. TG Bot 添加 admin whitelist
2. 移除 wallet.ts 控制台私钥输出

### P1 — 建议修复
3. 私钥加密存储
4. npm audit 检查

### P2 — 可选
5. deposit 白名单
6. 路由本地验证
