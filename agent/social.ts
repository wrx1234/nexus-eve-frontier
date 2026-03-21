/**
 * Social Sniper — 病毒传播引擎
 * 监控社交媒体 → AI 分析 → 自动交易 → 回复推文
 */

import { logAction } from './logger.js';

// ===================== 配置 =====================

interface SocialConfig {
  twitterEnabled: boolean;
  moltbookEnabled: boolean;
  autoReply: boolean;
  tradeBroadcast: boolean;
  monitorKeywords: string[];
  // Twitter API (预留)
  twitterApiKey?: string;
  twitterApiSecret?: string;
  twitterAccessToken?: string;
  twitterAccessSecret?: string;
  // Moltbook
  moltbookCredPath?: string;
}

const defaultConfig: SocialConfig = {
  twitterEnabled: false,  // 等接入 Twitter API 后开启
  moltbookEnabled: true,
  autoReply: false,        // 安全起见默认关
  tradeBroadcast: true,
  monitorKeywords: ['$SUI', '$CETUS', 'Sui DeFi', '@CetusProtocol', '@SuiNetwork', 'sui swap'],
};

// ===================== 推文监控 =====================

interface Tweet {
  id: string;
  author: string;
  authorFollowers: number;
  text: string;
  timestamp: string;
  url: string;
}

// 监控推文（Twitter API v2）
export async function monitorTweets(config: SocialConfig): Promise<Tweet[]> {
  if (!config.twitterEnabled) {
    console.log('⏸️ Twitter 监控未启用');
    return [];
  }
  
  // TODO: 接入 Twitter API v2 搜索
  // GET /2/tweets/search/recent?query=$SUI OR $CETUS
  // 需要 Bearer Token
  
  console.log(`🔍 监控关键词: ${config.monitorKeywords.join(', ')}`);
  return [];
}

// ===================== 情绪分析 =====================

interface SentimentResult {
  sentiment: 'bullish' | 'bearish' | 'neutral';
  confidence: number;      // 0-1
  tokens: string[];        // 提到的 token
  tradeSignal: 'buy' | 'sell' | 'hold';
  reasoning: string;
}

// AI 分析推文情绪
export async function analyzeSentiment(tweet: Tweet): Promise<SentimentResult> {
  // 简单关键词分析（MVP 版本）
  // 生产环境用 Claude API 做深度分析
  const text = tweet.text.toLowerCase();
  
  const bullishWords = ['moon', 'pump', 'bullish', '涨', 'buy', 'long', 'ath', 'breakout', '🚀', '📈'];
  const bearishWords = ['dump', 'crash', 'bearish', '跌', 'sell', 'short', 'rekt', '📉', '💀'];
  
  let bullScore = 0;
  let bearScore = 0;
  
  for (const word of bullishWords) {
    if (text.includes(word)) bullScore++;
  }
  for (const word of bearishWords) {
    if (text.includes(word)) bearScore++;
  }
  
  // 检测提到的 token
  const tokens: string[] = [];
  if (text.includes('sui') || text.includes('$sui')) tokens.push('SUI');
  if (text.includes('cetus') || text.includes('$cetus')) tokens.push('CETUS');
  if (text.includes('usdc')) tokens.push('USDC');
  
  const sentiment = bullScore > bearScore ? 'bullish' : bearScore > bullScore ? 'bearish' : 'neutral';
  const confidence = Math.min((Math.abs(bullScore - bearScore) + 1) / 5, 1);
  
  const result: SentimentResult = {
    sentiment,
    confidence,
    tokens: tokens.length > 0 ? tokens : ['SUI'],
    tradeSignal: sentiment === 'bullish' ? 'buy' : sentiment === 'bearish' ? 'sell' : 'hold',
    reasoning: `Keywords: bull=${bullScore} bear=${bearScore}. ${sentiment} on ${tokens.join(',')}`,
  };
  
  logAction('sentiment_analysis', {
    tweetId: tweet.id,
    author: tweet.author,
    sentiment: result.sentiment,
    signal: result.tradeSignal,
    confidence: result.confidence,
  });
  
  return result;
}

