# 🤖 Sui DeFi Jarvis — The Infinite Money Glitch

> An autonomous AI Agent running on OpenClaw that manages DeFi assets on Sui, aiming to be self-sustaining: earning more than it costs to run.

**Track**: Mission OpenClaw — Local God Mode 🤖
**Also competing in**: Sui Vibe Hackathon 2026

## 🌊 What is this?

Sui DeFi Jarvis is a fully autonomous AI agent that:
- **Earns** — Executes DeFi strategies on Sui (swap, LP, yield farming) via Cetus
- **Thinks** — AI-powered market analysis and strategy optimization
- **Records** — Every decision and trade logged immutably on Walrus
- **Protects** — Risk management with configurable limits and Seal encryption
- **Communicates** — Interact via Telegram Bot (@sui_kol_bot)

## 🔗 Sui Stack Integration

### 🐋 Cetus (DEX & Aggregator)
Cetus Aggregator SDK powers the trading engine, finding optimal swap routes across multiple DEXes on Sui. The agent automatically:
- Discovers best swap paths for any token pair
- Provides/removes liquidity to earn trading fees
- Monitors price movements for arbitrage opportunities

### 🐘 Walrus (Decentralized Storage)
Every action the agent takes is transparently recorded on Walrus:
- Trade execution logs with full reasoning
- Strategy snapshots at regular intervals
- Performance reports accessible to anyone
- **Why**: Creates an immutable audit trail — if the agent goes rogue, every step is traceable

### 🔐 Seal (Secrets Management)
Sensitive data is protected using Sui's native encryption:
- Agent wallet keys encrypted at rest
- Trading strategy details encrypted to prevent front-running
- Sui-based access control for decryption

### 🦞 OpenClaw (Agent Framework)
The brain of the operation:
- Persistent memory across sessions
- Proactive heartbeat — agent acts without being prompted
- Skill system for modular capability extension
- Native Telegram integration

### 📱 Moltbook (Agent Social Network)
Social intelligence layer:
- Fetches market alpha from agent community
- Publishes trading reports and performance updates
- Cross-agent information exchange

## 🏗️ Architecture

```
User (Telegram @sui_kol_bot)
         │
    TG Bot Layer
         │
    AI Agent Core ─── OpenClaw Runtime
    ├── DeFi Engine ──── Cetus Aggregator
    ├── Risk Manager ─── Seal Encryption
    ├── Strategy AI ──── Market Analysis
    └── Walrus Logger ── Immutable Audit Trail
         │
    Sui Blockchain
```

## 💡 Inspired by Base Ecosystem

This project takes patterns validated in the Base OpenClaw ecosystem and builds them as a unified system on Sui:

| Base Project | Validated Pattern | Our Sui Implementation |
|---|---|---|
| Clanker ($7.48B vol) | Agent token economics | Automated trading & market making |
| ClawMart (x402) | Agent API marketplace | Agent pays for data services with SUI |
| Bankr | Agent wallet management | Full DeFi portfolio management |
| Moltbook | Agent social network | Intelligence gathering + reporting |

**Key differentiator**: Base projects are single-purpose tools. We build a **full-cycle autonomous agent** — from intelligence → decision → execution → recording → analysis.

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/wrx1234/sui-hackathon.git
cd sui-hackathon

# Setup (coming soon)
./scripts/setup.sh

# Run the agent
python agent/main.py
```

## 📊 AI Usage Disclosure (Required by Hackathon Rules)

This project is developed with significant AI assistance. Full transparency:

| Tool | Model | Usage |
|------|-------|-------|
| **OpenClaw** v2026.2.6-3 | Claude Opus 4.6 | Agent framework, code gen, docs, deployment |
| **Claude Code** | Claude Opus 4.6 | CLI code editing & debugging |

- 📝 All AI interactions logged in `ai-logs/prompts.jsonl`
- 📄 Full disclosure: [`AI_DISCLOSURE.md`](./AI_DISCLOSURE.md)
- 🔑 Key prompts documented per hackathon requirement
- ~80% code AI-generated, human-directed architecture & decisions

## 📁 Project Structure

```
├── contracts/       # Move smart contracts (vault, strategy, logger)
├── agent/           # AI Agent core (DeFi engine, risk, strategy)
├── bot/             # Telegram Bot
├── frontend/        # Web dashboard
├── scripts/         # Deploy & setup scripts
├── tools/           # AI logger & utilities
├── ai-logs/         # AI interaction records
├── docs/            # Research & documentation
├── ARCHITECTURE.md  # System design
├── RESEARCH.md      # Hackathon research
└── AI_DISCLOSURE.md # AI usage transparency
```

## 📜 License

MIT

## 🌊🦞 Built with Sui + OpenClaw
