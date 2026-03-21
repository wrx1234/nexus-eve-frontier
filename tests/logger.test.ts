/**
 * logger.ts 单元测试
 */
import { logAction, flushLogs, getLogBuffer } from '../agent/logger.js';

async function testLogger() {
  let passed = 0, failed = 0;

  // Test 1: 记录日志
  try {
    logAction('test_action', { key: 'value', num: 42 });
    const buf = getLogBuffer();
    console.assert(buf.length > 0, '日志缓冲区不应为空');
    console.assert(buf[buf.length - 1].includes('test_action'), '应包含 action');
    console.log('✅ Test 1: 记录日志');
    passed++;
  } catch (e: any) { console.log(`❌ Test 1: ${e.message}`); failed++; }

  // Test 2: 多条日志
  try {
    const before = getLogBuffer().length;
    logAction('action_a', { a: 1 });
    logAction('action_b', { b: 2 });
    logAction('action_c', { c: 3 });
    const after = getLogBuffer().length;
    console.assert(after >= before + 3, '应新增 3 条日志');
    console.log('✅ Test 2: 多条日志');
    passed++;
  } catch (e: any) { console.log(`❌ Test 2: ${e.message}`); failed++; }

  // Test 3: flush 日志（Walrus 可能不可用，降级到本地）
  try {
    const result = await flushLogs();
    // 不管 Walrus 是否可用，flush 不应抛异常
    console.log(`✅ Test 3: flush 日志 (blobId: ${result || 'local fallback'})`);
    passed++;
  } catch (e: any) { console.log(`❌ Test 3: ${e.message}`); failed++; }

  // Test 4: flush 后缓冲区应清空
  try {
    logAction('pre_flush', {});
    await flushLogs();
    const buf = getLogBuffer();
    console.assert(buf.length === 0, `flush 后应清空, got ${buf.length}`);
    console.log('✅ Test 4: flush 后清空');
    passed++;
  } catch (e: any) { console.log(`❌ Test 4: ${e.message}`); failed++; }

  console.log(`\n📊 logger.ts: ${passed}/${passed + failed} 通过`);
  return { passed, failed };
}

testLogger().catch(console.error);
