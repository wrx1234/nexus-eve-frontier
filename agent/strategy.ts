/**
 * 策略引擎 — AI 驱动的 DeFi 交易决策
 * 分析市场 → 生成信号 → 执行交易 → 记录日志
 */

import { SuiClient } from '@mysten/sui/client';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { createAggregator, getSwapQuote, TOKENS, TOKEN_NAMES } from './swap.js';
import { getBalance } from './wallet.js';
import { logAction } from './logger.js';
import { broadcastTrade } from './social.js';

// ===================== 策略配置 =====================

export interface StrategyConfig {
  // 交易参数
  maxTradeAmount: number;     // 单笔最大金额（SUI）
  dailyLimit: number;         // 日交易限额（SUI）
  minProfitBps: number;       // 最小利润（基点，100 = 1%）
  slippageBps: number;        // 滑点容忍（基点）
  
  // 策略参数
  checkIntervalMs: number;    // 检查间隔（毫秒）
  enableAutoTrade: boolean;   // 自动交易开关
  strategy: 'trend' | 'mean_reversion' | 'momentum'; // 策略类型
  
  // 安全
  stopLossPercent: number;    // 止损百分比
  maxOpenPositions: number;   // 最大持仓数
}

export const DEFAULT_CONFIG: StrategyConfig = {
  maxTradeAmount: 10,         // 最多 10 SUI/笔
  dailyLimit: 50,             // 日限 50 SUI
  minProfitBps: 50,           // 0.5% 最小利润
  slippageBps: 100,           // 1% 滑点
  checkIntervalMs: 60000,     // 1 分钟检查
  enableAutoTrade: false,     // 默认关闭
  strategy: 'trend',
  stopLossPercent: 2,         // 2% 止损
  maxOpenPositions: 3,
};

// ===================== 市场数据 =====================

interface PricePoint {
  timestamp: number;
  price: number;
}

interface MarketSignal {
  token: string;
  direction: 'buy' | 'sell' | 'hold';
  confidence: number;        // 0-1
  reasoning: string;
  suggestedAmount: number;   // SUI
}

// 价格历史缓存
const priceHistory: Map<string, PricePoint[]> = new Map();

// 获取 token 价格（通过 Cetus 报价）
async function getTokenPrice(token: string): Promise<number | null> {
  try {
    const aggregator = createAggregator();
    const amount = BigInt(1_000_000_000); // 1 SUI
    
    if (token === 'SUI') {
      // SUI/USDC 价格
      const quote = await getSwapQuote(aggregator, TOKENS.SUI, TOKENS.USDC, amount);
      if (quote) {
        return Number(quote.outputAmount) / 1e6; // USDC 6 位小数
      }
    }
    return null;
  } catch {
    return null;
  }
}

// 记录价格点
function recordPrice(token: string, price: number) {
  const history = priceHistory.get(token) || [];
  history.push({ timestamp: Date.now(), price });
  
  // 保留最近 100 个价格点
  if (history.length > 100) history.shift();
  priceHistory.set(token, history);
}

// ===================== 策略分析 =====================

// 趋势跟踪策略
function analyzeTrend(token: string): MarketSignal {
  const history = priceHistory.get(token) || [];
  
  if (history.length < 5) {
    return {
      token,
      direction: 'hold',
      confidence: 0,
      reasoning: '数据不足，需要至少 5 个价格点',
      suggestedAmount: 0,
    };
  }
  
  // 简单移动平均
  const recent5 = history.slice(-5).map(p => p.price);
  const recent10 = history.slice(-10).map(p => p.price);
  const avg5 = recent5.reduce((a, b) => a + b, 0) / recent5.length;
  const avg10 = recent10.length >= 10 
    ? recent10.reduce((a, b) => a + b, 0) / recent10.length 
    : avg5;
  
  // 价格变化率
  const priceChange = (recent5[recent5.length - 1] - recent5[0]) / recent5[0];
  
  let direction: 'buy' | 'sell' | 'hold' = 'hold';
  let confidence = 0;
  let reasoning = '';
  
  if (avg5 > avg10 * 1.01 && priceChange > 0.005) {
    direction = 'buy';
    confidence = Math.min(priceChange * 10, 0.9);
    reasoning = `上升趋势: MA5(${avg5.toFixed(4)}) > MA10(${avg10.toFixed(4)}), 涨幅 ${(priceChange * 100).toFixed(2)}%`;
  } else if (avg5 < avg10 * 0.99 && priceChange < -0.005) {
    direction = 'sell';
    confidence = Math.min(Math.abs(priceChange) * 10, 0.9);
    reasoning = `下降趋势: MA5(${avg5.toFixed(4)}) < MA10(${avg10.toFixed(4)}), 跌幅 ${(priceChange * 100).toFixed(2)}%`;
  } else {
    direction = 'hold';
    confidence = 0.3;
    reasoning = `无明显趋势: MA5=${avg5.toFixed(4)}, MA10=${avg10.toFixed(4)}`;
  }
  
  return {
    token,
    direction,
    confidence,
    reasoning,
    suggestedAmount: direction !== 'hold' ? DEFAULT_CONFIG.maxTradeAmount * confidence : 0,
  };
}