// ===================== 社交发布 =====================

// 格式化交易播报推文
export function formatTradeTweet(params: {
  action: 'buy' | 'sell';
  fromToken: string;
  toToken: string;
  amount: string;
  result: string;
  pnlToday: string;
  walrusBlobId?: string;
  triggeredBy?: string; // 触发来源推文
}): string {
  const emoji = params.action === 'buy' ? '🟢' : '🔴';
  const walrusLink = params.walrusBlobId 
    ? `\n🐘 Proof: https://walrus.site/${params.walrusBlobId}` 
    : '';
  const trigger = params.triggeredBy 
    ? `\n💡 Triggered by market signal` 
    : '';
  
  return `${emoji} Sui DeFi Jarvis just executed:
${params.amount} ${params.fromToken} → ${params.result} ${params.toToken}

📊 Today's P&L: ${params.pnlToday}${walrusLink}${trigger}

🤖 Autonomous AI Agent on @SuiNetwork
Try it → t.me/sui_kol_bot
Built with @OpenClawAI 🦞

#SuiDeFi #AIAgent #InfiniteMoneyGlitch`;
}

// 格式化里程碑推文
export function formatMilestoneTweet(params: {
  milestone: string;  // "$500 profit", "100 trades", etc.
  startAmount: string;
  currentAmount: string;
  days: number;
  walrusBlobId?: string;
}): string {
  return `🎉 MILESTONE: ${params.milestone}!

Started with ${params.startAmount} → Now ${params.currentAmount}
⏱️ ${params.days} days of autonomous trading

Every trade logged on @WalrusProtocol 🐘
${params.walrusBlobId ? `Verify: https://walrus.site/${params.walrusBlobId}` : ''}

The Infinite Money Glitch is real 🚀
Try it → t.me/sui_kol_bot

#SuiDeFi #AIAgent @SuiNetwork @CetusProtocol`;
}

