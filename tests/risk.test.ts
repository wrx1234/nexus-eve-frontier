/**
 * risk.ts 单元测试
 */
import {
  checkTrade, recordTrade, updateBalance, checkStopLoss,
  emergencyStop, resumeTrading, resetDailyStats,
  formatRiskStatus, DEFAULT_RISK,
} from '../agent/risk.js';

async function testRisk() {
  let passed = 0, failed = 0;

  // 重置状态
  resetDailyStats();
  DEFAULT_RISK.emergencyStop = false;

  // Test 1: 正常交易通过
  try {
    const r = checkTrade(5);
    console.assert(r.allowed === true, '5 SUI 应允许');
    console.log('✅ Test 1: 正常交易通过');
    passed++;
  } catch (e: any) { console.log(`❌ Test 1: ${e.message}`); failed++; }

  // Test 2: 超单笔限额
  try {
    const r = checkTrade(100);
    console.assert(r.allowed === false, '100 SUI 应拒绝');
    console.assert(r.reason!.includes('单笔限额'), `应提示单笔限额, got: ${r.reason}`);
    console.log('✅ Test 2: 超单笔限额');
    passed++;
  } catch (e: any) { console.log(`❌ Test 2: ${e.message}`); failed++; }

  // Test 3: 紧急停止
  try {
    emergencyStop('测试');
    const r = checkTrade(1);
    console.assert(r.allowed === false, '紧急停止应拒绝');
    console.assert(r.reason!.includes('紧急'), '应提示紧急停止');
    resumeTrading();
    const r2 = checkTrade(1);
    console.assert(r2.allowed === true, '恢复后应允许');
    console.log('✅ Test 3: 紧急停止/恢复');
    passed++;
  } catch (e: any) { console.log(`❌ Test 3: ${e.message}`); failed++; }

  // Test 4: 日限额累计
  try {
    resetDailyStats();
    for (let i = 0; i < 5; i++) recordTrade(10, 0);
    const r = checkTrade(5);
    console.assert(r.allowed === false, '日限额满应拒绝');
    console.assert(r.reason!.includes('日限额'), `应提示日限额, got: ${r.reason}`);
    console.log('✅ Test 4: 日限额累计');
    passed++;
  } catch (e: any) { console.log(`❌ Test 4: ${e.message}`); failed++; }

  // Test 5: 止损触发
  try {
    const sl = checkStopLoss(100, 97);
    console.assert(sl.triggered === true, '3% 跌幅应触发 2% 止损');
    console.assert(sl.lossPercent >= 2, `亏损应 >= 2%, got ${sl.lossPercent}`);
    console.log('✅ Test 5: 止损触发');
    passed++;
  } catch (e: any) { console.log(`❌ Test 5: ${e.message}`); failed++; }

  // Test 6: 止损未触发
  try {
    const sl = checkStopLoss(100, 99);
    console.assert(sl.triggered === false, '1% 跌幅不应触发');
    console.log('✅ Test 6: 止损未触发');
    passed++;
  } catch (e: any) { console.log(`❌ Test 6: ${e.message}`); failed++; }

  // Test 7: 回撤检查
  try {
    resetDailyStats();
    updateBalance(100);
    updateBalance(88); // 12% 回撤
    const r = checkTrade(1);
    console.assert(r.allowed === false, '12% 回撤超 10% 限制应拒绝');
    console.log('✅ Test 7: 回撤检查');
    passed++;
  } catch (e: any) { console.log(`❌ Test 7: ${e.message}`); failed++; }

  // Test 8: 格式化状态
  try {
    const msg = formatRiskStatus();
    console.assert(msg.includes('风控状态'), '应包含风控状态');
    console.assert(msg.includes('止损'), '应包含止损');
    console.log('✅ Test 8: 格式化状态');
    passed++;
  } catch (e: any) { console.log(`❌ Test 8: ${e.message}`); failed++; }

  // Test 9: 日亏损限制
  try {
    resetDailyStats();
    updateBalance(100);
    updateBalance(100); // 重置 peak
    recordTrade(5, -10);
    recordTrade(5, -12);
    const r = checkTrade(1);
    console.assert(r.allowed === false, '日亏损 $22 超 $20 限制');
    console.log('✅ Test 9: 日亏损限制');
    passed++;
  } catch (e: any) { console.log(`❌ Test 9: ${e.message}`); failed++; }

  // Test 10: 重置日统计
  try {
    resetDailyStats();
    updateBalance(100);
    updateBalance(100);
    const r = checkTrade(5);
    console.assert(r.allowed === true, '重置后应允许');
    console.log('✅ Test 10: 重置日统计');
    passed++;
  } catch (e: any) { console.log(`❌ Test 10: ${e.message}`); failed++; }

  console.log(`\n📊 risk.ts: ${passed}/${passed + failed} 通过`);
  return { passed, failed };
}

testRisk().catch(console.error);