// 均值回归策略
function analyzeMeanReversion(token: string): MarketSignal {
  const history = priceHistory.get(token) || [];
  
  if (history.length < 10) {
    return { token, direction: 'hold', confidence: 0, reasoning: '数据不足', suggestedAmount: 0 };
  }
  
  const prices = history.map(p => p.price);
  const mean = prices.reduce((a, b) => a + b, 0) / prices.length;
  const current = prices[prices.length - 1];
  const deviation = (current - mean) / mean;
  
  let direction: 'buy' | 'sell' | 'hold' = 'hold';
  let confidence = 0;
  
  if (deviation < -0.02) {
    // 价格低于均值 2%+ → 买入（回归均值）
    direction = 'buy';
    confidence = Math.min(Math.abs(deviation) * 20, 0.9);
  } else if (deviation > 0.02) {
    // 价格高于均值 2%+ → 卖出
    direction = 'sell';
    confidence = Math.min(deviation * 20, 0.9);
  }
  
  return {
    token,
    direction,
    confidence,
    reasoning: `偏离均值 ${(deviation * 100).toFixed(2)}%, 均值=${mean.toFixed(4)}, 当前=${current.toFixed(4)}`,
    suggestedAmount: direction !== 'hold' ? DEFAULT_CONFIG.maxTradeAmount * confidence : 0,
  };
}

// 选择策略分析
export function analyzeMarket(token: string, strategy: string = 'trend'): MarketSignal {
  switch (strategy) {
    case 'mean_reversion':
      return analyzeMeanReversion(token);
    case 'trend':
    default:
      return analyzeTrend(token);
  }
}

// ===================== 交易状态 =====================

interface TradingState {
  dailyVolume: number;       // 今日交易量（SUI）
  dailyPnl: number;          // 今日盈亏（USD）
  tradesCount: number;       // 今日交易次数
  lastTradeTime: number;     // 上次交易时间
  positions: Array<{
    token: string;
    amount: number;
    entryPrice: number;
    timestamp: number;
  }>;
}

const tradingState: TradingState = {
  dailyVolume: 0,
  dailyPnl: 0,
  tradesCount: 0,
  lastTradeTime: 0,
  positions: [],
};

// 获取交易状态
export function getTradingState(): TradingState {
  return { ...tradingState };
}

// 格式化状态消息
export function formatStatusMessage(): string {
  const state = tradingState;
  return `🤖 *策略状态*
━━━━━━━━━━━━━━━
📊 今日交易: ${state.tradesCount} 笔
💰 今日盈亏: ${state.dailyPnl >= 0 ? '+' : ''}$${state.dailyPnl.toFixed(2)}
📈 交易量: ${state.dailyVolume.toFixed(2)} SUI
🔄 持仓数: ${state.positions.length}/${DEFAULT_CONFIG.maxOpenPositions}
⚙️ 自动交易: ${DEFAULT_CONFIG.enableAutoTrade ? '✅ 开启' : '⏸️ 关闭'}
📋 策略: ${DEFAULT_CONFIG.strategy}`;
}

// ===================== 策略主循环 =====================

