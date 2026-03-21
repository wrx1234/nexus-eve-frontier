# 🔧 技术参考 — 可直接使用的代码片段

## 1. Cetus Aggregator SDK

### 安装
```bash
npm install @cetusprotocol/aggregator-sdk
```

### 初始化
```typescript
import { AggregatorClient } from '@cetusprotocol/aggregator-sdk';
const client = new AggregatorClient({});
```

### 获取最优 swap 路径
```typescript
import BN from 'bn.js';

const routers = await client.findRouters({
  from: '0x2::sui::SUI',
  target: '0x06864a6f921804860930db6ddbe2e16acdf8504495ea7481637a1c8b9a8fe54b::cetus::CETUS',
  amount: new BN(1000000000), // 1 SUI = 1e9 MIST
  byAmountIn: true,  // true=固定输入, false=固定输出
});
```

### 快速 swap（推荐）
```typescript
import { Transaction } from '@mysten/sui/transactions';

const txb = new Transaction();
if (routers != null) {
  await client.fastRouterSwap({
    routers,
    txb,
    slippage: 0.01, // 1% 滑点
  });
  
  // 模拟执行检查
  const simResult = await client.devInspectTransactionBlock(txb, keypair);
  if (simResult.effects.status.status === 'success') {
    const result = await client.signAndExecuteTransaction(txb, keypair);
  }
}
```

### 自定义 swap（返回 coin 对象，可组合 PTB）
```typescript
const targetCoin = await client.routerSwap({
  routers,
  txb,
  inputCoin, // TransactionObjectArgument
  slippage: 0.01,
});
// targetCoin 可用于后续 PTB 操作
client.transferOrDestoryCoin(txb, targetCoin, targetCoinType);
```

### 集成的 DEX（30+）
Cetus, DeepBook V3, Kriya, FlowX, Turbos, Aftermath, Haedal, Volo, Bluemove, Bluefin, Scallop, Suilend, AlphaFi, SpringSui, Steamm, Metastable, Obric, Momentum, Magma, 7K, Fullsail, etc.

### 合约地址（Mainnet）
- CetusAggregatorV2: `0x40e457bc65a398d2db7026881358fcb7cfa2f1bb052bca41f46c55a1103f2d6f`
- CetusAggregatorV2ExtendV1: `0x2edc22bf96c85482b2208624fa9339255d5055113c92fd6c33add48ce971b774`
- CetusAggregatorV2ExtendV2: `0x2e227a3cbc6715518b18ed339d2f967153674b7b257da114ca62c72b2011258a`

---

## 2. Sui SDK (@mysten/sui)

### 钱包
```typescript
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';

// 生成钱包
const keypair = new Ed25519Keypair();
const address = keypair.getPublicKey().toSuiAddress();

// 连接网络
const client = new SuiClient({ url: getFullnodeUrl('mainnet') });

// 查余额
const balance = await client.getBalance({ owner: address });
const allBalances = await client.getAllBalances({ owner: address });
```

### 转账
```typescript
import { Transaction } from '@mysten/sui/transactions';

const tx = new Transaction();
const [coin] = tx.splitCoins(tx.gas, [1000000000n]); // 1 SUI
tx.transferObjects([coin], '0x目标地址');

const result = await client.signAndExecuteTransaction({
  signer: keypair,
  transaction: tx,
});
```

### Faucet（测试网领币）
```typescript
import { requestSuiFromFaucetV0, getFaucetHost } from '@mysten/sui/faucet';
await requestSuiFromFaucetV0({
  host: getFaucetHost('testnet'),
  recipient: address,
});
```

---

## 3. Walrus 存储

### HTTP API 上传 Blob
```bash
# 上传
curl -X PUT "https://publisher.testnet.walrus.space/v1/blobs" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @file.json

# 返回
# { "newlyCreated": { "blobObject": { "blobId": "xxx" } } }
# 或
# { "alreadyCertified": { "blobId": "xxx" } }
```

### TypeScript
```typescript
async function uploadToWalrus(data: string): Promise<string | null> {
  const res = await fetch('https://publisher.testnet.walrus.space/v1/blobs', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/octet-stream' },
    body: data,
  });
  const result = await res.json();
  return result?.newlyCreated?.blobObject?.blobId || 
         result?.alreadyCertified?.blobId || null;
}
```

