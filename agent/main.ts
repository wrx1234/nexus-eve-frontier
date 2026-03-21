/**
 * Sui DeFi Jarvis — 主入口
 * 启动所有模块：钱包 / 策略引擎 / 风控 / 日志 / 社交
 */

import dotenv from 'dotenv';
dotenv.config();

import { createClient, generateWallet, importWallet, getBalance } from './wallet.js';
import { createAggregator } from './swap.js';
import { logAction, flushLogs } from './logger.js';
import { strategyLoop, DEFAULT_CONFIG as STRATEGY_CONFIG } from './strategy.js';
import { DEFAULT_RISK, updateBalance, formatRiskStatus } from './risk.js';

const NETWORK = process.env.SUI_NETWORK || 'testnet';
const PRIVATE_KEY = process.env.SUI_PRIVATE_KEY;
const WALRUS_FLUSH_INTERVAL = 5 * 60 * 1000; // 5 分钟 flush 一次日志到 Walrus

async function main() {
  console.log(`
╔═══════════════════════════════════════════╗
║  🤖 Sui DeFi Jarvis — The Infinite Money Glitch  ║
║  Track 2: Local God Mode                  ║
║  Powered by OpenClaw 🦞 + Sui 🌊          ║
╚═══════════════════════════════════════════╝
  `);

  // 1. 初始化网络
  const client = createClient(NETWORK);
  console.log(`🌐 网络: ${NETWORK}`);

  // 2. 初始化钱包
  let keypair, address;
  if (PRIVATE_KEY) {
    const wallet = importWallet(PRIVATE_KEY);
    keypair = wallet.keypair;
    address = wallet.address;
    console.log(`🔑 钱包已导入: ${address}`);
  } else {
    const wallet = generateWallet();
    keypair = wallet.keypair;
    address = wallet.address;
    console.log(`🔑 新钱包已生成: ${address}`);
    console.log(`⚠️  请设置 SUI_PRIVATE_KEY 环境变量以使用已有钱包`);
  }

  // 3. 查询余额
  const balance = await getBalance(client, address);
  console.log(`💰 余额: ${balance.suiFormatted} SUI`);
  updateBalance(Number(balance.suiFormatted));

  // 4. 初始化 Aggregator
  const aggregator = createAggregator();
  console.log(`🐋 Cetus Aggregator 已连接`);

  // 5. 记录启动日志
  logAction('agent_start', {
    network: NETWORK,
    address,
    balance: balance.suiFormatted,
    strategy: STRATEGY_CONFIG.strategy,
    autoTrade: STRATEGY_CONFIG.enableAutoTrade,
  });

  // 6. 定时 flush 日志到 Walrus
  setInterval(async () => {
    const blobId = await flushLogs();
    if (blobId) {
      console.log(`🐘 日志已上传 Walrus: ${blobId}`);
    }
  }, WALRUS_FLUSH_INTERVAL);

  // 7. 显示状态
  console.log(`\n${formatRiskStatus()}`);
  console.log(`\n📋 策略: ${STRATEGY_CONFIG.strategy}`);
  console.log(`🤖 自动交易: ${STRATEGY_CONFIG.enableAutoTrade ? '✅ 开启' : '⏸️ 关闭（通过 TG Bot 开启）'}`);

  // 8. 启动策略循环
  console.log(`\n🚀 Agent 已就绪！`);
  console.log(`💬 通过 @sui_kol_bot 与我交互`);
  console.log(`📝 日志: logs/ + Walrus\n`);

  await strategyLoop(client, keypair, STRATEGY_CONFIG);
}

main().catch((e) => {
  console.error(`💀 Agent 崩溃: ${e.message}`);
  logAction('agent_crash', { error: e.message });
  process.exit(1);
});
