# Sui AI 开发工具与资源调研

> 调研日期：2026-02-09

---

## 一、Sui 官方对 AI 的战略定位

Sui 已将 AI 作为核心战略方向之一，官网专门设有 **[sui.io/ai](https://sui.io/ai)** 页面，标题为"Sui AI Stack | Trusted, Verifiable AI Systems"。

### 官方愿景
- **可信 AI 基础设施**：构建私密、自主、透明的 AI 系统，去除不透明中介
- **核心主张**：AI 基础设施需要可验证性——数据来源、训练过程、决策逻辑都应可审计
- **Sui Stack 模块化组件**：存储（Walrus）、访问控制（Seal）、可验证计算，支持 AI 应用全栈构建

### 官方重点用例
- 端到端加密的 AI 聊天、Copilot 服务
- 链上权限驱动的 offchain Agent
- 数据集资产化（贡献、货币化、复用）
- NFT/Token 门控的推理 API
- Agent 的链上身份和声誉系统
- **Google Agentic Payments Protocol (AP2) 发布合作伙伴**

### 官方博客 AI 系列文章
| 文章 | 链接 |
|------|------|
| Building the Internet for AI That Acts（AI Agent 执行基础设施） | https://blog.sui.io/agentic-execution-ai-agents-need-blockchain/ |
| When Agents Pay: The Trust Layer for Agentic Commerce | https://blog.sui.io/ai-agents-agentic-commerce-trust-layer/ |
| From Data to Decisions: Closing the Loop on a Verifiable AI Economy | https://blog.sui.io/verifiable-ai-economy-sui-stack/ |
| Data with Rights: Content Licensing for AI with the Sui Stack | https://blog.sui.io/data-with-rights-content-licensing-ai-sui-stack/ |
| Building Composable, Agent-Ready Applications on Sui | https://blog.sui.io/from-apps-to-composable-systems/ |

### 文档站 AI 助手
docs.sui.io 内置了 **"Ask Sui AI"** 功能，可以直接向 AI 问 Sui/Move 相关的开发问题。

---

## 二、Move 合约开发 AI 工具

### 1. Sui MCP (Model Context Protocol) - ⭐ 强烈推荐
- **仓库**: https://github.com/tamago-labs/sui-mcp
- **功能**: 33+ MCP 工具，覆盖钱包管理、DeFi 协议、智能合约开发、质押、市场数据
- **兼容**: Claude Desktop、Cursor.ai 等 MCP 客户端
- **特性**:
  - Scallop 借贷协议集成
  - Pyth 价格预言机集成
  - Sui CLI 集成用于合约开发和测试
  - zkLogin 钱包支持
- **用法**: 在 Claude Desktop 配置 MCP server 即可通过 AI 对话操作 Sui 链
- NPM: `@tamago-labs/sui-mcp`

### 2. SuiAudit (原 SuiGuard) - AI 合约审计
- **仓库**: https://github.com/k66inthesky/suiguard
- **网站**: https://suiaudit.wal.app/
- **功能**: AI 驱动的 Sui Move 代码审计方案
- **成绩**: 
  - 🥈 2025 Sui Hackathon Mandarin 第二名
  - 🥉 2025 Sui Taipei Dev Hackathon 第三名
- **特点**: Chrome 扩展 + AI 风险评估分析器 + ML 模型分类安全问题
- **发现**: 团队记录中提到"通用 LLM 对 Sui-Move 智能合约存在幻觉问题"，这是重要参考

### 3. Sui Move AI 知识库
- **仓库**: https://github.com/baicaiyihao/sui-move-ai-knowledgebase
- **描述**: Sui Move 语言的 AI 知识库，中文项目
- **用途**: 可用于增强 LLM 对 Sui Move 的理解

### 4. X-Engine - AI 代码审查
- **仓库**: https://github.com/tamago-labs/x-engine
- **功能**: AI-Powered Code Review for Move Smart Contracts

### 5. Legato Finance
- **仓库**: https://github.com/tamago-labs/legato-finance
- **描述**: AI-powered DeFi protocol built on Move（非托管流动性质押 + 市场预测）

---

## 三、Sui 生态 AI 项目

从 sui.io/ai 页面提到的生态项目：
- **Google AP2**: Sui 是 Google Agentic Payments Protocol 的发布合作伙伴
- **Swarm intelligence network**: Agent 协作网络，无需中央控制
- **去中心化 AI 聊天应用**: 基于 TEE 的私密可验证 AI
- **Agentic Finance Protocol**: AI Agent 支付、赚取、持有 USDC
- **Suithetic**: 去中心化合成数据集生成服务（https://github.com/lorine93s/suithetic）

---

## 四、AI 辅助 Move 开发的实用技巧

### LLM 使用注意事项
⚠️ **SuiAudit 团队的重要发现**: 通用 LLM（如 GPT-4、Claude）对 Sui Move 智能合约**存在幻觉问题**。这意味着：
- 不能完全信任 AI 生成的 Move 代码
- 需要人工验证所有关键逻辑
- 建议使用 Sui 文档和示例代码作为 RAG 上下文

### 推荐工作流
1. **使用 Sui MCP + Claude Desktop/Cursor**: 直接在 AI IDE 中集成 Sui 操作能力
2. **docs.sui.io 的 Ask Sui AI**: 遇到 API/概念问题先问官方 AI
3. **参考 sui-move-ai-knowledgebase**: 作为 prompt 的上下文补充
4. **用 SuiAudit 审计**: 写完合约后用 AI 审计工具检查安全性

### Prompt 工程建议
- 在 prompt 中明确指定 "Sui Move (not Aptos Move)"，因为两者有差异
- 提供 Sui 特有的概念（object model、shared objects、owned objects、Transfer Policy 等）
- 附带 Sui Move 框架的关键模块接口作为参考（sui::object, sui::transfer, sui::tx_context 等）

---

## 五、对黑客松项目的实用建议

### 开发工具链
1. **IDE**: Cursor + Sui MCP 插件，实现 AI 辅助 + 链上操作一体化
2. **审计**: 开发完成后用 SuiAudit 做安全扫描
3. **文档查询**: 善用 docs.sui.io 的 Ask Sui AI

### AI + Sui 项目方向（黑客松热门方向）
基于调研，以下方向在 Sui 生态中受到关注：
1. **AI Agent 链上执行框架** - Sui 官方博客大量讨论 agent 基础设施
2. **AI 数据资产化** - 用 Walrus 存储、Seal 加密，数据集作为 NFT 交易
3. **可验证 AI 推理** - 链上验证 AI 输出的正确性
4. **Agent 支付/商务** - Google AP2 合作背景下的 agentic commerce
5. **Move 合约 AI 审计工具** - SuiAudit 已证明可行且获奖

### 技术栈建议
- **Sui Stack**: Sui 链 + Walrus（去中心化存储）+ Seal（加密/访问控制）
- **AI 集成**: MCP 协议连接 AI 与链上操作
- **前端**: 标准 Web + Sui TypeScript SDK
- **合约**: Move on Sui，注意利用 object model 的优势

---

## 六、关键链接汇总

| 资源 | 链接 |
|------|------|
| Sui AI 官方页面 | https://sui.io/ai |
| Sui 文档（含 Ask Sui AI） | https://docs.sui.io |
| Sui MCP (AI 开发工具) | https://github.com/tamago-labs/sui-mcp |
| SuiAudit (AI 审计) | https://github.com/k66inthesky/suiguard |
| Sui Move AI 知识库 | https://github.com/baicaiyihao/sui-move-ai-knowledgebase |
| X-Engine (AI Code Review) | https://github.com/tamago-labs/x-engine |
| Sui Blog AI 系列 | https://blog.sui.io/?s=AI |
