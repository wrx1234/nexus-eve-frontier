/**
 * 运行所有测试
 */
console.log('🧪 Sui DeFi Jarvis — 测试套件\n');
console.log('═'.repeat(40));

async function runAll() {
  const modules = ['wallet', 'strategy', 'risk', 'logger', 'social'];
  
  for (const mod of modules) {
    console.log(`\n▶ ${mod}.test.ts`);
    console.log('─'.repeat(30));
    try {
      await import(`./${mod}.test.js`);
    } catch (e: any) {
      console.log(`💀 ${mod} 测试崩溃: ${e.message}`);
    }
    // 等一下让异步完成
    await new Promise(r => setTimeout(r, 2000));
  }
  
  console.log('\n' + '═'.repeat(40));
  console.log('🏁 所有测试完成');
}

runAll().catch(console.error);
