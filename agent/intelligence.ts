/**
 * 情报分析模块 - 分析 EVE Frontier 链上数据
 * 流量分析、威胁检测、市场趋势
 */

import { logAction } from './logger.js';
import { getJumpEvents, getAccessDeniedEvents, getPermitIssuedEvents, EventInfo } from './graphql.js';

// ===================== 类型定义 =====================

export interface TrafficReport {
  gateId: string;
  period: string;
  totalJumps: number;
  uniqueCharacters: number;
  topTribes: Array<{ tribe: number; count: number }>;
  peakHour: number;
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface ThreatReport {
  level: 'low' | 'medium' | 'high' | 'critical';
  denialCount: number;
  suspiciousActivity: string[];
  recommendations: string[];
}

export interface IntelReport {
  timestamp: string;
  traffic: TrafficReport[];
  threats: ThreatReport;
  summary: string;
}

// ===================== 流量分析 =====================

/**
 * 分析 Gate 跳跃流量
 */
export async function analyzeGateTraffic(gateId?: string): Promise<TrafficReport[]> {
  try {
    const events = await getJumpEvents(100);
    
    // 按 gate 分组
    const byGate = new Map<string, EventInfo[]>();
    for (const e of events) {
      const sourceGateId = e.data?.source_gate_id || 'unknown';
      if (gateId && sourceGateId !== gateId) continue;
      const list = byGate.get(sourceGateId) || [];
      list.push(e);
      byGate.set(sourceGateId, list);
    }

    const reports: TrafficReport[] = [];
    for (const [id, gateEvents] of byGate) {
      // 统计唯一角色
      const uniqueChars = new Set(gateEvents.map(e => e.data?.character_id));
      
      // 统计部落
      const tribeCounts = new Map<number, number>();
      for (const e of gateEvents) {
        const tribe = e.data?.character_tribe || 0;
        tribeCounts.set(tribe, (tribeCounts.get(tribe) || 0) + 1);
      }
      const topTribes = Array.from(tribeCounts.entries())
        .map(([tribe, count]) => ({ tribe, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      // 趋势分析 (简单: 比较前半段和后半段)
      const half = Math.floor(gateEvents.length / 2);
      const firstHalf = gateEvents.slice(0, half).length;
      const secondHalf = gateEvents.slice(half).length;
      const trend = secondHalf > firstHalf * 1.2 ? 'increasing' 
                   : secondHalf < firstHalf * 0.8 ? 'decreasing' 
                   : 'stable';

      reports.push({
        gateId: id,
        period: 'recent',
        totalJumps: gateEvents.length,
        uniqueCharacters: uniqueChars.size,
        topTribes,
        peakHour: 0, // 简化
        trend,
      });
    }

    logAction('traffic_analysis', { gateCount: reports.length, totalEvents: events.length });
    return reports;

  } catch (e: any) {
    console.error(`Traffic analysis error: ${e.message}`);
    return [];
  }
}

// ===================== 威胁检测 =====================

/**
 * 分析威胁等级
 */
export async function analyzeThreatLevel(commanderPackageId?: string): Promise<ThreatReport> {
  const suspiciousActivity: string[] = [];
  let denialCount = 0;

  if (commanderPackageId) {
    try {
      const deniedEvents = await getAccessDeniedEvents(commanderPackageId, 50);
      denialCount = deniedEvents.length;

      // 检测可疑模式
      const recentDenials = deniedEvents.filter(e => {
        const ts = Number(e.timestamp);
        return Date.now() - ts < 3600000; // 最近 1 小时
      });

      if (recentDenials.length > 10) {
        suspiciousActivity.push(`高频拒绝: ${recentDenials.length} 次/小时`);
      }

      // 检测同一角色多次尝试
      const charAttempts = new Map<string, number>();
      for (const e of recentDenials) {
        const charId = e.data?.character_id || 'unknown';
        charAttempts.set(charId, (charAttempts.get(charId) || 0) + 1);
      }
      for (const [charId, count] of charAttempts) {
        if (count > 3) {
          suspiciousActivity.push(`角色 ${charId.substring(0, 8)}... 重复尝试 ${count} 次`);
        }
      }
    } catch (e: any) {
      console.error(`Threat analysis error: ${e.message}`);
    }
  }

  // 评估威胁等级
  let level: ThreatReport['level'] = 'low';
  if (suspiciousActivity.length > 3 || denialCount > 50) level = 'critical';
  else if (suspiciousActivity.length > 1 || denialCount > 20) level = 'high';
  else if (suspiciousActivity.length > 0 || denialCount > 5) level = 'medium';

  // 生成建议
  const recommendations: string[] = [];
  if (level === 'critical' || level === 'high') {
    recommendations.push('建议收紧门禁规则');
    recommendations.push('考虑启用白名单模式');
  }
  if (suspiciousActivity.some(a => a.includes('重复尝试'))) {
    recommendations.push('建议将频繁尝试的角色加入黑名单');
  }
  if (level === 'low') {
    recommendations.push('当前安全态势良好');
  }

  const report: ThreatReport = { level, denialCount, suspiciousActivity, recommendations };
  logAction('threat_analysis', { level, denialCount, alerts: suspiciousActivity.length });
  return report;
}

// ===================== 综合情报报告 =====================

/**
 * 生成综合情报报告
 */
export async function generateIntelReport(commanderPackageId?: string): Promise<IntelReport> {
  const [traffic, threats] = await Promise.all([
    analyzeGateTraffic(),
    analyzeThreatLevel(commanderPackageId),
  ]);

  const totalJumps = traffic.reduce((sum, t) => sum + t.totalJumps, 0);
  const uniqueGates = traffic.length;

  let summary = `📊 情报摘要\n`;
  summary += `活跃 Gate: ${uniqueGates} | 总跳跃: ${totalJumps}\n`;
  summary += `威胁等级: ${formatThreatEmoji(threats.level)} ${threats.level.toUpperCase()}\n`;
  
  if (threats.suspiciousActivity.length > 0) {
    summary += `⚠️ 告警:\n`;
    for (const alert of threats.suspiciousActivity) {
      summary += `  - ${alert}\n`;
    }
  }

  for (const t of traffic) {
    summary += `\n🚪 Gate ${t.gateId.substring(0, 8)}...: ${t.totalJumps} 跳跃, ${t.uniqueCharacters} 用户, 趋势 ${formatTrend(t.trend)}`;
  }

  const report: IntelReport = {
    timestamp: new Date().toISOString(),
    traffic,
    threats,
    summary,
  };

  logAction('intel_report_generated', { 
    gateCount: uniqueGates, 
    totalJumps, 
    threatLevel: threats.level 
  });

  return report;
}

// ===================== 格式化 =====================

function formatThreatEmoji(level: string): string {
  switch (level) {
    case 'critical': return '🔴';
    case 'high': return '🟠';
    case 'medium': return '🟡';
    default: return '🟢';
  }
}

function formatTrend(trend: string): string {
  switch (trend) {
    case 'increasing': return '📈';
    case 'decreasing': return '📉';
    default: return '➡️';
  }
}

export function formatIntelReport(report: IntelReport): string {
  let text = `🕵️ *EVE Commander 情报报告*\n`;
  text += `📅 ${report.timestamp.split('T')[0]}\n`;
  text += `━━━━━━━━━━━━━━━\n\n`;
  text += report.summary;
  
  if (report.threats.recommendations.length > 0) {
    text += `\n\n💡 建议:\n`;
    for (const r of report.threats.recommendations) {
      text += `  • ${r}\n`;
    }
  }

  return text;
}

// 测试
async function main() {
  console.log('🕵️ Testing Intelligence module...');
  
  const report = await generateIntelReport();
  console.log(formatIntelReport(report));
  
  console.log('\n✅ Intelligence module test complete');
}

if (process.argv[1]?.includes('intelligence')) {
  main().catch(console.error);
}
