/**
 * 风控模块 — 保护 Agent 资金安全
 * 止损/限额/异常检测/紧急暂停
 */

import { logAction } from './logger.js';

// ===================== 风控配置 =====================

export interface RiskConfig {
  // 限额
  maxSingleTrade: number;    // 单笔最大（SUI）
  maxDailyVolume: number;    // 日最大交易量（SUI）
  maxDailyLoss: number;      // 日最大亏损（USD）
  maxDrawdown: number;       // 最大回撤百分比
  
  // 止损
  stopLossPercent: number;   // 单笔止损（%）
  trailingStop: boolean;     // 追踪止损
  
  // 异常检测
  maxTradesPerHour: number;  // 每小时最大交易次数
  maxSlippage: number;       // 最大可接受滑点（%）
  
  // 开关
  enabled: boolean;
  emergencyStop: boolean;    // 紧急停止
}

export const DEFAULT_RISK: RiskConfig = {
  maxSingleTrade: 10,
  maxDailyVolume: 50,
  maxDailyLoss: 20,
  maxDrawdown: 10,
  stopLossPercent: 2,
  trailingStop: false,
  maxTradesPerHour: 10,
  maxSlippage: 2,
  enabled: true,
  emergencyStop: false,
};

// ===================== 风控状态 =====================

interface RiskState {
  dailyVolume: number;
  dailyLoss: number;
  hourlyTrades: number[];    // 最近一小时的交易时间戳
  peakBalance: number;       // 历史最高余额
  currentBalance: number;
  violations: Array<{
    timestamp: string;
    rule: string;
    details: string;
  }>;
}

const state: RiskState = {
  dailyVolume: 0,
  dailyLoss: 0,
  hourlyTrades: [],
  peakBalance: 0,
  currentBalance: 0,
  violations: [],
};

// ===================== 风控检查 =====================

export interface RiskCheckResult {
  allowed: boolean;
  reason?: string;
  warnings: string[];
}

// 交易前风控检查
export function checkTrade(
  amount: number,
  config: RiskConfig = DEFAULT_RISK,
): RiskCheckResult {
  const warnings: string[] = [];
  
  // 紧急停止
  if (config.emergencyStop) {
    return { allowed: false, reason: '🚨 紧急停止已激活', warnings };
  }
  
  if (!config.enabled) {
    return { allowed: true, warnings: ['⚠️ 风控已关闭'] };
  }
  
  // 单笔限额
  if (amount > config.maxSingleTrade) {
    return {
      allowed: false,
      reason: `❌ 超过单笔限额: ${amount} > ${config.maxSingleTrade} SUI`,
      warnings,
    };
  }
  
  // 日交易量
  if (state.dailyVolume + amount > config.maxDailyVolume) {
    return {
      allowed: false,
      reason: `❌ 超过日限额: ${state.dailyVolume + amount} > ${config.maxDailyVolume} SUI`,
      warnings,
    };
  }
  
  // 日亏损
  if (state.dailyLoss >= config.maxDailyLoss) {
    return {
      allowed: false,
      reason: `❌ 已达日亏损上限: $${state.dailyLoss} >= $${config.maxDailyLoss}`,
      warnings,
    };
  }
  
  // 每小时交易频率
  const now = Date.now();
  const recentTrades = state.hourlyTrades.filter(t => now - t < 3600000);
  if (recentTrades.length >= config.maxTradesPerHour) {
    return {
      allowed: false,
      reason: `❌ 超过每小时交易上限: ${recentTrades.length} >= ${config.maxTradesPerHour}`,
      warnings,
    };
  }
  
  // 回撤检查
  if (state.peakBalance > 0) {
    const drawdown = (state.peakBalance - state.currentBalance) / state.peakBalance * 100;
    if (drawdown >= config.maxDrawdown) {
      return {
        allowed: false,
        reason: `❌ 回撤超限: ${drawdown.toFixed(1)}% >= ${config.maxDrawdown}%`,
        warnings,
      };
    }
    if (drawdown >= config.maxDrawdown * 0.7) {
      warnings.push(`⚠️ 接近回撤上限: ${drawdown.toFixed(1)}%`);
    }
  }
  
  // 警告：接近限额
  if (state.dailyVolume + amount > config.maxDailyVolume * 0.8) {
    warnings.push(`⚠️ 接近日限额: ${((state.dailyVolume + amount) / config.maxDailyVolume * 100).toFixed(0)}%`);
  }
  
  return { allowed: true, warnings };
}

