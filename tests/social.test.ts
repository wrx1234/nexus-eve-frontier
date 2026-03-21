/**
 * social.ts 单元测试
 */
import { broadcastTrade, formatTradeTweet, formatKolReply, formatMilestoneTweet } from '../agent/social.js';

async function testSocial() {
  let passed = 0, failed = 0;

  // Test 1: 交易推文格式化
  try {
    const tweet = formatTradeTweet({
      action: 'buy', fromToken: 'USDC', toToken: 'SUI',
      amount: '100', result: 'success', pnlToday: '+$5.00',
    });
    console.assert(tweet.length > 0, '推文不应为空');
    console.assert(tweet.includes('SUI') || tweet.includes('buy'), '应提到 SUI 或 buy');
    console.log('✅ Test 1: 交易推文格式化');
    passed++;
  } catch (e: any) { console.log(`❌ Test 1: ${e.message}`); failed++; }

  // Test 2: KOL 回复格式化
  try {
    const reply = formatKolReply({
      sentiment: { sentiment: 'bullish', confidence: 0.85, tokens: ['SUI'], tradeSignal: 'buy', reasoning: 'test' },
      tradeAction: 'went long on SUI',
      walrusBlobId: 'abc123',
    });
    console.assert(reply.length > 0, '回复不应为空');
    console.log('✅ Test 2: KOL 回复格式化');
    passed++;
  } catch (e: any) { console.log(`❌ Test 2: ${e.message}`); failed++; }

  // Test 3: 里程碑推文
  try {
    const tweet = formatMilestoneTweet({
      milestone: '100 trades', pnlTotal: '+$50', winRate: '65%',
    });
    console.assert(tweet.length > 0, '里程碑推文不应为空');
    console.assert(tweet.includes('100') || tweet.includes('milestone'), '应包含里程碑数据');
    console.log('✅ Test 3: 里程碑推文');
    passed++;
  } catch (e: any) { console.log(`❌ Test 3: ${e.message}`); failed++; }

  // Test 4: 交易播报（dry run）
  try {
    await broadcastTrade({
      action: 'buy', fromToken: 'USDC', toToken: 'SUI',
      amount: '100', result: 'success', pnlToday: '+$5.00',
    });
    // broadcastTrade 不应抛异常
    console.log('✅ Test 4: 交易播报');
    passed++;
  } catch (e: any) { console.log(`❌ Test 4: ${e.message}`); failed++; }

  console.log(`\n📊 social.ts: ${passed}/${passed + failed} 通过`);
  return { passed, failed };
}

testSocial().catch(console.error);