// 格式化 KOL 回复
export function formatKolReply(params: {
  sentiment: SentimentResult;
  tradeAction: string;
  walrusBlobId?: string;
}): string {
  const signal = params.sentiment.sentiment === 'bullish' ? '📈 Bullish' : 
                 params.sentiment.sentiment === 'bearish' ? '📉 Bearish' : '➡️ Neutral';
  
  return `🤖 AI Analysis: ${signal} (${(params.sentiment.confidence * 100).toFixed(0)}% conf.)

I just ${params.tradeAction} based on this signal.
${params.walrusBlobId ? `Proof on Walrus: https://walrus.site/${params.walrusBlobId}` : ''}

Track all my trades → t.me/sui_kol_bot
🦞 Powered by @OpenClawAI on @SuiNetwork`;
}

// 发布到 Twitter（预留接口）
export async function postToTwitter(text: string, replyToId?: string): Promise<boolean> {
  if (!defaultConfig.twitterEnabled) {
    console.log(`🐦 [DRY RUN] Would post:\n${text}`);
    logAction('twitter_dry_run', { text: text.substring(0, 100), replyTo: replyToId });
    return false;
  }
  
  // TODO: Twitter API v2 POST /2/tweets
  // { "text": text, "reply": { "in_reply_to_tweet_id": replyToId } }
  
  logAction('twitter_post', { text: text.substring(0, 100), replyTo: replyToId });
  return true;
}

// 发布到 Moltbook
export async function postToMoltbook(text: string, communitySlug?: string): Promise<boolean> {
  if (!defaultConfig.moltbookEnabled) return false;
  
  try {
    // 使用 Moltbook API
    // POST /api/posts { content: text, community: communitySlug }
    logAction('moltbook_post', { text: text.substring(0, 100), community: communitySlug });
    console.log(`📱 [Moltbook] Posted to ${communitySlug || 'feed'}`);
    return true;
  } catch (e: any) {
    console.error(`Moltbook post failed: ${e.message}`);
    return false;
  }
}

// ===================== 主循环 =====================

// Social Sniper 主循环
export async function socialSniperLoop(config: SocialConfig = defaultConfig) {
  console.log('🔥 Social Sniper 启动');
  console.log(`监控关键词: ${config.monitorKeywords.join(', ')}`);
  console.log(`Twitter: ${config.twitterEnabled ? '✅' : '⏸️'}`);
  console.log(`Moltbook: ${config.moltbookEnabled ? '✅' : '⏸️'}`);
  console.log(`Auto-reply: ${config.autoReply ? '✅' : '⏸️'}`);
  
  // 监控循环（每60秒）
  while (true) {
    try {
      // 1. 获取新推文
      const tweets = await monitorTweets(config);
      
      for (const tweet of tweets) {
        // 2. 分析情绪
        const sentiment = await analyzeSentiment(tweet);
        
        // 3. 如果信心足够高，执行交易
        if (sentiment.confidence >= 0.6 && sentiment.tradeSignal !== 'hold') {
          console.log(`🎯 Signal: ${sentiment.tradeSignal} ${sentiment.tokens.join(',')} (conf: ${sentiment.confidence})`);
          
          // TODO: 调用 swap 模块执行交易
          // const result = await executeSwap(...)
          
          // 4. 回复推文
          if (config.autoReply) {
            const reply = formatKolReply({
              sentiment,
              tradeAction: `went ${sentiment.tradeSignal === 'buy' ? 'long' : 'short'} on ${sentiment.tokens[0]}`,
            });
            await postToTwitter(reply, tweet.id);
          }
        }
      }
    } catch (e: any) {
      console.error(`Social Sniper error: ${e.message}`);
    }
    
    // 等待 60 秒
    await new Promise(r => setTimeout(r, 60000));
  }
}

// ===================== 交易后自动播报 =====================

// 交易完成后调用此函数自动播报
export async function broadcastTrade(params: {
  action: 'buy' | 'sell';
  fromToken: string;
  toToken: string;
  amount: string;
  result: string;
  pnlToday: string;
  walrusBlobId?: string;
  triggeredBy?: string;
}) {
  if (!defaultConfig.tradeBroadcast) return;
  
  const tweet = formatTradeTweet(params);
  
  // 发 Twitter
  await postToTwitter(tweet);
  
  // 发 Moltbook
  await postToMoltbook(tweet, 'sui');
  
  console.log(`📢 交易播报完成: ${params.action} ${params.amount} ${params.fromToken}`);
}

// 测试
async function main() {
  console.log('🔥 测试 Social Sniper...\n');
  
  // 测试情绪分析
  const mockTweet: Tweet = {
    id: '123',
    author: 'crypto_kol',
    authorFollowers: 50000,
    text: '$SUI is looking super bullish 🚀 breakout incoming! Buy the dip!',
    timestamp: new Date().toISOString(),
    url: 'https://x.com/crypto_kol/status/123',
  };
  
  const sentiment = await analyzeSentiment(mockTweet);
  console.log('情绪分析:', sentiment);
  
  // 测试推文格式
  console.log('\n--- 交易播报 ---');
  console.log(formatTradeTweet({
    action: 'buy',
    fromToken: 'USDC',
    toToken: 'SUI',
    amount: '150',
    result: '100',
    pnlToday: '+$23.5 (+2.1%)',
    walrusBlobId: 'abc123',
  }));
  
  console.log('\n--- 里程碑播报 ---');
  console.log(formatMilestoneTweet({
    milestone: '$500 Profit',
    startAmount: '$100',
    currentAmount: '$600',
    days: 7,
  }));
  
  console.log('\n--- KOL 回复 ---');
  console.log(formatKolReply({
    sentiment,
    tradeAction: 'went long on SUI',
    walrusBlobId: 'xyz789',
  }));
  
  console.log('\n✅ Social Sniper 测试完成');
}

if (process.argv[1]?.includes('social')) {
  main().catch(console.error);
}
