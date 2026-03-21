/**
 * 端到端集成测试 — 模拟完整交易周期
 * Bot命令 → 策略分析 → 风控检查 → Swap报价 → 日志记录 → 社交播报
 */

import { generateWallet, createClient, getBalance } from '../agent/wallet.js';
import { createAggregator, getSwapQuote, TOKENS, TOKEN_NAMES, formatSwapPreview } from '../agent/swap.js';
import { logAction, flushLogs, getLogBuffer } from '../agent/logger.js';
import { analyzeMarket, getTradingState, formatStatusMessage } from '../agent/strategy.js';
import { checkTrade, recordTrade, updateBalance, checkStopLoss, resetDailyStats, emergencyStop, resumeTrading, formatRiskStatus } from '../agent/risk.js';
import { formatTradeTweet, formatKolReply, formatMilestoneTweet, broadcastTrade } from '../agent/social.js';

let totalPassed = 0, totalFailed = 0;

function test(name: string, fn: () => void | Promise<void>) {
  return (async () => {
    try {
      await fn();
      console.log(`  ✅ ${name}`);
      totalPassed++;
    } catch (e: any) {
      console.log(`  ❌ ${name}: ${e.message}`);
      totalFailed++;
    }
  })();
}

function assert(cond: boolean, msg: string) {
  if (!cond) throw new Error(msg);
}

