# 🚀 EVE Frontier AI Commander

> An autonomous AI Agent running on OpenClaw that manages Smart Assemblies in EVE Frontier - Gates, Storage Units, Turrets, and Network Nodes.

**Built for**: EVE Frontier Hackathon
**Powered by**: OpenClaw 🦞 + Sui 🌊 + EVE Frontier 🌌

## 🌌 What is this?

EVE Frontier AI Commander is a fully autonomous AI agent that:
- **🚪 Controls Gates** - AI-driven jump permit rules (tribe filtering, allowlists, time-based access)
- **📦 Manages Storage** - Automated trading stations with custom deposit/withdraw logic
- **🔫 Optimizes Turrets** - AI-powered target priority for defense turrets
- **⚡ Monitors Infrastructure** - Network Node fuel/energy tracking with alerts
- **🕵️ Gathers Intelligence** - Real-time analysis of jump traffic, threats, and market trends

## 🔗 Tech Stack

### EVE Frontier World Contracts
The agent interacts with the on-chain EVE Frontier world:
- `world::gate` - Smart Gates with programmable jump rules
- `world::storage_unit` - Programmable Storage Units with extension logic
- `world::turret` - Smart Turrets with custom targeting
- `world::network_node` - Energy infrastructure management

### Custom Move Extensions
- `eve_commander::config` - Shared configuration with dynamic fields
- `eve_commander::gate_commander` - AI-driven gate access control with multi-rule support
  - Tribe filtering
  - Allowlist mode
  - Time-based access control
  - Traffic statistics & denial events for AI analysis

### AI + OpenClaw
- **Commander Strategy Loop** - Periodic analysis of assembly status, traffic, threats
- **Intelligence Module** - Analyzes on-chain events (JumpEvent, AccessDenied) for patterns
- **Walrus Logging** - Every AI decision immutably recorded on Walrus

### Data Access
- **Sui GraphQL API** - Query assemblies, characters, objects by type
- **suix_queryEvents** - Monitor JumpEvents, inventory changes, killmails
- **@evefrontier/dapp-kit** - Assembly queries and transformation helpers

## 📁 Project Structure

```
eve-frontier-ai-commander/
├── contracts/
│   └── sources/
│       ├── commander_config.move    # Shared config (AdminCap + CAuth)
│       └── gate_commander.move      # Smart Gate AI extension
├── agent/
│   ├── main.ts                      # Entry point
│   ├── wallet.ts                    # Sui wallet management
│   ├── assembly.ts                  # Assembly CRUD operations
│   ├── graphql.ts                   # Sui GraphQL queries
│   ├── intelligence.ts              # Traffic & threat analysis
│   ├── logger.ts                    # Walrus logging
│   └── social.ts                    # Social/notification engine
├── bot/
│   └── main.ts                      # Telegram Bot
├── frontend/
│   └── src/                         # React Dashboard
└── HACKATHON-PLAN.md               # Detailed transformation plan
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your keys:
#   SUI_PRIVATE_KEY=suiprivkey1...
#   SUI_NETWORK=testnet
#   WORLD_PACKAGE_ID=0x...
#   COMMANDER_PACKAGE_ID=0x...

# 3. Start the Commander
npm start

# 4. Or start the Telegram Bot
npm run bot
```

## 🔧 Environment Variables

| Variable | Description |
|----------|------------|
| `SUI_PRIVATE_KEY` | Sui wallet private key (bech32 format) |
| `SUI_NETWORK` | Network: testnet / mainnet / devnet |
| `WORLD_PACKAGE_ID` | EVE Frontier world contracts package ID |
| `COMMANDER_PACKAGE_ID` | Deployed eve_commander package ID |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `WALRUS_PUBLISHER` | Walrus publisher endpoint |

## 📊 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome + wallet connection |
| `/status` | Assembly overview (all types) |
| `/gate` | Gate management (traffic, rules) |
| `/storage` | Storage Unit management |
| `/defense` | Turret defense strategy |
| `/intel` | Intelligence report |
| `/fuel` | Network Node fuel status |
| `/config` | Configuration management |
| `/alert` | Alert settings |

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│                 Telegram Bot                   │
│            EVE Commander Bot                   │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│           AI Commander Core                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ Assembly  │ │  Intel    │ │  Defense   │  │
│  │ Manager   │ │  Analyst  │ │  Strategy  │  │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘  │
│        │             │             │          │
│  ┌─────▼─────────────▼─────────────▼─────┐   │
│  │        Sui Chain Interface             │   │
│  │  GraphQL + Events + Move Calls         │   │
│  └────────────────┬──────────────────────┘   │
└───────────────────┼──────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Sui Chain│ │   EVE    │ │  Walrus  │
│(Move TX) │ │ World    │ │ (Logs)   │
│          │ │Contracts │ │          │
└──────────┘ └──────────┘ └──────────┘
```

## 🛡️ Smart Gate Extension

The `gate_commander.move` extension supports multiple composable rules:

1. **Tribe Rule** - Allow only specific tribes
2. **Allowlist Rule** - Whitelist approved tribes
3. **Time Rule** - Open/close gate by time period
4. **Statistics** - Track permits issued and denials on-chain

All events are emitted for the AI agent to analyze:
- `PermitIssuedEvent` - Successful gate passage (traffic analysis)
- `AccessDeniedEvent` - Denied attempts (threat detection)
- `ConfigUpdatedEvent` - Rule changes

## 📝 AI Disclosure

This project uses AI assistance (Claude via OpenClaw) for:
- Code generation and architecture design
- Strategy analysis and decision-making
- Natural language interaction via Telegram

All AI decisions are logged to Walrus for full transparency and auditability.

## License

MIT
