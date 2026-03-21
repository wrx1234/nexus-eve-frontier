/**
 * Swap 模块 — Cetus Aggregator 最优路径交易
 * 集成全部 Sui DEX (Cetus/DeepBook/Kriya/FlowX/Turbos/Aftermath)
 */

import { AggregatorClient } from '@cetusprotocol/aggregator-sdk';
import { SuiJsonRpcClient } from '@mysten/sui/jsonRpc';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { Transaction } from '@mysten/sui/transactions';

// 常用 Token 地址
export const TOKENS = {
  SUI: '0x2::sui::SUI',
  USDC: '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN', // Wormhole USDC
  CETUS: '0x06864a6f921804860930db6ddbe2e16acdf8504495ea7481637a1c8b9a8fe54b::cetus::CETUS',
  USDT: '0xc060006111016b8a020ad5b33834984a437aaa7d3c74c18e09a95d48aceab08c::coin::COIN', // Wormhole USDT
} as const;

// Token 名称映射
export const TOKEN_NAMES: Record<string, string> = {
  [TOKENS.SUI]: 'SUI',
  [TOKENS.USDC]: 'USDC',
  [TOKENS.CETUS]: 'CETUS',
  [TOKENS.USDT]: 'USDT',
};

// 创建 Aggregator 客户端
export function createAggregator(): AggregatorClient {
  return new AggregatorClient({});
}

// 获取最优 swap 路径和报价
export async function getSwapQuote(
  aggregator: AggregatorClient,
  fromToken: string,
  toToken: string,
  amount: bigint, // 以最小单位（如 SUI 的 MIST）
) {
  const result = await aggregator.findRouters({
    from: fromToken,
    target: toToken,
    amount: BigInt(amount),
    byAmountIn: true,
  });

  // SDK 返回字段: amountOut (hex BN), paths (非 routes)
  const r = result as any;
  if (!r || r.error || (!r.paths && !r.routes) || (r.paths?.length === 0 && r.routes?.length === 0)) {
    return null;
  }

  // amountOut 可能是 hex BN 字符串或数字
  const amountOutRaw = r.amountOut || r.outputAmount || '0';
  const amountOutNum = typeof amountOutRaw === 'string' && amountOutRaw.match(/^[0-9a-f]+$/i) && !amountOutRaw.match(/^\d+$/)
    ? parseInt(amountOutRaw, 16) 
    : Number(amountOutRaw);

  return {
    routes: r.paths || r.routes || [],
    outputAmount: amountOutNum,
    outputFormatted: (amountOutNum / 1e9).toFixed(6),
    inputAmount: amount.toString(),
    inputFormatted: (Number(amount) / 1e9).toFixed(6),
    fromToken,
    toToken,
    quoteID: r.quoteID,
    rawResult: r,
  };
}

// 执行 swap 交易
export async function executeSwap(
  aggregator: AggregatorClient,
  client: SuiJsonRpcClient,
  keypair: Ed25519Keypair,
  fromToken: string,
  toToken: string,
  amount: bigint,
  slippageBps: number = 100, // 1% 默认滑点
) {
  const address = keypair.getPublicKey().toSuiAddress();
  
  // 获取路由
  const quote = await getSwapQuote(aggregator, fromToken, toToken, amount);
  if (!quote) {
    throw new Error('No swap route found');
  }

  // 构建交易
  const tx = new Transaction();
  tx.setSender(address);

  // 使用 aggregator 构建 swap 交易
  const result = await aggregator.findRouters({
    from: fromToken,
    target: toToken,
    amount: BigInt(amount),
    byAmountIn: true,
  });

  if (!result) {
    throw new Error('Failed to find swap route');
  }

  // 快速路由构建交易
  const buildResult = await aggregator.routerSwap({
    routers: result.routes!,
    byAmountIn: true,
    inputCoinType: fromToken,
    outputCoinType: toToken,
    inputAmount: BigInt(amount),
    slippage: slippageBps / 10000,
    txb: tx,
    partner: '',
  });

  // 签名并执行
  const txResult = await client.signAndExecuteTransaction({
    signer: keypair,
    transaction: tx,
    options: { showEffects: true, showEvents: true },
  });

  return {
    digest: txResult.digest,
    status: txResult.effects?.status?.status,
    quote,
    txResult,
  };
}

// 格式化 swap 预览消息
export function formatSwapPreview(
  fromName: string,
  toName: string,
  inputAmount: string,
  outputAmount: string | bigint | number,
  slippage?: number,
): string {
  return `🔄 Swap 预览
━━━━━━━━━━━━━━━
卖出: ${inputAmount} ${fromName}
获得: ~${outputAmount} ${toName}
路径: ${fromName} → ${toName} (Cetus Aggregator)
━━━━━━━━━━━━━━━`;
}

// 测试
async function main() {
  console.log('🔄 测试 Cetus Aggregator...');
  
  const aggregator = createAggregator();
  
  // 测试获取 SUI → USDC 报价
  const amount = BigInt(1_000_000_000); // 1 SUI
  console.log(`\n获取报价: 1 SUI → USDC`);
  
  try {
    const quote = await getSwapQuote(aggregator, TOKENS.SUI, TOKENS.USDC, amount);
    if (quote) {
      console.log(`输出: ${quote.outputFormatted} USDC`);
      console.log(`路由数: ${quote.routes.length}`);
    } else {
      console.log('未找到路由');
    }
  } catch (e: any) {
    console.log(`报价失败: ${e.message}`);
  }
  
  console.log('\n✅ Swap 模块测试完成');
}

if (process.argv[1]?.includes('swap')) {
  main().catch(console.error);
}
