/**
 * Assembly 管理模块 - 管理 EVE Frontier Smart Assemblies
 * 提供上线/下线/元数据更新/扩展注册等操作
 */

import { SuiClient } from '@mysten/sui/client';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { Transaction } from '@mysten/sui/transactions';
import { logAction } from './logger.js';

const WORLD_PACKAGE_ID = process.env.WORLD_PACKAGE_ID || '';
const COMMANDER_PACKAGE_ID = process.env.COMMANDER_PACKAGE_ID || '';

// ===================== 类型定义 =====================

export type AssemblyType = 'gate' | 'storage_unit' | 'turret' | 'assembly';

export interface AssemblyState {
  id: string;
  type: AssemblyType;
  name: string;
  isOnline: boolean;
  typeId: number;
  ownerCapId: string;
  energySourceId?: string;
  extension?: string;
  // Gate 专属
  linkedGateId?: string;
  // 统计
  lastChecked: number;
}

// ===================== 内存状态 =====================

const managedAssemblies: Map<string, AssemblyState> = new Map();

export function getManagedAssemblies(): AssemblyState[] {
  return Array.from(managedAssemblies.values());
}

export function getAssembly(id: string): AssemblyState | undefined {
  return managedAssemblies.get(id);
}

export function registerAssembly(state: AssemblyState) {
  managedAssemblies.set(state.id, state);
  logAction('assembly_registered', { id: state.id, type: state.type, name: state.name });
}

// ===================== 交易构建 =====================

/**
 * 构建 Assembly 上线交易
 * 需要: characterId, ownerCapId, assemblyId, networkNodeId
 */
export function buildOnlineTransaction(
  assemblyType: AssemblyType,
  characterId: string,
  ownerCapId: string,
  assemblyId: string,
  networkNodeId: string,
  energyConfigId: string,
): Transaction {
  if (!WORLD_PACKAGE_ID) throw new Error('WORLD_PACKAGE_ID not set');

  const tx = new Transaction();
  const module = assemblyType === 'storage_unit' ? 'storage_unit' : assemblyType;
  const typeArg = `${WORLD_PACKAGE_ID}::${module}::${capitalize(assemblyType)}`;

  // 1. Borrow OwnerCap from character
  const [ownerCap] = tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::borrow_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), tx.object(ownerCapId)],
  });

  // 2. Bring assembly online
  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::${module}::online`,
    arguments: [
      tx.object(assemblyId),
      tx.object(networkNodeId),
      tx.object(energyConfigId),
      ownerCap,
    ],
  });

  // 3. Return OwnerCap
  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::return_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), ownerCap],
  });

  return tx;
}

/**
 * 构建 Assembly 下线交易
 */
export function buildOfflineTransaction(
  assemblyType: AssemblyType,
  characterId: string,
  ownerCapId: string,
  assemblyId: string,
  networkNodeId: string,
  energyConfigId: string,
): Transaction {
  if (!WORLD_PACKAGE_ID) throw new Error('WORLD_PACKAGE_ID not set');

  const tx = new Transaction();
  const module = assemblyType === 'storage_unit' ? 'storage_unit' : assemblyType;
  const typeArg = `${WORLD_PACKAGE_ID}::${module}::${capitalize(assemblyType)}`;

  const [ownerCap] = tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::borrow_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), tx.object(ownerCapId)],
  });

  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::${module}::offline`,
    arguments: [
      tx.object(assemblyId),
      tx.object(networkNodeId),
      tx.object(energyConfigId),
      ownerCap,
    ],
  });

  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::return_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), ownerCap],
  });

  return tx;
}

/**
 * 构建 Gate 扩展授权交易 (注册 Commander 为 Gate 扩展)
 */
