/**
 * wallet.ts 单元测试
 */
import { generateWallet, importWallet, createClient, getBalance } from '../agent/wallet.js';

async function testWallet() {
  let passed = 0, failed = 0;

  // Test 1: 生成钱包
  try {
    const w = generateWallet();
    console.assert(w.address.startsWith('0x'), '地址应以 0x 开头');
    console.assert(w.address.length === 66, '地址长度应为 66');
    console.assert(w.privateKey.length > 0, '私钥不应为空');
    console.assert(w.keypair !== null, 'keypair 不应为空');
    console.log('✅ Test 1: 生成钱包');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 1: 生成钱包 — ${e.message}`);
    failed++;
  }

  // Test 2: 生成两个钱包地址不同
  try {
    const w1 = generateWallet();
    const w2 = generateWallet();
    console.assert(w1.address !== w2.address, '两个钱包地址应不同');
    console.log('✅ Test 2: 钱包唯一性');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 2: 钱包唯一性 — ${e.message}`);
    failed++;
  }

  // Test 3: 导入钱包
  try {
    const w1 = generateWallet();
    const w2 = importWallet(w1.privateKey);
    console.assert(w1.address === w2.address, `导入后地址应相同: ${w1.address} vs ${w2.address}`);
    console.log('✅ Test 3: 导入钱包');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 3: 导入钱包 — ${e.message}`);
    failed++;
  }

  // Test 4: 创建客户端
  try {
    const client = createClient('testnet');
    console.assert(client !== null, '客户端不应为空');
    console.log('✅ Test 4: 创建客户端');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 4: 创建客户端 — ${e.message}`);
    failed++;
  }

  // Test 5: 查询余额（新地址应为0）
  try {
    const client = createClient('testnet');
    const w = generateWallet();
    const bal = await getBalance(client, w.address);
    console.assert(bal.sui === 0n, `新地址余额应为 0, got ${bal.sui}`);
    console.assert(bal.suiFormatted === '0.000000000', `格式化余额应为 0.000000000, got ${bal.suiFormatted}`);
    console.log('✅ Test 5: 查询余额');
    passed++;
  } catch (e: any) {
    console.log(`❌ Test 5: 查询余额 — ${e.message}`);
    failed++;
  }

  console.log(`\n📊 wallet.ts: ${passed}/${passed + failed} 通过`);
  return { passed, failed };
}

testWallet().catch(console.error);
