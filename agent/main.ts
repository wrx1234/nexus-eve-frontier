/**
 * EVE Frontier AI Commander - 主入口
 * 启动所有模块: 钱包 / Assembly 管理 / 情报分析 / 日志
 */

import dotenv from 'dotenv';
dotenv.config();

import { createClient, importWallet, generateWallet, getBalance } from './wallet.js';
import { logAction, flushLogs } from './logger.js';
import { getManagedAssemblies, formatAssemblyStatus } from './assembly.js';
import { generateIntelReport, formatIntelReport } from './intelligence.js';
import { getCharacterByWallet, getAllGates, getAllStorageUnits, getAllNetworkNodes, getAllTurrets } from './graphql.js';

const NETWORK = process.env.SUI_NETWORK || 'testnet';
const PRIVATE_KEY = process.env.SUI_PRIVATE_KEY;
const WALRUS_FLUSH_INTERVAL = 5 * 60 * 1000; // 5 分钟
const INTEL_CHECK_INTERVAL = 2 * 60 * 1000; // 2 分钟

async function main() {
  console.log(`
╔═══════════════════════════════════════════════════╗
║  🚀 EVE Frontier AI Commander                     ║
║  Autonomous Smart Assembly Manager                ║
║  Powered by OpenClaw 🦞 + Sui 🌊 + EVE Frontier  ║
╚═══════════════════════════════════════════════════╝
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
    console.log(`⚠️  请设置 SUI_PRIVATE_KEY 环境变量`);
  }

  // 3. 查询余额
  const balance = await getBalance(client, address);
  console.log(`💰 余额: ${balance.suiFormatted} SUI`);

  // 4. 查询 Character
  console.log(`\n🔍 查询 EVE Character...`);
  const character = await getCharacterByWallet(address);
  if (character) {
    console.log(`👤 Character: ${character.name} (Tribe: ${character.tribe})`);
  } else {
    console.log(`⚠️  未找到 Character - 需要先在游戏中创建角色`);
    console.log(`   或设置 WORLD_PACKAGE_ID 环境变量`);
  }

  // 5. 扫描 Assembly
  console.log(`\n📡 扫描 Smart Assemblies...`);
  try {
    const [gates, storageUnits, networkNodes, turrets] = await Promise.all([
      getAllGates(10),
      getAllStorageUnits(10),
      getAllNetworkNodes(10),
      getAllTurrets(10),
    ]);
    console.log(`🚪 Gates: ${gates.length}`);
    console.log(`📦 Storage Units: ${storageUnits.length}`);
    console.log(`⚡ Network Nodes: ${networkNodes.length}`);
    console.log(`🔫 Turrets: ${turrets.length}`);
  } catch (e: any) {
    console.log(`⚠️  Assembly 扫描失败: ${e.message}`);
  }

  // 6. 记录启动日志
  logAction('commander_start', {
    network: NETWORK,
    address,
    balance: balance.suiFormatted,
    character: character?.name || 'none',
  });

  // 7. 定时 flush 日志到 Walrus
  setInterval(async () => {
    const blobId = await flushLogs();
    if (blobId) {
      console.log(`🐘 日志已上传 Walrus: ${blobId}`);
    }
  }, WALRUS_FLUSH_INTERVAL);

  // 8. 启动情报循环
  console.log(`\n🕵️ 启动情报分析循环 (每 ${INTEL_CHECK_INTERVAL / 1000}s)...`);
  
  // 首次情报报告
  try {
    const report = await generateIntelReport(process.env.COMMANDER_PACKAGE_ID);
    console.log(`\n${formatIntelReport(report)}`);
  } catch (e: any) {
    console.log(`⚠️  首次情报分析失败: ${e.message}`);
  }

  // 9. 显示状态
  console.log(`\n${formatAssemblyStatus(getManagedAssemblies())}`);
  console.log(`\n🚀 Commander 已就绪！`);
  console.log(`💬 通过 Telegram Bot 与我交互`);
  console.log(`📝 日志: logs/ + Walrus\n`);

  // 10. 情报循环
  await commanderLoop();
}

async function commanderLoop() {
  while (true) {
    try {
      // 定期生成情报报告
      const report = await generateIntelReport(process.env.COMMANDER_PACKAGE_ID);
      
      // 如果威胁等级为 high/critical，记录告警
      if (report.threats.level === 'high' || report.threats.level === 'critical') {
        logAction('threat_alert', {
          level: report.threats.level,
          alerts: report.threats.suspiciousActivity,
        });
        console.log(`🚨 威胁等级: ${report.threats.level.toUpperCase()}`);
        for (const alert of report.threats.suspiciousActivity) {
          console.log(`  ⚠️ ${alert}`);
        }
      }

    } catch (e: any) {
      console.error(`Commander loop error: ${e.message}`);
      logAction('commander_error', { error: e.message });
    }

    await new Promise(r => setTimeout(r, INTEL_CHECK_INTERVAL));
  }
}

main().catch((e) => {
  console.error(`💀 Commander 崩溃: ${e.message}`);
  logAction('commander_crash', { error: e.message });
  process.exit(1);
});
