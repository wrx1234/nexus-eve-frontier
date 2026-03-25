/**
 * GraphQL 查询模块 - 读取 EVE Frontier 链上数据
 * 通过 Sui GraphQL API 查询 Assembly 状态、Character 信息等
 * 
 * EVE Frontier World Contracts 部署在 Sui Testnet
 * 官方文档: https://docs.evefrontier.com/tools/interfacing-with-the-eve-frontier-world
 */

// === 网络配置 ===

const GRAPHQL_ENDPOINTS: Record<string, string> = {
  testnet: 'https://graphql.testnet.sui.io/graphql',
  mainnet: 'https://graphql.mainnet.sui.io/graphql',
  devnet: 'https://graphql.devnet.sui.io/graphql',
};

const RPC_URLS: Record<string, string> = {
  testnet: 'https://fullnode.testnet.sui.io:443',
  mainnet: 'https://fullnode.mainnet.sui.io:443',
  devnet: 'https://fullnode.devnet.sui.io:443',
};

const NETWORK = process.env.SUI_NETWORK || 'testnet';

// EVE Frontier World Contracts 真实 Package IDs (Sui Testnet)
// 来源: https://github.com/evefrontier/world-contracts/blob/main/contracts/world/Published.toml
const WORLD_PACKAGE_IDS: Record<string, string> = {
  // 主 testnet 部署
  testnet: '0x920e577e1bf078bad19385aaa82e7332ef92b4973dcf8534797b129f9814d631',
  // 内部 testnet (同一链不同部署)
  testnet_internal: '0x353988e063b4683580e3603dbe9e91fefd8f6a06263a646d43fd3a2f3ef6b8c1',
  // Utopia testnet
  testnet_utopia: '0xd12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75',
  // Stillness testnet
  testnet_stillness: '0x28b497559d65ab320d9da4613bf2498d5946b2c0ae3597ccfda3072ce127448c',
};

// 使用环境变量覆盖, 或从已知部署中获取
const WORLD_PACKAGE_ID = process.env.WORLD_PACKAGE_ID || WORLD_PACKAGE_IDS[NETWORK] || WORLD_PACKAGE_IDS['testnet'];

// === 类型定义 ===

export interface AssemblyInfo {
  id: string;
  type: 'gate' | 'storage_unit' | 'turret' | 'network_node' | 'assembly';
  typeId: number;
  status: string;
  ownerCapId: string;
  energySourceId?: string;
  metadata?: {
    name: string;
    description: string;
    url: string;
  };
  // Gate 专属
  linkedGateId?: string;
  extension?: string;
  // StorageUnit 专属
  inventoryKeys?: string[];
}

export interface CharacterInfo {
  id: string;
  address: string;
  name: string;
  tribe: number;
  ownerCapId: string;
}

export interface EventInfo {
  type: string;
  timestamp: string;
  data: Record<string, any>;
  txDigest: string;
}

export interface GateInfo {
  id: string;
  status: any;
  location: any;
  extension: string | null;
  linkedGateId: string | null;
  metadata: any;
}

export interface NetworkNodeInfo {
  id: string;
  status: any;
  location: any;
  energyBalance: any;
  metadata: any;
}

// === GraphQL 查询引擎 ===

async function executeQuery(query: string, variables?: Record<string, any>): Promise<any> {
  const endpoint = GRAPHQL_ENDPOINTS[NETWORK];
  if (!endpoint) throw new Error(`Unknown network: ${NETWORK}`);

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    throw new Error(`GraphQL error: ${response.status} ${response.statusText}`);
  }

  const result = await response.json() as any;
  if (result.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
  }

  return result.data;
}

async function executeRpcCall(method: string, params: any[]): Promise<any> {
  const rpcUrl = RPC_URLS[NETWORK];
  if (!rpcUrl) throw new Error(`Unknown network: ${NETWORK}`);

  const response = await fetch(rpcUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method,
      params,
    }),
  });

  const result = await response.json() as any;
  if (result.error) {
    throw new Error(`RPC error: ${JSON.stringify(result.error)}`);
  }

  return result.result;
}

// === 对象查询 (GraphQL) ===

/**
 * 按类型查询所有对象
 * 文档: https://docs.evefrontier.com/tools/interfacing-with-the-eve-frontier-world
 */
export async function getObjectsByType(type: string, limit: number = 50): Promise<any[]> {
  const query = `
    query GetObjectsByType($type: String!, $first: Int) {
      objects(filter: { type: $type }, first: $first) {
        pageInfo { hasNextPage endCursor }
        nodes {
          address
          asMoveObject {
            contents {
              type { repr }
              json
            }
          }
        }
      }
    }
  `;

  const data = await executeQuery(query, { type, first: limit });
  return data?.objects?.nodes || [];
}

/**
 * 获取单个对象的 JSON 数据
 */
