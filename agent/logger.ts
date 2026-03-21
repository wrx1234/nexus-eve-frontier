/**
 * Walrus Logger — 操作日志写入 Walrus 去中心化存储
 * 每笔操作记录到 Walrus，公开可审计
 */

import fs from 'fs';
import path from 'path';

const WALRUS_PUBLISHER = process.env.WALRUS_PUBLISHER || 'https://walrus-testnet-publisher.nodes.guru';
const WALRUS_AGGREGATOR = process.env.WALRUS_AGGREGATOR || 'https://aggregator.walrus-testnet.walrus.space';
const LOCAL_LOG_DIR = path.join(process.cwd(), 'logs');

interface LogEntry {
  timestamp: string;
  action: string;       // swap, deposit, withdraw, strategy, error
  details: Record<string, any>;
  agentAddress?: string;
  txDigest?: string;
}

// 内存日志缓冲
const logBuffer: LogEntry[] = [];

// 记录操作日志
export function logAction(action: string, details: Record<string, any>, txDigest?: string) {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    action,
    details,
    txDigest,
  };
  
  logBuffer.push(entry);
  
  // 同时写本地文件
  ensureLogDir();
  const today = new Date().toISOString().split('T')[0];
  const logFile = path.join(LOCAL_LOG_DIR, `${today}.jsonl`);
  fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
  
  console.log(`📝 [${action}] ${JSON.stringify(details).substring(0, 100)}`);
  
  return entry;
}

// 上传日志到 Walrus
export async function uploadToWalrus(data: string): Promise<string | null> {
  try {
    const response = await fetch(`${WALRUS_PUBLISHER}/v1/blobs`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/octet-stream' },
      body: data,
    });
    
    if (!response.ok) {
      console.error(`Walrus upload failed: ${response.status}`);
      return null;
    }
    
    const result = await response.json() as any;
    // Walrus 返回 blob ID
    const blobId = result?.newlyCreated?.blobObject?.blobId || 
                   result?.alreadyCertified?.blobId ||
                   null;
    
    if (blobId) {
      console.log(`🐘 Walrus blob: ${blobId}`);
    }
    
    return blobId;
  } catch (e: any) {
    console.error(`Walrus upload error: ${e.message}`);
    // Walrus 不可用时降级为本地存储
    return null;
  }
}

// 刷新日志缓冲到 Walrus
export async function flushLogs(): Promise<string | null> {
  if (logBuffer.length === 0) return null;
  
  const data = logBuffer.map(e => JSON.stringify(e)).join('\n');
  const blobId = await uploadToWalrus(data);
  
  if (blobId) {
    // 记录 blob ID 到本地索引
    ensureLogDir();
    const indexFile = path.join(LOCAL_LOG_DIR, 'walrus-index.jsonl');
    fs.appendFileSync(indexFile, JSON.stringify({
      timestamp: new Date().toISOString(),
      blobId,
      entries: logBuffer.length,
    }) + '\n');
    
    // 清空缓冲
    logBuffer.length = 0;
  }
  
  return blobId;
}

// 获取今日日志
export function getLogBuffer(): string[] {
  return logBuffer.map(e => JSON.stringify(e));
}

export function getTodayLogs(): LogEntry[] {
  ensureLogDir();
  const today = new Date().toISOString().split('T')[0];
  const logFile = path.join(LOCAL_LOG_DIR, `${today}.jsonl`);
  
  if (!fs.existsSync(logFile)) return [];
  
  return fs.readFileSync(logFile, 'utf-8')
    .split('\n')
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

// 格式化日志为可读文本
export function formatLogs(logs: LogEntry[]): string {
  if (logs.length === 0) return '📝 暂无操作记录';
  
  let text = '📝 操作日志\n━━━━━━━━━━━━━━━\n';
  
  for (const log of logs.slice(-10)) { // 最近 10 条
    const time = log.timestamp.split('T')[1]?.substring(0, 8) || '';
    const tx = log.txDigest ? ` [tx: ${log.txDigest.substring(0, 8)}...]` : '';
    text += `${time} | ${log.action} | ${JSON.stringify(log.details).substring(0, 60)}${tx}\n`;
  }
  
  return text;
}

function ensureLogDir() {
  if (!fs.existsSync(LOCAL_LOG_DIR)) {
    fs.mkdirSync(LOCAL_LOG_DIR, { recursive: true });
  }
}

// 测试
async function main() {
  console.log('📝 测试 Logger...');
  
  logAction('swap', { from: 'SUI', to: 'USDC', amount: '1.0', output: '1.52' }, '0xabc123');
  logAction('strategy', { decision: 'buy', reason: 'price dip detected' });
  
  const logs = getTodayLogs();
  console.log(`\n今日 ${logs.length} 条日志:`);
  console.log(formatLogs(logs));
  
  console.log('\n尝试上传到 Walrus...');
  const blobId = await flushLogs();
  console.log(blobId ? `✅ Walrus blob: ${blobId}` : '⚠️ Walrus 不可用，已保存本地');
  
  console.log('\n✅ Logger 测试完成');
}

if (process.argv[1]?.includes('logger')) {
  main().catch(console.error);
}