export async function strategyLoop(
  client: SuiClient,
  keypair: Ed25519Keypair,
  config: StrategyConfig = DEFAULT_CONFIG,
) {
  console.log('🤖 策略引擎启动');
  console.log(`策略: ${config.strategy}`);
  console.log(`自动交易: ${config.enableAutoTrade ? '✅' : '⏸️'}`);
  console.log(`单笔上限: ${config.maxTradeAmount} SUI`);
  console.log(`日限: ${config.dailyLimit} SUI`);
  
  logAction('strategy_start', {
    strategy: config.strategy,
    autoTrade: config.enableAutoTrade,
    maxTrade: config.maxTradeAmount,
    dailyLimit: config.dailyLimit,
  });
  
  while (true) {
    try {
      // 1. 获取价格
      const price = await getTokenPrice('SUI');
      if (price) {
        recordPrice('SUI', price);
        console.log(`💲 SUI: $${price.toFixed(4)}`);
      }
      
      // 2. 分析市场
      const signal = analyzeMarket('SUI', config.strategy);
      console.log(`📊 信号: ${signal.direction} (${(signal.confidence * 100).toFixed(0)}%) — ${signal.reasoning}`);
      
      logAction('market_analysis', {
        token: signal.token,
        direction: signal.direction,
        confidence: signal.confidence,
        reasoning: signal.reasoning,
      });
      
      // 3. 执行交易（如果启用自动交易且信号足够强）
      if (config.enableAutoTrade && signal.direction !== 'hold' && signal.confidence >= 0.6) {
        // 检查日限
        if (tradingState.dailyVolume + signal.suggestedAmount > config.dailyLimit) {
          console.log('⚠️ 已达日限，跳过');
          continue;
        }
        
        // 检查持仓数
        if (tradingState.positions.length >= config.maxOpenPositions) {
          console.log('⚠️ 持仓已满，跳过');
          continue;
        }
        
        console.log(`🎯 执行: ${signal.direction} ${signal.suggestedAmount.toFixed(2)} SUI`);
        
        // TODO: 调用 executeSwap
        // const result = await executeSwap(aggregator, client, keypair, ...);
        
        // 更新状态
        tradingState.dailyVolume += signal.suggestedAmount;
        tradingState.tradesCount++;
        tradingState.lastTradeTime = Date.now();
        
        logAction('trade_execute', {
          direction: signal.direction,
          amount: signal.suggestedAmount,
          confidence: signal.confidence,
        });
        
        // 4. 社交播报
        await broadcastTrade({
          action: signal.direction === 'buy' ? 'buy' : 'sell',
          fromToken: signal.direction === 'buy' ? 'USDC' : 'SUI',
          toToken: signal.direction === 'buy' ? 'SUI' : 'USDC',
          amount: signal.suggestedAmount.toFixed(2),
          result: '待确认',
          pnlToday: `${tradingState.dailyPnl >= 0 ? '+' : ''}$${tradingState.dailyPnl.toFixed(2)}`,
        });
      }
      
    } catch (e: any) {
      console.error(`策略循环错误: ${e.message}`);
      logAction('strategy_error', { error: e.message });
    }
    
    // 等待下一轮
    await new Promise(r => setTimeout(r, config.checkIntervalMs));
  }
}

// 测试
async function main() {
  console.log('🤖 测试策略引擎...\n');
  
  // 模拟价格数据
  const prices = [1.50, 1.52, 1.55, 1.53, 1.58, 1.60, 1.62, 1.59, 1.65, 1.68];
  for (const p of prices) {
    recordPrice('SUI', p);
  }
  
  // 趋势分析
  console.log('--- 趋势策略 ---');
  const trendSignal = analyzeMarket('SUI', 'trend');
  console.log(trendSignal);
  
  // 均值回归
  console.log('\n--- 均值回归策略 ---');
  const mrSignal = analyzeMarket('SUI', 'mean_reversion');
  console.log(mrSignal);
  
  // 状态
  console.log('\n' + formatStatusMessage());
  
  console.log('\n✅ 策略引擎测试完成');
}

if (process.argv[1]?.includes('strategy')) {
  main().catch(console.error);
}