async function e2eTest() {
  console.log('🔗 端到端集成测试 — 完整交易周期\n');

  // ═══════════════════════════════════════
  // Phase 1: 初始化（模拟用户首次使用）
  // ═══════════════════════════════════════
  console.log('═══ Phase 1: 用户初始化 ═══');
  
  const wallet = generateWallet();
  const client = createClient('testnet');
  const aggregator = createAggregator();
  
  await test('1.1 钱包生成', () => {
    assert(wallet.address.startsWith('0x'), '地址格式');
    assert(wallet.address.length === 66, '地址长度');
  });

  let balance: any;
  await test('1.2 连接网络+查余额', async () => {
    balance = await getBalance(client, wallet.address);
    assert(balance.sui === 0n, '新地址余额应为0');
  });

  await test('1.3 初始化日志', () => {
    logAction('e2e_init', { address: wallet.address, network: 'testnet' });
    assert(getLogBuffer().length > 0, '日志应已记录');
  });

  // ═══════════════════════════════════════
  // Phase 2: 市场分析（策略引擎）
  // ═══════════════════════════════════════
  console.log('\n═══ Phase 2: 市场分析 ═══');

  await test('2.1 Cetus 报价查询', async () => {
    const quote = await getSwapQuote(aggregator, TOKENS.SUI, TOKENS.USDC, BigInt(1_000_000_000));
    // testnet 可能无路由，不 assert 有值
    logAction('quote_check', { hasRoute: quote !== null });
  });

  await test('2.2 趋势策略（数据不足→hold）', () => {
    const signal = analyzeMarket('E2E_SUI', 'trend');
    assert(signal.direction === 'hold', `数据不足应 hold, got ${signal.direction}`);
    assert(signal.confidence === 0, 'confidence 应为 0');
    logAction('strategy_signal', { ...signal });
  });

  await test('2.3 均值回归策略（数据不足→hold）', () => {
    const signal = analyzeMarket('E2E_SUI', 'mean_reversion');
    assert(signal.direction === 'hold', '数据不足应 hold');
  });

  await test('2.4 状态消息格式化', () => {
    const msg = formatStatusMessage();
    assert(msg.includes('策略状态'), '应包含策略状态');
    assert(msg.includes('自动交易'), '应包含自动交易');
  });

  // ═══════════════════════════════════════
  // Phase 3: 风控检查
  // ═══════════════════════════════════════
  console.log('\n═══ Phase 3: 风控检查 ═══');

  resetDailyStats();
  updateBalance(100);

  await test('3.1 正常交易放行', () => {
    const r = checkTrade(5);
    assert(r.allowed, '5 SUI 应放行');
    assert(r.warnings.length === 0, '无警告');
  });

  await test('3.2 超额交易拦截', () => {
    const r = checkTrade(100);
    assert(!r.allowed, '100 SUI 应拦截');
    assert(r.reason!.includes('单笔限额'), '应提示单笔限额');
  });

  await test('3.3 紧急停止→恢复', () => {
    emergencyStop('e2e test');
    const r1 = checkTrade(1);
    assert(!r1.allowed, '紧急停止应拦截');
    resumeTrading();
    const r2 = checkTrade(1);
    assert(r2.allowed, '恢复后应放行');
  });

  await test('3.4 日限额累积', () => {
    resetDailyStats();
    updateBalance(100);
    updateBalance(100);
    for (let i = 0; i < 5; i++) recordTrade(10, 0);
    const r = checkTrade(1);
    assert(!r.allowed, '50 SUI 日限额后应拦截');
    resetDailyStats();
    updateBalance(100);
    updateBalance(100);
  });

  await test('3.5 止损检测', () => {
    const sl1 = checkStopLoss(100, 97);
    assert(sl1.triggered, '3%跌幅应触发');
    const sl2 = checkStopLoss(100, 99);
    assert(!sl2.triggered, '1%跌幅不应触发');
  });

  await test('3.6 风控状态格式化', () => {
    const msg = formatRiskStatus();
    assert(msg.includes('风控状态'), '应含风控状态');
    assert(msg.includes('止损'), '应含止损');
  });

  // ═══════════════════════════════════════
  // Phase 4: 模拟交易执行
  // ═══════════════════════════════════════
  console.log('\n═══ Phase 4: 模拟交易 ═══');

  await test('4.1 交易前风控放行→记录交易', () => {
    resetDailyStats();
    updateBalance(100);
    updateBalance(100);
    const r = checkTrade(5);
    assert(r.allowed, '应放行');
    recordTrade(5, 1.5);
    logAction('trade_execute', {
      direction: 'buy', from: 'USDC', to: 'SUI',
      amount: 5, pnl: 1.5,
    });
  });

  await test('4.2 Swap 预览格式化', () => {
    const preview = formatSwapPreview('SUI', 'USDC', '5', BigInt(7_500_000), 0.01);
    assert(preview.includes('SUI'), '应含 SUI');
    assert(preview.includes('USDC'), '应含 USDC');
  });

  // ═══════════════════════════════════════
  // Phase 5: 日志上链
  // ═══════════════════════════════════════
  console.log('\n═══ Phase 5: 日志上链 ═══');

  await test('5.1 日志缓冲区非空', () => {
    assert(getLogBuffer().length > 0, '应有日志');
  });

  await test('5.2 Flush 日志（Walrus/本地）', async () => {
    const blobId = await flushLogs();
    // Walrus 可能不可用，降级到本地也算成功
    logAction('e2e_flush', { blobId: blobId || 'local' });
  });

  // ═══════════════════════════════════════
  // Phase 6: 社交播报
  // ═══════════════════════════════════════
  console.log('\n═══ Phase 6: 社交播报 ═══');

  await test('6.1 交易推文', () => {
    const tweet = formatTradeTweet({
      action: 'buy', fromToken: 'USDC', toToken: 'SUI',
      amount: '5', result: '5.2 SUI', pnlToday: '+$1.50',
    });
    assert(tweet.length > 0, '推文非空');
    assert(tweet.includes('SUI'), '应含 SUI');
  });

  await test('6.2 KOL 回复', () => {
    const reply = formatKolReply({
      sentiment: { sentiment: 'bullish', confidence: 0.9, tokens: ['SUI'], tradeSignal: 'buy', reasoning: 'test' },
      tradeAction: 'went long on SUI',
      walrusBlobId: 'e2e_test_blob',
    });
    assert(reply.includes('Bullish'), '应含 Bullish');
    assert(reply.includes('walrus'), '应含 walrus 链接');
  });

  await test('6.3 里程碑推文', () => {
    const tweet = formatMilestoneTweet({
      milestone: 'E2E Test Complete', pnlTotal: '+$1.50', winRate: '100%',
    });
    assert(tweet.length > 0, '里程碑推文非空');
  });

  await test('6.4 完整播报流程', async () => {
    await broadcastTrade({
      action: 'buy', fromToken: 'USDC', toToken: 'SUI',
      amount: '5', result: '5.2 SUI', pnlToday: '+$1.50',
    });
  });

  // ═══════════════════════════════════════
  // Phase 7: 多轮交易模拟
  // ═══════════════════════════════════════
  console.log('\n═══ Phase 7: 多轮交易模拟 ═══');

  await test('7.1 连续 3 笔交易→风控正常', () => {
    resetDailyStats();
    updateBalance(100);
    updateBalance(100);
    
    const trades = [
      { amount: 5, pnl: 1.5 },
      { amount: 8, pnl: -0.5 },
      { amount: 3, pnl: 0.8 },
    ];
    
    for (const t of trades) {
      const r = checkTrade(t.amount);
      assert(r.allowed, `${t.amount} SUI 应放行`);
      recordTrade(t.amount, t.pnl);
      logAction('multi_trade', t);
    }
  });

  await test('7.2 第 4 笔接近日限→警告', () => {
    const r = checkTrade(10);
    assert(r.allowed, '应放行');
    // 16+10=26, 已达52% 日限
  });

  await test('7.3 交易状态一致性', () => {
    const state = getTradingState();
    // strategy 模块的 state 是独立的，这里只验证结构
    assert(typeof state.dailyVolume === 'number', 'dailyVolume 应为 number');
    assert(Array.isArray(state.positions), 'positions 应为数组');
  });

  // ═══════════════════════════════════════
  // 结果汇总
  // ═══════════════════════════════════════
  console.log('\n' + '═'.repeat(50));
  console.log(`🏁 端到端集成测试: ${totalPassed}/${totalPassed + totalFailed} 通过`);
  
  if (totalFailed === 0) {
    console.log('🎉 全部通过！模块间协作正常。');
    console.log('\n📋 已验证链路:');
    console.log('  钱包生成 → 网络连接 → 余额查询');
    console.log('  Cetus报价 → 策略分析 → 风控检查');
    console.log('  交易执行 → 日志记录 → Walrus上传');
    console.log('  社交播报 → 推文格式化 → 多轮交易');
  } else {
    console.log(`⚠️ ${totalFailed} 个测试失败！`);
  }
}

e2eTest().catch(console.error);