export async function getObjectJson(objectId: string): Promise<any> {
  const query = `
    query GetObject($id: SuiAddress!) {
      object(address: $id) {
        asMoveObject {
          contents {
            type { repr }
            json
          }
        }
      }
    }
  `;

  const data = await executeQuery(query, { id: objectId });
  return data?.object?.asMoveObject?.contents?.json;
}

/**
 * 查询钱包拥有的指定类型对象
 */
export async function getOwnedObjectsByType(
  walletAddress: string, 
  objectType: string, 
  limit: number = 50
): Promise<string[]> {
  const query = `
    query GetOwnedObjects($address: SuiAddress!, $type: String!, $last: Int) {
      address(address: $address) {
        objects(last: $last, filter: { type: $type }) {
          nodes { address }
        }
      }
    }
  `;

  const data = await executeQuery(query, { address: walletAddress, type: objectType, last: limit });
  return data?.address?.objects?.nodes?.map((n: any) => n.address) || [];
}

// === EVE Frontier 特定查询 ===

/**
 * 查询所有 Gate 对象
 * Gate 是星门 - 用于空间旅行的可编程结构
 */
export async function getAllGates(limit: number = 50): Promise<any[]> {
  return getObjectsByType(`${WORLD_PACKAGE_ID}::gate::Gate`, limit);
}

/**
 * 查询所有 NetworkNode 对象
 * NetworkNode 是能源节点 - 为基地中的 Assembly 提供能量
 */
export async function getAllNetworkNodes(limit: number = 50): Promise<any[]> {
  return getObjectsByType(`${WORLD_PACKAGE_ID}::network_node::NetworkNode`, limit);
}

/**
 * 查询所有 StorageUnit 对象
 * StorageUnit 是存储单元 - 管理物品存取
 */
export async function getAllStorageUnits(limit: number = 50): Promise<any[]> {
  return getObjectsByType(`${WORLD_PACKAGE_ID}::storage_unit::StorageUnit`, limit);
}

/**
 * 查询所有 Turret 对象
 * Turret 是炮塔 - 自定义目标逻辑
 */
export async function getAllTurrets(limit: number = 50): Promise<any[]> {
  return getObjectsByType(`${WORLD_PACKAGE_ID}::turret::Turret`, limit);
}

/**
 * 通过钱包地址查询 Character
 * 参考: https://docs.evefrontier.com/tools/interfacing-with-the-eve-frontier-world
 */
export async function getCharacterByWallet(walletAddress: string): Promise<CharacterInfo | null> {
  const profileType = `${WORLD_PACKAGE_ID}::character::PlayerProfile`;
  const query = `
    query GetCharacterDetails($address: SuiAddress!, $profileType: String!) {
      address(address: $address) {
        objects(last: 10, filter: { type: $profileType }) {
          nodes {
            asMoveObject {
              contents {
                type { repr }
                json
              }
            }
          }
        }
      }
    }
  `;

  const data = await executeQuery(query, { address: walletAddress, profileType });
  const nodes = data?.address?.objects?.nodes || [];
  
  if (nodes.length === 0) return null;
  
  const json = nodes[0]?.asMoveObject?.contents?.json;
  if (!json) return null;

  return {
    id: json.character_id || json.id,
    address: walletAddress,
    name: json.name || 'Unknown',
    tribe: json.tribe_id || json.tribe || 0,
    ownerCapId: json.owner_cap_id || '',
  };
}

// === 事件查询 (JSON-RPC) ===

/**
 * 查询 Move 事件
 * 参考: https://docs.sui.io/guides/developer/accessing-data/using-events
 */
export async function queryEvents(
  eventType: string, 
  limit: number = 20, 
  descending: boolean = true
): Promise<EventInfo[]> {
  const result = await executeRpcCall('suix_queryEvents', [
    { MoveEventType: eventType },
    null,
    limit,
    descending,
  ]);

  return (result?.data || []).map((e: any) => ({
    type: e.type,
    timestamp: e.timestampMs,
    data: e.parsedJson,
    txDigest: e.id?.txDigest || '',
  }));
}

/**
 * 查询 JumpEvent 事件 - 星门跳跃记录
 */
export async function getJumpEvents(limit: number = 20): Promise<EventInfo[]> {
  return queryEvents(`${WORLD_PACKAGE_ID}::gate::JumpEvent`, limit);
}

/**
 * 查询 Gate 创建事件
 */
export async function getGateCreatedEvents(limit: number = 20): Promise<EventInfo[]> {
  return queryEvents(`${WORLD_PACKAGE_ID}::gate::GateCreatedEvent`, limit);
}

/**
 * 查询 Commander 的 PermitIssued 事件
 */
export async function getPermitIssuedEvents(
  commanderPackageId: string, 
  limit: number = 20
): Promise<EventInfo[]> {
  return queryEvents(`${commanderPackageId}::gate_commander::PermitIssuedEvent`, limit);
}

