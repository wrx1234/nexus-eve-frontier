/**
 * Telegram Bot — @SuiJarvisBot
 * Sui DeFi Jarvis 的用户交互界面
 */

const PROXY_URL = process.env.HTTPS_PROXY || 'http://172.18.0.1:7890';

import { ProxyAgent, setGlobalDispatcher, fetch as undiciFetch } from 'undici';
const agent = new ProxyAgent(PROXY_URL);
setGlobalDispatcher(agent);
// Override global fetch to use proxy
const originalFetch = globalThis.fetch;
globalThis.fetch = ((url: any, init?: any) => {
  return originalFetch(url, { ...init, dispatcher: agent } as any);
}) as typeof fetch;

import { Bot, Context, InlineKeyboard } from 'grammy';
import { createClient, generateWallet, importWallet, getBalance } from '../agent/wallet.ts';
import { createAggregator, getSwapQuote, TOKENS, TOKEN_NAMES, formatSwapPreview } from '../agent/swap.ts';
import { logAction, getTodayLogs, formatLogs, flushLogs } from '../agent/logger.ts';

// 配置
const BOT_TOKEN = process.env.TG_BOT_TOKEN || '7825340169:AAEL5DRdPL6E_zR6-eOSu0ttw-AxaHr0yzI';
const NETWORK = process.env.SUI_NETWORK || 'testnet';
const ADMIN_IDS = (process.env.TG_ADMIN_IDS || '').split(',').filter(Boolean);

// 权限检查
function isAdmin(ctx: Context): boolean {
  if (ADMIN_IDS.length === 0) return true; // 未配置则允许所有人
  return ADMIN_IDS.includes(String(ctx.from?.id || ''));
}

// 初始化 — custom fetch with proxy for grammy
import { fetch as undiciFetch } from 'undici';
const proxyFetch = (url: any, init?: any) => undiciFetch(url, { ...init, dispatcher: agent });
const bot = new Bot(BOT_TOKEN, {
  client: {
    // @ts-ignore
    canUseWebhookReply: () => false,
  },
});
// Monkey-patch grammy's internal fetch
(bot.api.config as any).use((prev: any, method: string, payload: any, signal?: any) => {
  return prev(method, payload, signal);
});
// Override raw API call's fetch
const origRaw = bot.api.raw;

const suiClient = createClient(NETWORK);
const aggregator = createAggregator();

// 用户钱包存储（生产环境应加密持久化）
const userWallets: Map<string, { address: string; privateKeyHex: string }> = new Map();

// ===================== 命令处理 =====================

// /start — 欢迎消息
bot.command('start', async (ctx: Context) => {
  const keyboard = new InlineKeyboard()
    .text('💰 查看余额', 'balance')
    .text('🔄 Swap', 'swap_menu')
    .row()
    .text('🤖 策略状态', 'strategy')
    .text('📝 操作日志', 'logs')
    .row()
    .text('⚙️ 设置', 'settings')
    .text('❓ 帮助', 'help');

  await ctx.reply(
    `🤖 *Sui DeFi Jarvis*\n` +
    `━━━━━━━━━━━━━━━━━━\n` +
    `The Infinite Money Glitch on Sui\n\n` +
    `我是你的 AI DeFi 助手，运行在 OpenClaw 上。\n` +
    `我可以：\n` +
    `• 💰 管理你的 Sui 钱包\n` +
    `• 🔄 通过 Cetus 最优路径交易\n` +
    `• 🤖 自动执行 DeFi 策略\n` +
    `• 📝 所有操作记录在 Walrus 上\n\n` +
    `网络: *${NETWORK}*\n` +
    `输入 /wallet 开始设置钱包`,
    { parse_mode: 'Markdown', reply_markup: keyboard }
  );
  
  logAction('bot_start', { userId: ctx.from?.id });
});