export function buildAuthorizeGateExtensionTransaction(
  characterId: string,
  ownerCapId: string,
  gateId: string,
): Transaction {
  if (!WORLD_PACKAGE_ID || !COMMANDER_PACKAGE_ID) {
    throw new Error('WORLD_PACKAGE_ID and COMMANDER_PACKAGE_ID must be set');
  }

  const tx = new Transaction();
  const typeArg = `${WORLD_PACKAGE_ID}::gate::Gate`;

  const [ownerCap] = tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::borrow_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), tx.object(ownerCapId)],
  });

  // authorize_extension<CAuth>
  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::gate::authorize_extension`,
    typeArguments: [`${COMMANDER_PACKAGE_ID}::config::CAuth`],
    arguments: [tx.object(gateId), ownerCap],
  });

  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::return_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), ownerCap],
  });

  return tx;
}

/**
 * 构建 Gate Commander 配置交易
 */
export function buildSetGateConfigTransaction(
  extensionConfigId: string,
  adminCapId: string,
  config: {
    allowedTribe: number;
    permitDurationMs: number;
    allowlistEnabled: boolean;
    timeControlEnabled: boolean;
    openFromMs: number;
    openUntilMs: number;
  },
): Transaction {
  if (!COMMANDER_PACKAGE_ID) throw new Error('COMMANDER_PACKAGE_ID not set');

  const tx = new Transaction();

  tx.moveCall({
    target: `${COMMANDER_PACKAGE_ID}::gate_commander::set_gate_config`,
    arguments: [
      tx.object(extensionConfigId),
      tx.object(adminCapId),
      tx.pure.u32(config.allowedTribe),
      tx.pure.u64(config.permitDurationMs),
      tx.pure.bool(config.allowlistEnabled),
      tx.pure.bool(config.timeControlEnabled),
      tx.pure.u64(config.openFromMs),
      tx.pure.u64(config.openUntilMs),
    ],
  });

  return tx;
}

/**
 * 构建更新元数据交易
 */
export function buildUpdateMetadataTransaction(
  assemblyType: AssemblyType,
  characterId: string,
  ownerCapId: string,
  assemblyId: string,
  name: string,
  description: string,
): Transaction {
  if (!WORLD_PACKAGE_ID) throw new Error('WORLD_PACKAGE_ID not set');

  const tx = new Transaction();
  const module = assemblyType === 'storage_unit' ? 'storage_unit' : assemblyType;
  const typeArg = `${WORLD_PACKAGE_ID}::${module}::${capitalize(assemblyType)}`;

  const [ownerCap] = tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::borrow_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), tx.object(ownerCapId)],
  });

  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::${module}::update_metadata_name`,
    arguments: [tx.object(assemblyId), ownerCap, tx.pure.string(name)],
  });

  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::${module}::update_metadata_description`,
    arguments: [tx.object(assemblyId), ownerCap, tx.pure.string(description)],
  });

  tx.moveCall({
    target: `${WORLD_PACKAGE_ID}::character::return_owner_cap`,
    typeArguments: [typeArg],
    arguments: [tx.object(characterId), ownerCap],
  });

  return tx;
}

// ===================== 执行 =====================

/**
 * 签名并执行交易
 */
export async function executeTransaction(
  client: SuiClient,
  keypair: Ed25519Keypair,
  tx: Transaction,
): Promise<{ digest: string; status: string }> {
  const result = await client.signAndExecuteTransaction({
    signer: keypair,
    transaction: tx,
    options: { showEffects: true, showEvents: true },
  });

  const status = result.effects?.status?.status || 'unknown';
  logAction('tx_executed', { digest: result.digest, status });

  return { digest: result.digest, status };
}

// ===================== 格式化 =====================

export function formatAssemblyStatus(assemblies: AssemblyState[]): string {
  if (assemblies.length === 0) return '📦 暂无管理的 Assembly';

  const byType = new Map<string, AssemblyState[]>();
  for (const a of assemblies) {
    const list = byType.get(a.type) || [];
    list.push(a);
    byType.set(a.type, list);
  }

  let text = '📦 *Assembly 总览*\n━━━━━━━━━━━━━━━\n';
  
  for (const [type, list] of byType) {
    const emoji = type === 'gate' ? '🚪' : type === 'storage_unit' ? '📦' : type === 'turret' ? '🔫' : '⚡';
    const online = list.filter(a => a.isOnline).length;
    text += `${emoji} ${capitalize(type)}: ${online}/${list.length} 在线\n`;
    for (const a of list) {
      const status = a.isOnline ? '🟢' : '🔴';
      const ext = a.extension ? ' 📝' : '';
      text += `  ${status} ${a.name || 'Unnamed'}${ext}\n`;
    }
  }

  return text;
}

// ===================== 工具函数 =====================

function capitalize(s: string): string {
  if (s === 'storage_unit') return 'StorageUnit';
  if (s === 'network_node') return 'NetworkNode';
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// 测试
async function main() {
  console.log('📦 Testing Assembly module...');
  
  // 模拟注册
  registerAssembly({
    id: '0xabc123',
    type: 'gate',
    name: 'Alpha Gate',
    isOnline: true,
    typeId: 1,
    ownerCapId: '0xdef456',
    linkedGateId: '0x789abc',
    lastChecked: Date.now(),
  });

  registerAssembly({
    id: '0xdef456',
    type: 'storage_unit',
    name: 'Trade Hub',
    isOnline: false,
    typeId: 2,
    ownerCapId: '0x111222',
    lastChecked: Date.now(),
  });

  registerAssembly({
    id: '0x789abc',
    type: 'turret',
    name: 'Defense Turret Alpha',
    isOnline: true,
    typeId: 3,
    ownerCapId: '0x333444',
    lastChecked: Date.now(),
  });

  console.log(formatAssemblyStatus(getManagedAssemblies()));
  console.log('\n✅ Assembly module test complete');
}

if (process.argv[1]?.includes('assembly')) {
  main().catch(console.error);
}