### 读取 Blob
```bash
curl "https://aggregator.testnet.walrus.space/v1/blobs/{blobId}"
```

### 关键点
- Walrus 用 Sui 链做协调和支付
- 存储空间以 Sui 对象表示，可拥有/拆分/合并/转让
- 成本约为存储大小的 5 倍（erasure coding）
- WAL token 用于支付存储费

---

## 4. Move 合约基础

### 最简 Vault 合约
```move
module jarvis::vault {
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::event;

    // 事件
    public struct DepositEvent has copy, drop {
        amount: u64,
        sender: address,
    }
    
    public struct WithdrawEvent has copy, drop {
        amount: u64,
        recipient: address,
    }
    
    public struct TradeEvent has copy, drop {
        action: vector<u8>,
        from_token: vector<u8>,
        to_token: vector<u8>,
        amount: u64,
        timestamp: u64,
    }

    // Vault 对象
    public struct Vault has key {
        id: UID,
        owner: address,
        balance: Coin<SUI>,
    }

    // 创建 Vault
    public fun create(ctx: &mut TxContext) {
        let vault = Vault {
            id: object::new(ctx),
            owner: tx_context::sender(ctx),
            balance: coin::zero<SUI>(ctx),
        };
        transfer::transfer(vault, tx_context::sender(ctx));
    }

    // 存入
    public fun deposit(vault: &mut Vault, coin: Coin<SUI>, ctx: &TxContext) {
        let amount = coin::value(&coin);
        coin::join(&mut vault.balance, coin);
        event::emit(DepositEvent { amount, sender: tx_context::sender(ctx) });
    }

    // 取出
    public fun withdraw(vault: &mut Vault, amount: u64, ctx: &mut TxContext) {
        assert!(tx_context::sender(ctx) == vault.owner, 0);
        let coin = coin::split(&mut vault.balance, amount, ctx);
        transfer::public_transfer(coin, vault.owner);
        event::emit(WithdrawEvent { amount, recipient: vault.owner });
    }
    
    // 记录交易事件
    public fun log_trade(
        action: vector<u8>,
        from_token: vector<u8>,
        to_token: vector<u8>,
        amount: u64,
        timestamp: u64,
    ) {
        event::emit(TradeEvent { action, from_token, to_token, amount, timestamp });
    }
}
```

### 部署
```bash
sui move build
sui client publish --gas-budget 100000000
```

---

## 5. Moltbook API

### Base URL
`https://www.moltbook.com/api/v1`

⚠️ 必须带 `www`，不带会重定向丢失 Authorization header

### 认证
```bash
-H "Authorization: Bearer YOUR_API_KEY"
```

### 发帖
```bash
curl -X POST https://www.moltbook.com/api/v1/posts \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "帖子内容", "community": "sui"}'
```

### 搜索
```bash
curl "https://www.moltbook.com/api/v1/posts/search?q=keyword" \
  -H "Authorization: Bearer $API_KEY"
```

### 评论
```bash
curl -X POST "https://www.moltbook.com/api/v1/posts/{postId}/comments" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "评论内容"}'
```

### 凭据位置
`~/.config/moltbook/credentials.json`

---

## 6. grammy (TG Bot)

### 基本用法
```typescript
import { Bot, InlineKeyboard } from 'grammy';

const bot = new Bot('TOKEN');

bot.command('start', (ctx) => ctx.reply('Hello!'));

// 内联键盘
bot.command('menu', (ctx) => {
  const kb = new InlineKeyboard()
    .text('按钮1', 'callback_1')
    .text('按钮2', 'callback_2');
  ctx.reply('选择:', { reply_markup: kb });
});

// 处理回调
bot.callbackQuery('callback_1', (ctx) => {
  ctx.answerCallbackQuery('已选择');
  ctx.reply('你选了按钮1');
});

bot.start();
```

---

## 7. 常用 Token 地址

| Token | 地址 |
|-------|------|
| SUI | `0x2::sui::SUI` |
| USDC (Wormhole) | `0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN` |
| CETUS | `0x06864a6f921804860930db6ddbe2e16acdf8504495ea7481637a1c8b9a8fe54b::cetus::CETUS` |
| USDT (Wormhole) | `0xc060006111016b8a020ad5b33834984a437aaa7d3c74c18e09a95d48aceab08c::coin::COIN` |