// 记录交易完成
export function recordTrade(amount: number, pnl: number) {
  state.dailyVolume += amount;
  state.hourlyTrades.push(Date.now());
  
  if (pnl < 0) {
    state.dailyLoss += Math.abs(pnl);
  }
  
  logAction('risk_trade_recorded', {
    amount,
    pnl,
    dailyVolume: state.dailyVolume,
    dailyLoss: state.dailyLoss,
  });
}

// 更新余额
export function updateBalance(balance: number) {
  state.currentBalance = balance;
  if (balance > state.peakBalance) {
    state.peakBalance = balance;
  }
}

// 止损检查
export function checkStopLoss(
  entryPrice: number,
  currentPrice: number,
  config: RiskConfig = DEFAULT_RISK,
): { triggered: boolean; lossPercent: number } {
  const lossPercent = (entryPrice - currentPrice) / entryPrice * 100;
  
  if (lossPercent >= config.stopLossPercent) {
    logAction('stop_loss_triggered', { entryPrice, currentPrice, lossPercent });
    return { triggered: true, lossPercent };
  }
  
  return { triggered: false, lossPercent };
}

// 紧急停止
export function emergencyStop(reason: string) {
  DEFAULT_RISK.emergencyStop = true;
  logAction('emergency_stop', { reason });
  console.log(`🚨 紧急停止: ${reason}`);
}

// 恢复交易
export function resumeTrading() {
  DEFAULT_RISK.emergencyStop = false;
  logAction('trading_resumed', {});
  console.log('✅ 交易已恢复');
}

// 重置日统计（每日凌晨调用）
export function resetDailyStats() {
  state.dailyVolume = 0;
  state.dailyLoss = 0;
  state.hourlyTrades = [];
  state.violations = [];
  logAction('daily_reset', {});
}

// 格式化风控状态
export function formatRiskStatus(config: RiskConfig = DEFAULT_RISK): string {
  const drawdown = state.peakBalance > 0 
    ? ((state.peakBalance - state.currentBalance) / state.peakBalance * 100).toFixed(1) 
    : '0.0';
  
  return `🛡️ *风控状态*
━━━━━━━━━━━━━━━
风控: ${config.enabled ? '✅ 开启' : '⚠️ 关闭'}
紧急停止: ${config.emergencyStop ? '🚨 已激活' : '✅ 正常'}

📊 *今日统计*
交易量: ${state.dailyVolume.toFixed(2)}/${config.maxDailyVolume} SUI
亏损: $${state.dailyLoss.toFixed(2)}/$${config.maxDailyLoss}
回撤: ${drawdown}%/${config.maxDrawdown}%

⚙️ *限额设置*
单笔上限: ${config.maxSingleTrade} SUI
日交易上限: ${config.maxDailyVolume} SUI
止损: ${config.stopLossPercent}%
每小时最多: ${config.maxTradesPerHour} 笔`;
}

// 测试
async function main() {
  console.log('🛡️ 测试风控模块...\n');
  
  // 测试交易检查
  console.log('--- 正常交易 ---');
  let result = checkTrade(5);
  console.log(result);
  
  console.log('\n--- 超额交易 ---');
  result = checkTrade(100);
  console.log(result);
  
  // 模拟交易
  recordTrade(5, -1);
  recordTrade(8, 2);
  recordTrade(10, -3);
  
  console.log('\n--- 交易后状态 ---');
  updateBalance(95);
  console.log(formatRiskStatus());
  
  // 止损检查
  console.log('\n--- 止损检查 ---');
  const sl = checkStopLoss(1.50, 1.46);
  console.log(`止损触发: ${sl.triggered}, 亏损: ${sl.lossPercent.toFixed(2)}%`);
  
  // 紧急停止
  emergencyStop('测试');
  result = checkTrade(1);
  console.log(`\n紧急停止后: ${result.allowed} — ${result.reason}`);
  
  resumeTrading();
  
  console.log('\n✅ 风控模块测试完成');
}

if (process.argv[1]?.includes('risk')) {
  main().catch(console.error);
}