// /wallet — 钱包管理
bot.command('wallet', async (ctx: Context) => {
  const userId = ctx.from?.id?.toString() || '';
  const existing = userWallets.get(userId);
  
  if (existing) {
    const balance = await getBalance(suiClient, existing.address);
    await ctx.reply(
      `💰 *你的钱包*\n` +
      `━━━━━━━━━━━━━━━\n` +
      `地址: \`${existing.address}\`\n` +
      `网络: ${NETWORK}\n` +
      `SUI: ${balance.suiFormatted}\n` +
      `\n所有 Token:\n` +
      balance.tokens.map(t => `• ${t.coinType.split('::').pop()}: ${t.formatted}`).join('\n') || '暂无其他 Token',
      { parse_mode: 'Markdown' }
    );
  } else {
    const keyboard = new InlineKeyboard()
      .text('🆕 创建新钱包', 'wallet_create')
      .text('📥 导入钱包', 'wallet_import');
    
    await ctx.reply(
      '你还没有设置钱包。选择一个操作：',
      { reply_markup: keyboard }
    );
  }
});

// /balance — 查看余额
bot.command('balance', async (ctx: Context) => {
  const userId = ctx.from?.id?.toString() || '';
  const wallet = userWallets.get(userId);
  
  if (!wallet) {
    await ctx.reply('⚠️ 请先设置钱包：/wallet');
    return;
  }
  
  const balance = await getBalance(suiClient, wallet.address);
  await ctx.reply(
    `💰 *资产总览*\n` +
    `━━━━━━━━━━━━━━━\n` +
    `地址: \`${wallet.address.substring(0, 10)}...${wallet.address.slice(-6)}\`\n` +
    `\n*余额:*\n` +
    `• SUI: ${balance.suiFormatted}\n` +
    balance.tokens
      .filter(t => t.coinType !== '0x2::sui::SUI')
      .map(t => `• ${t.coinType.split('::').pop()}: ${t.formatted}`)
      .join('\n'),
    { parse_mode: 'Markdown' }
  );
});

// /swap — Swap 菜单
bot.command('swap', async (ctx: Context) => {
  const keyboard = new InlineKeyboard()
    .text('SUI → USDC', 'swap_sui_usdc')
    .text('USDC → SUI', 'swap_usdc_sui')
    .row()
    .text('SUI → CETUS', 'swap_sui_cetus')
    .text('自定义', 'swap_custom');
  
  await ctx.reply(
    '🔄 *Swap — Cetus Aggregator*\n' +
    '选择交易对，或发送格式：\n' +
    '`swap 10 SUI USDC`',
    { parse_mode: 'Markdown', reply_markup: keyboard }
  );
});

// /logs — 查看操作日志
bot.command('logs', async (ctx: Context) => {
  const logs = getTodayLogs();
  const text = formatLogs(logs);
  
  const keyboard = new InlineKeyboard()
    .text('🐘 上传到 Walrus', 'flush_walrus')
    .text('🔄 刷新', 'refresh_logs');
  
  await ctx.reply(text, { reply_markup: keyboard });
});

// /help — 帮助
bot.command('help', async (ctx: Context) => {
  await ctx.reply(
    `❓ *Sui DeFi Jarvis 帮助*\n` +
    `━━━━━━━━━━━━━━━━━━\n\n` +
    `*命令:*\n` +
    `/start — 主菜单\n` +
    `/wallet — 钱包管理\n` +
    `/balance — 查看余额\n` +
    `/swap — 交易\n` +
    `/logs — 操作日志\n` +
    `/help — 帮助\n\n` +
    `*自然语言:*\n` +
    `"帮我把 10 SUI 换成 USDC"\n` +
    `"我的余额是多少"\n` +
    `"今天的交易记录"\n\n` +
    `*Powered by:*\n` +
    `🦞 OpenClaw | 🌊 Sui | 🐋 Cetus | 🐘 Walrus`,
    { parse_mode: 'Markdown' }
  );
});

// ===================== 回调处理 =====================

// 创建新钱包
bot.callbackQuery('wallet_create', async (ctx) => {
  const userId = ctx.from?.id?.toString() || '';
  const wallet = generateWallet();
  
  userWallets.set(userId, {
    address: wallet.address,
    privateKeyHex: wallet.privateKey,
  });
  
  logAction('wallet_create', { address: wallet.address });
  
  await ctx.answerCallbackQuery();
  await ctx.reply(
    `🆕 *新钱包已创建*\n` +
    `━━━━━━━━━━━━━━━\n` +
    `地址: \`${wallet.address}\`\n` +
    `网络: ${NETWORK}\n\n` +
    `⚠️ *私钥（请安全保存）:*\n` +
    `\`${wallet.privateKey}\`\n\n` +
    `💡 在 ${NETWORK} 上可以通过 faucet 领取测试币：\n` +
    `https://faucet.testnet.sui.io/`,
    { parse_mode: 'Markdown' }
  );
});

