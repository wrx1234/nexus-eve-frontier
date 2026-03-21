/**
 * Mainnet 报价测试 — 只查价不交易
 */
import { createAggregator, getSwapQuote, TOKENS, TOKEN_NAMES } from '../agent/swap.js';

async function main() {
  console.log('🌐 Mainnet 报价测试（只查价不交易）\n');

  const client = createAggregator();

  const pairs = [
    { from: TOKENS.SUI, to: TOKENS.USDC, amount: BigInt(1_000_000_000), label: '1 SUI → USDC', outDecimals: 6 },
    { from: TOKENS.SUI, to: TOKENS.CETUS, amount: BigInt(1_000_000_000), label: '1 SUI → CETUS', outDecimals: 9 },
    { from: TOKENS.USDC, to: TOKENS.SUI, amount: BigInt(1_000_000), label: '1 USDC → SUI', outDecimals: 9 },
    { from: TOKENS.SUI, to: TOKENS.USDT, amount: BigInt(5_000_000_000), label: '5 SUI → USDT', outDecimals: 6 },
  ];

  for (const p of pairs) {
    try {
      console.log(`📊 ${p.label}...`);
      const quote = await getSwapQuote(client, p.from, p.to, p.amount);

      if (quote) {
        const outAmount = quote.outputAmount / Math.pow(10, p.outDecimals);
        console.log(`  ✅ 输出: ${outAmount.toFixed(6)}`);
        console.log(`  📍 路由数: ${quote.routes?.length || '?'}`);
        console.log(`  🆔 quoteID: ${quote.quoteID || 'N/A'}`);
        if (quote.routes?.[0]) {
          const r = quote.routes[0] as any;
          console.log(`  🏦 DEX: ${r.provider || 'N/A'}`);
        }
      } else {
        console.log(`  ⚠️ 无可用路由`);
      }
    } catch (e: any) {
      console.log(`  ❌ 错误: ${e.message}`);
    }
    console.log('');
  }

  console.log('✅ Mainnet 报价测试完成（未执行任何交易）');
}

main().catch(console.error);
