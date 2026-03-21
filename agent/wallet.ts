/**
 * 钱包模块 — Sui Ed25519 钱包管理
 * 创建/导入/查余额/签名交易
 */

import { SuiJsonRpcClient, getJsonRpcFullnodeUrl } from '@mysten/sui/jsonRpc';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { Transaction } from '@mysten/sui/transactions';

// 网络配置
const NETWORK = process.env.SUI_NETWORK || 'testnet';

// 创建 Sui 客户端
export function createClient(network: string = NETWORK): SuiJsonRpcClient {
  const url = getJsonRpcFullnodeUrl(network as 'mainnet' | 'testnet' | 'devnet');
  return new SuiJsonRpcClient({ url });
}

// 生成新钱包
export function generateWallet(): { keypair: Ed25519Keypair; address: string; privateKey: string } {
  const keypair = new Ed25519Keypair();
  const address = keypair.getPublicKey().toSuiAddress();
  // 导出 bech32 格式私钥 (suiprivkey1...)
  const privateKey = keypair.getSecretKey();
  
  return {
    keypair,
    address,
    privateKey,
  };
}

// 从私钥导入钱包
export function importWallet(privateKey: string): { keypair: Ed25519Keypair; address: string } {
  // 支持 bech32 (suiprivkey1...) 格式
  const keypair = Ed25519Keypair.fromSecretKey(privateKey);
  const address = keypair.getPublicKey().toSuiAddress();
  return { keypair, address };
}

// 查询余额
export async function getBalance(client: SuiJsonRpcClient, address: string): Promise<{
  sui: bigint;
  suiFormatted: string;
  tokens: Array<{ coinType: string; balance: string; formatted: string }>;
}> {
  // SUI 余额
  const suiBalance = await client.getBalance({ owner: address });
  const suiBigInt = BigInt(suiBalance.totalBalance);
  const suiFormatted = (Number(suiBigInt) / 1e9).toFixed(9);
  
  // 所有 token 余额
  const allBalances = await client.getAllBalances({ owner: address });
  const tokens = allBalances.map(b => ({
    coinType: b.coinType,
    balance: b.totalBalance,
    formatted: (Number(BigInt(b.totalBalance)) / 1e9).toFixed(9),
  }));
  
  return {
    sui: suiBigInt,
    suiFormatted,
    tokens,
  };
}

// 转账 SUI
export async function transferSui(
  client: SuiJsonRpcClient,
  keypair: Ed25519Keypair,
  to: string,
  amountMist: bigint
) {
  const tx = new Transaction();
  const [coin] = tx.splitCoins(tx.gas, [amountMist]);
  tx.transferObjects([coin], to);
  
  const result = await client.signAndExecuteTransaction({
    signer: keypair,
    transaction: tx,
    options: { showEffects: true },
  });
  
  return result;
}

// 测试入口
async function main() {
  console.log('🔑 生成新钱包...');
  const wallet = generateWallet();
  console.log(`地址: ${wallet.address}`);
  console.log(`私钥: [已隐藏]`);
  
  const client = createClient();
  console.log(`\n💰 查询余额 (${NETWORK})...`);
  const balance = await getBalance(client, wallet.address);
  console.log(`SUI: ${balance.suiFormatted}`);
  console.log(`所有 token:`, balance.tokens);
  
  console.log('\n✅ 钱包模块测试通过');
}

if (process.argv[1]?.includes('wallet')) {
  main().catch(console.error);
}
