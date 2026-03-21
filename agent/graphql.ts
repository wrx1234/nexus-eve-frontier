/**
 * GraphQL 查询模块 - 读取 EVE Frontier 链上数据
 * 通过 Sui GraphQL API 查询 Assembly 状态、Character 信息等
 */

const GRAPHQL_ENDPOINTS: Record<string, string> = {
  testnet: 'https://graphql.testnet.sui.io/graphql',
  mainnet: 'https://graphql.mainnet.sui.io/graphql',
  devnet: 'https://graphql.devnet.sui.io/graphql',
};

const NETWORK = process.env.SUI_NETWORK || 'testnet';
const WORLD_PACKAGE_ID = process.env.WORLD_PACKAGE_ID || '';

// ===================== 类型定义 =====================

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

// ===================== GraphQL 查询 =====================

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

// ===================== Assembly 查询 =====================

/**
 * 按类型查询所有对象
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

/**
 * 通过钱包地址查询 Character
 */
export async function getCharacterByWallet(walletAddress: string): Promise<CharacterInfo | null> {
  if (!WORLD_PACKAGE_ID) {
    console.warn('WORLD_PACKAGE_ID not set, cannot query character');
    return null;
  }

  const profileType = `${WORLD_PACKAGE_ID}::character::PlayerProfile`;
  const query = `
    query GetCharacter($address: SuiAddress!, $profileType: String!) {
      address(address: $address) {
        objects(last: 10, filter: { type: $profileType }) {
          nodes {
            contents {
              ... on MoveObject {
                contents {
                  type { repr }
                  json
                }
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
  
  const json = nodes[0]?.contents?.contents?.json;
  if (!json) return null;

  return {
    id: json.character_id || json.id,
    address: walletAddress,
    name: json.name || 'Unknown',
    tribe: json.tribe || 0,
    ownerCapId: json.owner_cap_id || '',
  };
}

/**
 * 查询所有 Gate 对象
 */
export async function getAllGates(limit: number = 50): Promise<any[]> {
  if (!WORLD_PACKAGE_ID) return [];
  return getObjectsByType(`${WORLD_PACKAGE_ID}::gate::Gate`, limit);
}

/**
 * 查询所有 StorageUnit 对象
 */
export async function getAllStorageUnits(limit: number = 50): Promise<any[]> {
  if (!WORLD_PACKAGE_ID) return [];
  return getObjectsByType(`${WORLD_PACKAGE_ID}::storage_unit::StorageUnit`, limit);
}

/**
 * 查询所有 NetworkNode 对象
 */
export async function getAllNetworkNodes(limit: number = 50): Promise<any[]> {
  if (!WORLD_PACKAGE_ID) return [];
  return getObjectsByType(`${WORLD_PACKAGE_ID}::network_node::NetworkNode`, limit);
}

/**
 * 查询所有 Turret 对象
 */
export async function getAllTurrets(limit: number = 50): Promise<any[]> {
  if (!WORLD_PACKAGE_ID) return [];
  return getObjectsByType(`${WORLD_PACKAGE_ID}::turret::Turret`, limit);
}

// ===================== 事件查询 =====================

/**
 * 查询 Move 事件（通过 JSON-RPC）
 */
export async function queryEvents(
  eventType: string, 
  limit: number = 20, 
  descending: boolean = true
): Promise<EventInfo[]> {
  const RPC_URLS: Record<string, string> = {
    testnet: 'https://fullnode.testnet.sui.io:443',
    mainnet: 'https://fullnode.mainnet.sui.io:443',
    devnet: 'https://fullnode.devnet.sui.io:443',
  };

  const rpcUrl = RPC_URLS[NETWORK];
  if (!rpcUrl) throw new Error(`Unknown network: ${NETWORK}`);

  const response = await fetch(rpcUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'suix_queryEvents',
      params: [{ MoveEventType: eventType }, null, limit, descending],
    }),
  });

  const result = await response.json() as any;
  if (result.error) {
    throw new Error(`RPC error: ${JSON.stringify(result.error)}`);
  }

  return (result.result?.data || []).map((e: any) => ({
    type: e.type,
    timestamp: e.timestampMs,
    data: e.parsedJson,
    txDigest: e.id?.txDigest || '',
  }));
}

/**
 * 查询 JumpEvent 事件
 */
export async function getJumpEvents(limit: number = 20): Promise<EventInfo[]> {
  if (!WORLD_PACKAGE_ID) return [];
  return queryEvents(`${WORLD_PACKAGE_ID}::gate::JumpEvent`, limit);
}

/**
 * 查询 Gate 创建事件
 */
export async function getGateCreatedEvents(limit: number = 20): Promise<EventInfo[]> {
  if (!WORLD_PACKAGE_ID) return [];
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

// ===================== 格式化 =====================

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

// 测试
async function main() {
  console.log('🔍 Testing GraphQL module...');
  console.log(`Network: ${NETWORK}`);
  console.log(`World Package: ${WORLD_PACKAGE_ID || 'NOT SET'}`);
  
  if (WORLD_PACKAGE_ID) {
    try {
      const gates = await getAllGates(5);
      console.log(`\n🚪 Gates found: ${gates.length}`);
      
      const nodes = await getAllNetworkNodes(5);
      console.log(`⚡ Network Nodes found: ${nodes.length}`);
      
      const events = await getJumpEvents(5);
      console.log(`🛸 Recent jumps: ${events.length}`);
    } catch (e: any) {
      console.log(`Query error: ${e.message}`);
    }
  } else {
    console.log('\n⚠️ Set WORLD_PACKAGE_ID to query EVE objects');
  }
  
  console.log('\n✅ GraphQL module test complete');
}

if (process.argv[1]?.includes('graphql')) {
  main().catch(console.error);
}