// Swap SUI → USDC 报价
bot.callbackQuery('swap_sui_usdc', async (ctx) => {
  await ctx.answerCallbackQuery('获取报价中...');
  
  try {
    const amount = BigInt(1_000_000_000); // 1 SUI
    const quote = await getSwapQuote(aggregator, TOKENS.SUI, TOKENS.USDC, amount);
    
    if (quote) {
      const keyboard = new InlineKeyboard()
        .text('✅ 执行交易', 'exec_swap_sui_usdc_1')
        .text('❌ 取消', 'cancel');
      
      await ctx.reply(
        formatSwapPreview('SUI', 'USDC', '1.0', quote.outputFormatted),
        { reply_markup: keyboard }
      );
    } else {
      await ctx.reply('⚠️ 未找到可用路由');
    }
  } catch (e: any) {
    await ctx.reply(`❌ 报价失败: ${e.message}`);
  }
});

// 查看余额按钮
bot.callbackQuery('balance', async (ctx) => {
  await ctx.answerCallbackQuery();
  // 触发 /balance 逻辑
  const userId = ctx.from?.id?.toString() || '';
  const wallet = userWallets.get(userId);
  
  if (!wallet) {
    await ctx.reply('⚠️ 请先设置钱包：/wallet');
    return;
  }
  
  const balance = await getBalance(suiClient, wallet.address);
  await ctx.reply(
    `💰 SUI: ${balance.suiFormatted}\n` +
    balance.tokens
      .filter(t => t.coinType !== '0x2::sui::SUI')
      .map(t => `• ${t.coinType.split('::').pop()}: ${t.formatted}`)
      .join('\n') || '暂无其他 Token'
  );
});

// 上传日志到 Walrus
bot.callbackQuery('flush_walrus', async (ctx) => {
  await ctx.answerCallbackQuery('上传中...');
  const blobId = await flushLogs();
  
  if (blobId) {
    await ctx.reply(`🐘 日志已上传到 Walrus\nBlob ID: \`${blobId}\``, { parse_mode: 'Markdown' });
  } else {
    await ctx.reply('⚠️ Walrus 暂不可用，日志已保存在本地');
  }
});

// ===================== 自然语言处理 =====================

bot.on('message:text', async (ctx) => {
  const text = ctx.message.text.toLowerCase();
  
  // 简单意图识别
  if (text.includes('余额') || text.includes('balance') || text.includes('多少钱')) {
    // 触发查余额
    const userId = ctx.from?.id?.toString() || '';
    const wallet = userWallets.get(userId);
    if (wallet) {
      const balance = await getBalance(suiClient, wallet.address);
      await ctx.reply(`💰 SUI: ${balance.suiFormatted}`);
    } else {
      await ctx.reply('⚠️ 请先 /wallet 设置钱包');
    }
  } else if (text.includes('swap') || text.includes('换') || text.includes('兑换')) {
    await ctx.reply('🔄 请使用 /swap 命令或按钮进行交易');
  } else if (text.includes('日志') || text.includes('记录') || text.includes('log')) {
    const logs = getTodayLogs();
    await ctx.reply(formatLogs(logs));
  } else {
    await ctx.reply(
      '🤖 我是 Sui DeFi Jarvis。试试：\n' +
      '/balance — 查余额\n' +
      '/swap — 交易\n' +
      '/logs — 日志'
    );
  }
});

// ===================== 启动 =====================

async function main() {
  console.log('🤖 Sui DeFi Jarvis Bot 启动中...');
  console.log(`网络: ${NETWORK}`);
  console.log(`Bot: @sui_kol_bot`);
  
  logAction('bot_init', { network: NETWORK });
  
  bot.start({
    onStart: () => console.log('✅ Bot 已上线: @SuiJarvisBot'),
  });
}

main().catch(console.error);