/**
 * 查询 Commander 的 AccessDenied 事件
 */
export async function getAccessDeniedEvents(
  commanderPackageId: string, 
  limit: number = 20
): Promise<EventInfo[]> {
  return queryEvents(`${commanderPackageId}::gate_commander::AccessDeniedEvent`, limit);
}

/**
 * 查询保险合约事件
 */
export async function getInsuranceEvents(
  insurancePackageId: string,
  eventName: 'PolicyCreated' | 'ClaimProcessed' | 'ClaimDenied' | 'PolicyRenewed',
  limit: number = 20
): Promise<EventInfo[]> {
  return queryEvents(`${insurancePackageId}::insurance::${eventName}`, limit);
}

// === 聚合查询 ===

/**
 * 获取 EVE Frontier 世界概况
 */
export async function getWorldOverview(): Promise<{
  gates: number;
  networkNodes: number;
  storageUnits: number;
  turrets: number;
  recentJumps: number;
}> {
  const [gates, nodes, storage, turrets, jumps] = await Promise.all([
    getAllGates(1).then(r => r.length).catch(() => 0),
    getAllNetworkNodes(1).then(r => r.length).catch(() => 0),
    getAllStorageUnits(1).then(r => r.length).catch(() => 0),
    getAllTurrets(1).then(r => r.length).catch(() => 0),
    getJumpEvents(50).then(r => r.length).catch(() => 0),
  ]);

  return {
    gates,
    networkNodes: nodes,
    storageUnits: storage,
    turrets,
    recentJumps: jumps,
  };
}

// === 格式化 ===

export function formatAssemblyList(assemblies: any[]): string {
  if (assemblies.length === 0) return '📦 暂无 Assembly';
  
  let text = '📦 Assembly 列表\n━━━━━━━━━━━━━━━\n';
  for (const a of assemblies) {
    const json = a.asMoveObject?.contents?.json;
    const type = a.asMoveObject?.contents?.type?.repr?.split('::').pop() || 'Unknown';
    const name = json?.metadata?.name || 'Unnamed';
    const status = json?.status?.is_online ? '🟢 Online' : '🔴 Offline';
    text += `${type}: ${name} ${status}\n  ID: ${a.address.substring(0, 16)}...\n`;
  }
  return text;
}

export function formatWorldOverview(overview: Awaited<ReturnType<typeof getWorldOverview>>): string {
  return [
    '🌌 EVE Frontier World Overview',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    `🚪 Gates: ${overview.gates}`,
    `⚡ Network Nodes: ${overview.networkNodes}`,
    `📦 Storage Units: ${overview.storageUnits}`,
    `🔫 Turrets: ${overview.turrets}`,
    `🛸 Recent Jumps: ${overview.recentJumps}`,
    `📡 Network: ${NETWORK}`,
    `📋 World Package: ${WORLD_PACKAGE_ID.substring(0, 20)}...`,
  ].join('\n');
}

// === 配置导出 ===

export function getConfig() {
  return {
    network: NETWORK,
    worldPackageId: WORLD_PACKAGE_ID,
    graphqlEndpoint: GRAPHQL_ENDPOINTS[NETWORK],
    rpcUrl: RPC_URLS[NETWORK],
  };
}

// === 测试入口 ===

async function main() {
  console.log('🔍 Testing EVE Frontier GraphQL module...');
  console.log(`Network: ${NETWORK}`);
  console.log(`World Package: ${WORLD_PACKAGE_ID}`);
  console.log(`GraphQL: ${GRAPHQL_ENDPOINTS[NETWORK]}`);
  
  try {
    console.log('\n--- Querying Gates ---');
    const gates = await getAllGates(5);
    console.log(`🚪 Gates found: ${gates.length}`);
    if (gates.length > 0) {
      console.log(`  First gate: ${gates[0].address}`);
      const json = gates[0].asMoveObject?.contents?.json;
      if (json) console.log(`  Data: ${JSON.stringify(json).substring(0, 200)}`);
    }

    console.log('\n--- Querying Network Nodes ---');
    const nodes = await getAllNetworkNodes(5);
    console.log(`⚡ Network Nodes found: ${nodes.length}`);

    console.log('\n--- Querying Events ---');
    const jumps = await getJumpEvents(5);
    console.log(`🛸 Recent jumps: ${jumps.length}`);
    if (jumps.length > 0) {
      console.log(`  Latest: ${JSON.stringify(jumps[0].data).substring(0, 200)}`);
    }

    console.log('\n--- World Overview ---');
    const overview = await getWorldOverview();
    console.log(formatWorldOverview(overview));

  } catch (e: any) {
    console.log(`Query error: ${e.message}`);
  }
  
  console.log('\n✅ GraphQL module test complete');
}

if (process.argv[1]?.includes('graphql')) {
  main().catch(console.error);
}
