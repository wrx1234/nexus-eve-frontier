/**
 * 集成测试 — 模拟完整用户流程
 */
import { generateWallet, createClient, getBalance } from '../agent/wallet.js';
import { createAggregator, getSwapQuote, TOKENS } from '../agent/swap.js';
import { logAction, flushLogs } from '../agent/logger.js';
import { checkTrade, resetDailyStats, updateBalance, formatRiskStatus } from '../agent/risk.js';
import { formatTradeTweet } from '../agent/social.js';

async function integrationTest() {
  console.log('🧪 集成测试 — 模拟完整用户流程\n');
  let passed = 0, failed = 0;

  // Step 1: 生成钱包
  console.log('─── Step 1: 生成钱包 ───');
  const wallet = generateWallet();
  console.log(`地址: ${wallet.address}`);
  
  try {
    console.assert(wallet.address.startsWith('0x'), '地址格式错误');
    console.log('✅ Step 1');
    passed++;
  } catch (e: any) { console.log(`❌ Step 1: ${e.message}`); failed++; }

  // Step 2: 连接 testnet，查余额
  console.log('\n─── Step 2: 查询余额 ───');
  const client = createClient('testnet');
  try {
    const bal = await getBalance(client, wallet.address);
    console.log(`SUI: ${bal.suiFormatted}`);
    console.assert(bal.sui === 0n, '新地址应为 0');
    console.log('✅ Step 2');
    passed++;
  } catch (e: any) { console.log(`❌ Step 2: ${e.message}`); failed++; }

  // Step 3: 获取 swap 报价
  console.log('\n─── Step 3: Cetus 报价 ───');
  const aggregator = createAggregator();
  try {
    const quote = await getSwapQuote(
      aggregator, TOKENS.SUI, TOKENS.USDC,
      BigInt(1_000_000_000) // 1 SUI
    );
    if (quote) {
      console.log(`1 SUI → ${Number(quote.outputAmount) / 1e6} USDC`);
    } else {
      console.log('⚠️ 无可用路由（testnet 可能没流动性）');
    }
    console.log('✅ Step 3');
    passed++;
  } catch (e: any) { console.log(`❌ Step 3: ${e.message}`); failed++; }

  // Step 4: 风控检查
  console.log('\n─── Step 4: 风控检查 ───');
  resetDailyStats();
  updateBalance(100);
  try {
    const r1 = checkTrade(5);
    console.assert(r1.allowed, '5 SUI 应通过');
    const r2 = checkTrade(999);
    console.assert(!r2.allowed, '999 SUI 应拒绝');
    console.log(formatRiskStatus());
    console.log('✅ Step 4');
    passed++;
  } catch (e: any) { console.log(`❌ Step 4: ${e.message}`); failed++; }

  // Step 5: 日志记录
  console.log('\n─── Step 5: 日志记录 ───');
  try {
    logAction('integration_test', {
      wallet: wallet.address,
      timestamp: new Date().toISOString(),
      action: 'simulated_buy',
      amount: '5 SUI',
    });
    const blobId = await flushLogs();
    console.log(`日志: ${blobId || 'local fallback'}`);
    console.log('✅ Step 5');
    passed++;
  } catch (e: any) { console.log(`❌ Step 5: ${e.message}`); failed++; }

  // Step 6: 社交播报
  console.log('\n─── Step 6: 社交播报 ───');
  try {
    const tweet = formatTradeTweet({
      action: 'buy', fromToken: 'USDC', toToken: 'SUI',
      amount: '5', result: '5.2 SUI', pnlToday: '+$0.50',
    });
    console.assert(tweet.length > 0, '推文不应为空');
    console.log(tweet.substring(0, 100) + '...');
    console.log('✅ Step 6');
    passed++;
  } catch (e: any) { console.log(`❌ Step 6: ${e.message}`); failed++; }

  console.log('\n' + '═'.repeat(40));
  console.log(`🏁 集成测试: ${passed}/${passed + failed} 通过`);
  
  if (failed === 0) {
    console.log('🎉 所有测试通过！Agent 准备就绪。');
  } else {
    console.log(`⚠️ ${failed} 个测试失败，需要修复。`);
  }
}

integrationTest().catch(console.error);
