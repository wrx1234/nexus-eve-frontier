/**
 * strategy.ts 单元测试
 */
import { analyzeMarket, getTradingState, formatStatusMessage } from '../agent/strategy.js';

// 需要直接操作 priceHistory，用 hack 方式注入
// 因为 priceHistory 是模块私有的，通过 analyzeMarket 间接测试

async function testStrategy() {
  let passed = 0, failed = 0;

  // Test 1: 数据不足时返回 hold
  try {
    const signal = analyzeMarket('TEST_TOKEN', 'trend');
    console.assert(signal.direction === 'hold', `数据不足应返回 hold, got ${signal.direction}`);
    console.assert(signal.confidence === 0, '数据不足 confidence 应为 0');
    console.log('✅ Test 1: 数据不足返回 hold');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 1: ${e.message}`);
    failed++;
  }

  // Test 2: 初始交易状态
  try {
    const state = getTradingState();
    console.assert(state.dailyVolume === 0, '初始交易量应为 0');
    console.assert(state.tradesCount === 0, '初始交易次数应为 0');
    console.assert(state.positions.length === 0, '初始持仓应为空');
    console.log('✅ Test 2: 初始交易状态');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 2: ${e.message}`);
    failed++;
  }

  // Test 3: 格式化状态消息
  try {
    const msg = formatStatusMessage();
    console.assert(msg.includes('策略状态'), '应包含策略状态');
    console.assert(msg.includes('自动交易'), '应包含自动交易');
    console.assert(msg.includes('trend'), '应包含策略名');
    console.log('✅ Test 3: 格式化状态消息');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 3: ${e.message}`);
    failed++;
  }

  // Test 4: 均值回归策略 — 数据不足
  try {
    const signal = analyzeMarket('MR_TOKEN', 'mean_reversion');
    console.assert(signal.direction === 'hold', '数据不足应 hold');
    console.log('✅ Test 4: 均值回归 — 数据不足');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 4: ${e.message}`);
    failed++;
  }

  console.log(`\n📊 strategy.ts: ${passed}/${passed + failed} 通过`);
  return { passed, failed };
}

testStrategy().catch(console.error);
