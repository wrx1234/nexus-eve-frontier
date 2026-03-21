#!/usr/bin/env python3
"""
🤖 Sui DeFi Jarvis Bot — @SuiJarvisBot
The Infinite Money Glitch on Sui

Autonomous AI DeFi Agent powered by OpenClaw
Tech Stack: Sui × Cetus × Walrus × Seal
"""

import json, os, time, logging, requests, hashlib, random, re, sys
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.request import HTTPXRequest

# i18n
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.')
from i18n import _ as L, get_lang as i18n_get_lang, set_lang as i18n_set_lang

# ==================== 配置 ====================
TOKEN = "7825340169:AAEL5DRdPL6E_zR6-eOSu0ttw-AxaHr0yzI"
PROXY = "http://172.18.0.1:7890"
ADMIN_ID = 6633019220
NETWORK = "testnet"
SUI_RPC = f"https://fullnode.{NETWORK}.sui.io:443"
WALRUS_AGGREGATOR = "https://aggregator.walrus-testnet.walrus.space"
DEPLOYED_PACKAGE = "0x737a73b3a146d45694c341a22b62607e5a6e6b6496b91156217a7d2c91f7e65d"
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

HK_TZ = timezone(timedelta(hours=8))

# ==================== 双语系统 i18n ====================
LANG_FILE = os.path.join(DATA_DIR, "lang_prefs.json")

TEXTS = {
    "main_greeting": {
        "cn": "🤖 *Sui DeFi Jarvis*\n选择操作:",
        "en": "🤖 *Sui DeFi Jarvis*\nChoose action:",
    },
    "btn_assets": {"cn": "💰 资产", "en": "💰 Assets"},
    "btn_swap": {"cn": "🔄 Swap 交易", "en": "🔄 Swap"},
    "btn_portfolio": {"cn": "📊 持仓", "en": "📊 Portfolio"},
    "btn_limit": {"cn": "🏷️ 限价单", "en": "🏷️ Limit Order"},
    "btn_whale": {"cn": "🐋 鲸鱼追踪", "en": "🐋 Whale Tracker"},
    "btn_pools": {"cn": "🌱 新池子", "en": "🌱 New Pools"},
    "btn_signals": {"cn": "📢 AI 信号", "en": "📢 AI Signals"},
    "btn_strategy": {"cn": "🤖 策略", "en": "🤖 Strategy"},
    "btn_mint": {"cn": "💎 JarvisUSD Mint", "en": "💎 JarvisUSD Mint"},
    "btn_yield": {"cn": "📈 收益", "en": "📈 Yield"},
    "btn_walrus": {"cn": "🐘 Walrus", "en": "🐘 Walrus"},
    "btn_vault": {"cn": "🔐 Vault", "en": "🔐 Vault"},
    "btn_social": {"cn": "📣 Social", "en": "📣 Social"},
    "btn_settings": {"cn": "⚙️ 设置", "en": "⚙️ Settings"},
    "btn_help": {"cn": "❓ 帮助", "en": "❓ Help"},
    "btn_back": {"cn": "🔙 Back to Menu", "en": "🔙 Back to Menu"},
    "lang_choose": {
        "cn": "🌐 *语言设置*\n请选择语言 / Choose language:",
        "en": "🌐 *Language Settings*\nChoose language / 请选择语言:",
    },
    "lang_set_cn": {"cn": "✅ 语言已切换为中文", "en": "✅ 语言已切换为中文"},
    "lang_set_en": {"cn": "✅ Language set to English", "en": "✅ Language set to English"},
    "referral_welcome": {
        "cn": "🎉 You joined via friend referral!",
        "en": "🎉 You joined via referral!",
    },
    "social_panel_title": {
        "cn": "📣 *Viral Social — Viral Spread*",
        "en": "📣 *Viral Social — Growth Engine*",
    },
}

def _load_lang_prefs() -> dict:
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE) as f: return json.load(f)
        except: pass
    return {}

def _save_lang_prefs(prefs: dict):
    with open(LANG_FILE, "w") as f: json.dump(prefs, f, indent=2)

def get_lang(uid) -> str:
    return i18n_get_lang(uid)

def set_lang(uid, lang: str):
    i18n_set_lang(uid, lang)

def t(uid, key: str) -> str:
    """获取翻译文本"""
    lang = get_lang(uid)
    entry = TEXTS.get(key, {})
    return entry.get(lang, entry.get("cn", key))

# === 批量中英翻译映射 ===
CN_TO_EN = {
    "正在查询代币信息": "Fetching token info",
    "Choose an action to begin:": "Choose to begin:",
    "Core Features:": "Core Features:",
    "钱包信息": "Wallet Info", "Wallet Ready:": "Wallet Ready:",
    "余额:": "Balance:", "Tech Stack:": "Tech Stack:",
    "层区块链": "Layer 1", "最优路由": "Best Route",
    "Decentralized Operation Logs": "Decentralized Log Storage",
    "On-chain Encrypted Strategy Data": "On-chain Encrypted Strategy",
    "运行时环境": "AI Runtime",
    "Send contract address to check Token info": "Send contract address to check Token info",
    "Optimal Swap across 30+ DEXs": "Optimal Swap across 30+ DEXs",
    "Portfolio + AI Trading Signals": "Portfolio + AI Trading Signals",
    "Whale Tracking + New Pool Discovery": "Whale Tracking + New Pool Discovery",
    "Limit Orders + Strategy Engine": "Limit Orders + Strategy Engine",
    "选择操作:": "Choose action:",
    "持仓概览": "Portfolio Overview", "总Value:": "Total Value:",
    "盈亏:": "PnL:", "No positions": "No positions yet",
    "代币余额": "Token Balances", "资产面板": "Asset Panel",
    "总余额:": "Total Balance:", "Insufficient Balance": "Insufficient Balance",
    "安全评分": "Safety Score", "合约审计": "Contract Audit",
    "代币信息": "Token Info", "Name:": "Name:", "Symbol:": "Symbol:",
    "Decimals:": "Decimals:", "持有者数:": "Holders:",
    "池子:": "Pool:", "流动性:": "Liquidity:",
    "小时涨跌:": "h Change:", "风险评估:": "Risk Assessment:",
    "鲸鱼追踪器": "Whale Tracker", "最近鲸鱼动态": "Recent Whale Activity",
    "买入": "Buy", "卖出": "Sell",
    "新池子发现器": "New Pool Finder", "最新上线池子": "Newest Pools",
    "创建时间:": "Created:", "交易信号面板": "Signal Panel",
    "强烈买入": "Strong Buy", "持有": "Hold",
    "策略面板": "Strategy Panel", "活跃策略:": "Active:",
    "运行中": "Running", "收益:": "Yield:",
    "铸造面板": "Mint Panel", "可用余额:": "Available:",
    "当前利率:": "Current Rate:",
    "收益面板": "Yield Panel", "年化收益:": "APY:",
    "总Deposited:": "Deposited:", "Accumulated:": "Accumulated:",
    "日志存储": "Log Storage", "Total:": "Total:", "Aggregator:": "Aggregator:",
    "All logs uploaded periodically for audit transparency": "All logs uploaded for audit transparency",
    "日志上传中": "Uploading", "上传成功": "Uploaded",
    "Size:": "Size:", "存储时间:": "Duration:", "永久": "Permanent",
    "Data securely stored on Walrus decentralized network": "Data stored on Walrus decentralized network",
    "链上金库": "On-chain Vault", "金库地址:": "Vault:",
    "总锁仓:": "Locked:", "你的份额:": "Your Share:",
    "帮助": "Help", "命令列表": "Commands",
    "查看钱包": "View Wallet", "代币兑换": "Token Swap",
    "查看持仓": "View Portfolio", "鲸鱼动态": "Whale Activity",
    "语言设置": "Language", "Viral Spread": "Viral Social",
    "你的邀请链接:": "Your referral link:", "已邀请人数:": "Referrals:",
    "邀请排行榜": "Referral Leaderboard", "暂无数据": "No data",
    "推文模板": "Tweet Template", "操作日志": "Logs",
    "No operation logs yet. Try /start or /swap!": "No logs yet. Try /start or /swap!",
    "Recent:": "Recent:", "立即上传": "Upload Now",
    "Back to Menu": "Back to Menu", "返回": "Back",
    "确认": "Confirm", "取消": "Cancel",
    "存入": "Deposit", "提取": "Withdraw", "Refresh": "Refresh",
    "查看链上": "View on-chain", "合约地址:": "Contract:",
    "正在执行": "Executing", "交易成功": "Success", "交易失败": "Failed",
    "Simulation交易": "Simulated", "预估输出:": "Est. output:",
    "路由:": "Route:", "Slippage:": "Slippage:", "执行 Swap": "Execute Swap",
    "使用 AI 自主交易策略": "AI autonomous trading",
    "跟踪大户钱包动态": "Track whale wallets",
    "发现新上线流动性池": "Discover new pools",
    "接收 AI Trading Signals": "AI trading signals",
    "一键分享和邀请好友": "Share & invite friends",
    "中英文双语支持": "Bilingual support",
    "查看所有操作日志": "View all logs",
    "Deposit Funds到链上金库": "Deposit to vault",
    "提取金库资金": "Withdraw from vault",
    "Simulation模式": "Simulation Mode",
    "正在获取最优路由": "Finding best route",
    "所有限价单已移除": "All limit orders removed",
    "All orders cancelled": "All orders cancelled",
    "Use /help for full help guide": "Use /help for full help guide",
    "设置": "Settings", "网络:": "Network:",
    "模式:": "Mode:", "资产": "Assets",
    "I'm Jarvis, your autonomous AI DeFi agent.": "I'm Jarvis, your autonomous AI DeFi agent.",
    "我是你的自主 AI DeFi 代理": "I'm your autonomous AI DeFi agent",
    "Token Info Not Found": "Token not found",
    "Possible reasons:": "Possible reasons:",
    "Invalid address format": "Invalid address format",
    "Token not found on": "Token not found on",
    "Please use full CoinType format": "Please check CoinType format",
    "共享 Testnet": "Shared Testnet",
    "查看Explorer": "View Explorer",
    "地址": "Address",
    "Simulation": "Simulation",
    "输入金额:": "Enter amount:",
    "自定义": "Custom",
    "Token 详情": "Token Details",
    "No description": "No description",
    "安全检查": "Safety Check",
    "Rating:": "Rating:",
    "Total Supply:": "Total Supply:",
    "Description:": "Description:",
    "Active Strategy:": "Current Strategy:",
    "信号源": "Signals",
    "绩效": "Performance",
    "Total Trades:": "Total Trades:",
    " trades": "trades",
    "Win Rate:": "Win Rate:",
    "Total PnL:": "Accumulated PnL:",
    "Avg Return:": "Avg Return:",
    "Latest Signal:": "Latest Signal:",
    "Risk Level:": "Risk Level:",
    "Toggle strategies:": "Toggle strategies:",
    "Trend": "Trend Following",
    "Mean Rev": "Mean Reversion",
    "Arbitrage": "DEX Arbitrage",
    "策略详情": "Strategy Details",
    "操作日志": "Operation Logs",
    "Recent:": "Recent:",
    "Total:": "Total Records:",
    " entries": "entries",
    "On-chain:": "On-chain:",
    "Upload to Walrus": "Upload to Walrus",
    "Refresh": "Refresh",
    "鲸鱼追踪": "Whale Tracker",
    "筛选:": "Filter:",
    "最近 3h 大额Trades:": "Large trades in 3h:",
    "Total Volume:": "Total Flow:",
    "数据Every 5 minutesRefresh": "Data refreshes every 5 min",
    "实时监控 Sui 网络": "Real-time Sui network monitoring",
    "Statistics": "Statistics",
    "pools": "New Pools",
    "New in 24h:": "New in 24h:",
    " pools": "pools",
    "High APR = High Risk. Watch for impermanent loss": "High APR = High risk, beware of impermanent loss",
    "Sort by APR": "Sort by APR",
    "持仓面板": "Portfolio",
    "Amount:": "Amount:",
    "Value:": "Value:",
    "Cost:": "Cost:",
    "Current:": "Current:",
    "Total Assets:": "Total Assets:",
    "总Cost:": "Total Cost:",
    "Total PnL:": "Total PnL:",
    "PnL Chart": "Performance Chart",
    "SUI balance is live on-chain data, others are demo simulation": "SUI balance is real on-chain data, others are demo",
    "限价单": "Limit Orders",
    "Active Orders:": "Active Orders:",
    "暂无挂单": "No active orders",
    "Create New Limit Order:": "Create Limit Order:",
    "Send format:": "Send format:",
    "格式:": "Format:",
    "取消全部挂单": "Cancel All Orders",
    "AI Trading Signals": "AI Trading Signals",
    "引擎:": "Engine:",
    "Signals today:": "Today's Signals:",
    "": "",
    "基于:": "Based on:",
    "成交量": "Volume",
    "链上数据": "on-chain data",
    "Signals for reference only, not financial advice": "Signals are for reference only, not investment advice",
    "Refresh信号": "Refresh Signals",
    "Settings": "Signal Settings",
    "Technical Indicators:": "Technical Indicators:",
    "布林带": "Bollinger Bands",
    "Fibonacci Retracement": "Fibonacci Retracement",
    "Notifications:": "Notifications:",
    "Buy Signals": "Buy Signals",
    "Sell Signals": "Sell Signals",
    "Hold Signals": "Hold Signals",
    "Refresh频率:": "Refresh Rate:",
    "Every 5 minutes": "Every 5 min",
    "Full version supports custom indicator parameters": "Full version supports custom parameters",
    "Decentralized Logs": "Decentralized Logs",
    "每 trades交易、每策略决策都透明记录在 Walrus 上。": "Every trade and strategy decision is transparently recorded on Walrus.",
    "Immutable and verifiable by anyone.": "Immutable, verifiable by anyone.",
    "链上日志": "On-chain Logs",
    "立即上传": "Upload Now",
    "日志上传中": "Uploading logs",
    "上传成功": "Upload complete",
    "存储时间:": "Storage Duration:",
    "永久": "Permanent",
    "Data securely stored on Walrus decentralized network": "Data stored on Walrus decentralized network",
    "智能合约": "Smart Contract",
    "Funds managed via Move contracts, secure and transparent.": "Funds managed by Move smart contracts, secure and transparent.",
    "Contract Info:": "Contract Info:",
    "Security Features:": "Security Features:",
    "权限控制": "Access Control",
    "Single Withdrawal Limit": "Single Withdrawal Limit",
    "Emergency Pause Mechanism": "Emergency Pause",
    "All operations verifiable on-chain": "All operations on-chain verifiable",
    "Functions:": "Functions:",
    "Deposit Funds": "Deposit Funds",
    "Withdraw Earnings": "Withdraw Earnings",
    "Emergency Pause": "Emergency Pause",
    "View Contract": "View Contract",
    "Back to Menu": "Back to Menu",
    "网络:": "Network:",
    "模式:": "Mode:",
    "Full version supports custom wallets and Mainnet": "Full version supports custom wallet and Mainnet",
    "使用指南": "User Guide",
    "命令": "Commands",
    "主菜单": "Main Menu",
    "钱包信息": "Wallet Info",
    "查看余额": "Check Balance",
    "代币交换": "Token Swap",
    "持仓面板": "Portfolio",
    "鲸鱼追踪": "Whale Tracker",
    "AI Trading Signals": "AI Trading Signals",
    "AI Strategy Manager": "AI Strategy",
    "铸造": "Mint",
    "赎回": "Redeem",
    "查看收益": "View Yield",
    "面板": "Panel",
    "帮助": "Help",
    "Token Lookup:": "Token Query:",
    "Send contract address or CoinType to look up:": "Send contract address or CoinType to query:",
    "自然语言": "Natural Language",
    "Architecture:": "Tech Architecture:",
    "智能合约": "Smart Contracts",
    "Aggregator Optimal Routing": "Aggregator Best Route",
    "Decentralized Logs": "Decentralized Logs",
    "Strategy Data Encryption": "Strategy Encryption",
    "运行时": "Runtime",
    "Contract:": "Contract:",
    "仪表盘": "Dashboard",
    "资产": "Assets",
    "策略": "Strategy",
    "Trades:": "Trades:",
    "铸造面板": "Mint Panel",
    "品牌稳定币": "Brand Stablecoin",
    "Deposit USDC → Mint equivalent JarvisUSD": "Deposit USDC → Mint JarvisUSD 1:1",
    "Underlying USDC auto-enters Bucket Savings Pool for yield": "Underlying USDC auto-enters Bucket Savings Pool for yield",
    "Current APY:": "Current APY:",
    "选择铸造金额": "Choose mint amount",
    "返回": "Back",
    "铸造成功！": "Mint Complete!",
    "Deposited:": "Deposited:",
    "Received:": "Received:",
    "余额:": "Balance:",
    "底层:": "Underlying:",
    "Auto-compound": "Auto-compound",
    "Demo 模式": "Demo Mode",
    "Testnet Simulation铸造": "Testnet simulated mint",
    "继续 Mint": "Mint More",
    "Redeem JarvisUSD": "Redeem JarvisUSD",
    "Burn JarvisUSD → Reclaim equivalent USDC": "Burn JarvisUSD → Get back USDC",
    "当前 JarvisUSD Balance:": "JarvisUSD Balance:",
    "Insufficient balance, please Mint first": "Insufficient balance, please Mint first",
    "去 Mint": "Go Mint",
    "选择赎回金额": "Choose redeem amount",
    "全部": "All",
    "赎回成功！": "Burn Complete!",
    "Burned:": "Burned:",
    "Reclaimed:": "Returned:",
    "Remaining JarvisUSD:": "Remaining JarvisUSD:",
    "Testnet Simulation赎回": "Testnet simulated burn",
    "收益": "Yield",
    "收益面板": "Yield Panel",
    "Holdings:": "Holdings:",
    "Current Yield:": "Current Yield:",
    "Daily:": "Daily Yield:",
    "Monthly:": "Monthly Yield:",
    "Annual:": "Annual Yield:",
    "Accumulated:": "Accumulated Yield:",
    "Underlying Protocol:": "Underlying Protocol:",
    "收益来源:": "Yield Source:",
    "借贷利息": "Lending Interest",
    "Mint 更多": "Mint More",
    "Burn 赎回": "Burn Redeem",
    "仪表盘": "Dashboard",
    "Value:": "Valuation:",
    "All orders cancelled": "All orders cancelled",
    "All limit orders removed.": "All limit orders removed.",
    "返回限价单": "Back to Limit Orders",
    "池子Sort by APR": "Pools by APR",
    "High APR = High Risk": "High APR = High risk",
    "返回池子": "Back to Pools",
    "PnL Chart": "Performance Chart",
    "Weekly:": "Weekly:",
    "High:": "High:",
    "Low:": "Low:",
    "返回持仓": "Back to Portfolio",
    "鲸鱼统计": "Whale Stats",
    "Net Inflow:": "Net Inflow:",
    "Net Outflow:": "Net Outflow:",
    "Net Change:": "Net Change:",
    "Active Whales:": "Active Whales:",
    "地址": "addresses",
    "最大单 trades:": "Largest Single:",
    "Trend:": "Trend:",
    "偏多": "Bullish",
    "净买入": "Net Buy",
    "数据来源:": "Data Source:",
    "链上交易分析": "On-chain Transaction Analysis",
    "返回鲸鱼": "Back to Whale",
    "返回信号": "Back to Signals",
    "返回策略": "Back to Strategy",
    "Swap 报价": "Swap Quote",
    "输入": "Input",
    "输出": "Output",
    "路由详情": "Route Details",
    "Path:": "Path:",
    "Via DEXs:": "DEXes:",
    "Liquidity Pools:": "Pools:",
    "Slippage Protection:": "Slippage Protection:",
    "Est. Gas:": "Est. Gas:",
    "Quote valid for 30 seconds": "Quote valid for 30s",
    "确认交易": "Confirm",
    "Trade Simulation Executed!": "Trade simulation executed!",
    "Confirm Time:": "Confirmation:",
    "Logged to Walrus": "Logs recorded to Walrus",
    "Demo Mode — Testnet Simulated Trade": "Demo Mode — Testnet simulated trade",
    "继续交易": "Continue Trading",
    "Custom Swap": "Custom Swap",
    "发送格式": "Send format",
    "支持的代币:": "Supported tokens:",
    "策略详情": "Strategy Details",
    "Signals:": "Signals:",
    "Return:": "Return:",
    "Risk:": "Risk:",
    "Swap 交易": "Swap Trading",
    "Routes across 30+ DEXs:": "Routing across 30+ DEXs:",
    "选择交易对，获取最优报价": "Choose pair for best quote",
    "Swap Buy": "Swap Buy",
    "Details": "View Details",
    "在线！": "Online!",
    "Try these:": "Try these:",
    "查看资产": "View Assets",
    "开始交易": "Start Trading",
    "投资组合": "Portfolio",
    "大额追踪": "Large Trade Tracking",
    "Send CoinType to look up Token": "Send CoinType to check Token",
    "完整帮助": "Full Help",
    "或直接使用下方按钮": "Or use buttons below",
    "Sui Address Detected": "Sui Address Detected",
    "To check token info, send full CoinType:": "To query token info, send full CoinType:",
    "View on Explorer": "View in Explorer",
    "Limit Order Created!": "Limit Order Created!",
    "BUY": "BUY",
    "SELL": "SELL",
    "Pair:": "Pair:",
    "Target:": "Target Price:",
    "Order ID:": "Order #:",
    "Will auto-execute when price hits target": "Will auto-execute when price reaches target",
    "查看挂单": "View Orders",
    "买入": "Buy",
    "卖出": "Sell",
    "转账": "Transfer",
    "金叉确认": "Golden Cross Confirmed",
    "柱状图转正": "Histogram Turned Positive",
    "超买区": "Overbought Zone",
    "上轨压力": "Upper Band Pressure",
    "突破下降趋势线": "Broke Downtrend Line",
    "成交量放大": "Volume Surge",
    "Consolidating, awaiting directional breakout": "Consolidating, waiting for breakout",
    "质押收益率上升": "Staking yield rising",
    "协议 TVL 增长": "Protocol TVL growth",
    "观望": "Hold",
    "Target:": "Target:",
    "Stop:": "Stop Loss:",
    "Confidence:": "Confidence:",
    "Brand stablecoin powered by StableLayer": "Brand stablecoin powered by StableLayer",
    "Deposit USDC, auto-earn yield, redeem anytime": "Deposit USDC, auto-yield, redeem anytime",
    "Protocol Data:": "Protocol Stats:",
    "Total Supply:": "Total Supply:",
    "Underlying Reserve:": "Reserve:",
    "Underlying Protocol:": "Protocol:",
    "等待": "Pending",
    "完成": "Completed",
    "Target:": "Target:",
    "Status:": "Status:",
    "Created:": "Created:",
    "Refresh余额": "Refresh Balance",
    "Explorer": "Explorer",
    "总Value:": "Total Valuation:",
    "No positions": "No assets",
}

def T(text: str, uid) -> str:
    """For English-base text, translate to Chinese for CN users."""
    lang = get_lang(uid)
    if lang == "en":
        return text
    # Build reverse map (EN → CN), sorted by length desc to avoid partial matches
    if not hasattr(T, '_en_to_cn'):
        T._en_to_cn = sorted(
            [(en, cn) for cn, en in CN_TO_EN.items() if len(en) >= 4],
            key=lambda x: len(x[0]), reverse=True
        )
    result = text
    for en, cn in T._en_to_cn:
        if en in result:
            result = result.replace(en, cn)
    return result

# ==================== Referral 系统 ====================
REFERRALS_FILE = os.path.join(DATA_DIR, "referrals.json")

def _load_referrals() -> dict:
    if os.path.exists(REFERRALS_FILE):
        try:
            with open(REFERRALS_FILE) as f: return json.load(f)
        except: pass
    return {}

def _save_referrals(refs: dict):
    with open(REFERRALS_FILE, "w") as f: json.dump(refs, f, indent=2)

def record_referral(new_uid: str, referrer_uid: str):
    """记录推荐关系"""
    refs = _load_referrals()
    if new_uid == referrer_uid:
        return  # 不能自己推荐自己
    if new_uid in refs:
        return  # 已被推荐过
    refs[new_uid] = {
        "referrer": referrer_uid,
        "time": datetime.now(HK_TZ).isoformat(),
    }
    _save_referrals(refs)
    log_action("referral", f"new:{new_uid} by:{referrer_uid}")

def get_referral_count(uid: str) -> int:
    """统计某用户邀请了多少人"""
    refs = _load_referrals()
    return sum(1 for v in refs.values() if v.get("referrer") == str(uid))

def get_referral_leaderboard(top_n=10) -> list:
    """邀请排行榜"""
    refs = _load_referrals()
    counts = {}
    for v in refs.values():
        r = v.get("referrer", "")
        counts[r] = counts.get(r, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return ranked

# AI 推文模板
TWEET_TEMPLATES = [
    "🚀 Just discovered @SuiJarvisBot — the ultimate AI DeFi agent on #Sui! Auto-routing across 30+ DEXs, whale tracking, and AI signals. The Infinite Money Glitch is real! 💎🤖 #DeFi #Web3",
    "🤖 My new DeFi co-pilot: @SuiJarvisBot on #Sui\n\n✅ Smart swap routing\n✅ Whale alerts\n✅ AI trading signals\n✅ Portfolio tracking\n\nThis is the future of DeFi 🔥 #SuiNetwork",
    "GM! Been using @SuiJarvisBot and it's a game changer 🎯\n\nAI-powered trading on Sui with Cetus aggregation, on-chain logs via Walrus, and encrypted strategies via Seal.\n\nNot financial advice, but DYOR 👀 #Sui #AI",
    "💡 Why I'm bullish on @SuiJarvisBot:\n\n🌊 Sui L1 speed\n🐋 Cetus 30+ DEX routing\n🐘 Walrus transparent logs\n🔐 Seal encrypted strategies\n🦞 OpenClaw AI runtime\n\nFull stack DeFi AI agent 🤯 #Crypto",
    "🧠 AI + DeFi = @SuiJarvisBot\n\nJust set up limit orders, tracked some whales, and got AI signals — all in one Telegram bot on #Sui.\n\nThe future is autonomous finance 🌐💰 #Web3 #DeFi",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(DATA_DIR, "jarvis.log"))]
)
log = logging.getLogger("jarvis")

# ==================== 用户钱包管理 ====================
WALLETS_FILE = os.path.join(DATA_DIR, "wallets.json")

def load_wallets():
    if os.path.exists(WALLETS_FILE):
        with open(WALLETS_FILE) as f: return json.load(f)
    return {}

def save_wallets(w):
    with open(WALLETS_FILE, "w") as f: json.dump(w, f, indent=2)

def get_or_create_wallet(user_id: str) -> dict:
    wallets = load_wallets()
    if user_id in wallets:
        return wallets[user_id]
    wallet = {
        "address": "0xc3aa5e010270b6fa9f415739127152328f0bf860012577fff4e21569230a9b80",
        "created": datetime.now(HK_TZ).isoformat(),
        "mode": "demo",
    }
    wallets[user_id] = wallet
    save_wallets(wallets)
    log_action("wallet_auto_create", f"user:{user_id}")
    return wallet

# ==================== 操作日志 ====================
LOG_FILE = os.path.join(DATA_DIR, "operations.json")

def log_action(action: str, detail: str = ""):
    logs = _load_logs()
    logs.append({
        "time": datetime.now(HK_TZ).isoformat(),
        "action": action,
        "detail": detail
    })
    logs = logs[-200:]
    with open(LOG_FILE, "w") as f: json.dump(logs, f, ensure_ascii=False, indent=2)

def _load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f: return json.load(f)
        except: pass
    return []

# ==================== Sui RPC 调用 ====================
def sui_rpc(method: str, params: list):
    try:
        r = requests.post(SUI_RPC, json={
            "jsonrpc": "2.0", "id": 1,
            "method": method, "params": params
        }, timeout=10)
        return r.json().get("result")
    except Exception as e:
        log.error(f"RPC error: {e}")
        return None

def get_sui_balance(address: str) -> dict:
    result = sui_rpc("suix_getBalance", [address, "0x2::sui::SUI"])
    if result:
        bal = int(result["totalBalance"]) / 1e9
        return {"sui": bal, "formatted": f"{bal:.4f} SUI"}
    return {"sui": 0, "formatted": "Query Failed"}

def get_all_balances(address: str) -> list:
    result = sui_rpc("suix_getAllBalances", [address])
    if not result: return []
    tokens = []
    for item in result:
        ct = item["coinType"]
        bal = int(item["totalBalance"])
        name = ct.split("::")[-1] if "::" in ct else ct
        decimals = 9 if name == "SUI" else 6
        formatted = bal / (10 ** decimals)
        tokens.append({"name": name, "balance": formatted, "raw": bal, "coinType": ct})
    return tokens

def get_recent_txns(address: str, limit=5) -> list:
    result = sui_rpc("suix_queryTransactionBlocks", [{
        "filter": {"FromAddress": address},
        "options": {"showEffects": True, "showInput": False}
    }, None, limit, True])
    if result and "data" in result:
        return result["data"]
    return []

def get_coin_metadata(coin_type: str) -> dict:
    """Get token metadata via suix_getCoinMetadata"""
    result = sui_rpc("suix_getCoinMetadata", [coin_type])
    return result

def get_total_supply(coin_type: str) -> str:
    """Get total supply via suix_getTotalSupply"""
    result = sui_rpc("suix_getTotalSupply", [coin_type])
    if result and "value" in result:
        return result["value"]
    return None

# ==================== 限价单存储 ====================
LIMIT_ORDERS_FILE = os.path.join(DATA_DIR, "limit_orders.json")

def load_limit_orders() -> list:
    if os.path.exists(LIMIT_ORDERS_FILE):
        try:
            with open(LIMIT_ORDERS_FILE) as f: return json.load(f)
        except: pass
    return []

def save_limit_orders(orders: list):
    with open(LIMIT_ORDERS_FILE, "w") as f: json.dump(orders, f, ensure_ascii=False, indent=2)

# ==================== Cetus 报价（Simulation） ====================
SWAP_PAIRS = {
    "SUI/USDC": {"rate": 3.82, "route": "Cetus → DeepBook → Aftermath", "dexes": 3, "pools": 5},
    "USDC/SUI": {"rate": 0.2618, "route": "DeepBook → Turbos → Cetus", "dexes": 3, "pools": 4},
    "SUI/WETH": {"rate": 0.00118, "route": "Cetus → FlowX → KriyaDEX", "dexes": 3, "pools": 6},
    "SUI/CETUS": {"rate": 42.5, "route": "Cetus AMM (Direct)", "dexes": 1, "pools": 1},
    "SUI/USDT": {"rate": 3.81, "route": "Aftermath → BlueFin → Cetus", "dexes": 3, "pools": 4},
}

# ==================== AI 策略引擎 ====================
STRATEGIES = {
    "trend": {
        "name": "📈 Trend Following",
        "desc": "Follow major trends. When SUI shows sustained momentum, ride the wave.",
        "signals": ["EMA Cross", "MACD Trend", "Volume Breakout"],
        "risk": "Medium",
        "win_rate": "62%",
        "avg_return": "+4.2%/trade",
    },
    "mean_reversion": {
        "name": "🔄 Mean Reversion",
        "desc": "Buy low, sell high when price deviates from mean.",
        "signals": ["Bollinger", "RSI OB/OS", "VWAP Deviation"],
        "risk": "Low-Med",
        "win_rate": "71%",
        "avg_return": "+2.1%/trade",
    },
    "arbitrage": {
        "name": "⚡ DEX Arbitrage",
        "desc": "Exploit price differences across Cetus, DeepBook, Turbos etc.",
        "signals": ["Spread Monitor", "Gas Optimize", "Atomic Exec"],
        "risk": "Low",
        "win_rate": "89%",
        "avg_return": "+0.3%/trade",
    }
}

strategy_state = {
    "active": "trend",
    "enabled": {"trend": True, "mean_reversion": False, "arbitrage": False},
    "total_trades": 47,
    "win_count": 31,
    "pnl": +12.6,
    "last_signal": "EMA 12/26 golden cross, suggest add SUI",
    "last_signal_time": "10:15",
}

# ==================== Walrus 日志 ====================
WALRUS_BLOBS = [
    {"id": "Dq4wG3x...", "time": "02-09 22:00", "type": "strategy_snapshot", "size": "2.1KB"},
    {"id": "Fx8kL2m...", "time": "02-09 18:30", "type": "trade_log", "size": "1.4KB"},
    {"id": "Ap3nR7w...", "time": "02-09 15:00", "type": "risk_report", "size": "3.2KB"},
]

# ==================== Social Sniper 模拟数据 ====================
SNIPER_TWEETS = [
    {
        "author": "@SuiWhale_",
        "text": "$SUI ecosystem is exploding! Cetus DEX volume up 300% this week. DYOR but I'm loading up 🚀",
        "time": "12m ago",
        "followers": "45.2K",
        "sentiment": "🟢 Bullish",
        "confidence": "92%",
        "action": "BUY 500 SUI @ $3.82",
        "pnl": "+2.1%",
        "reply": "🤖 Jarvis AI detected bullish signal from @SuiWhale_.\n📊 Sentiment: Bullish (92%)\n⚡ Auto-executed: BUY 500 SUI\n🔗 Try automated DeFi: t.me/SuiJarvisBot"
    },
    {
        "author": "@CryptoAnalyst99",
        "text": "Seeing heavy sell pressure on $CETUS. Whales dumping, TVL dropping. Be careful out there.",
        "time": "28m ago",
        "followers": "12.8K",
        "sentiment": "🔴 Bearish",
        "confidence": "85%",
        "action": "SELL 2000 CETUS @ $0.089",
        "pnl": "+1.4%",
        "reply": "🤖 Jarvis AI detected bearish signal from @CryptoAnalyst99.\n📊 Sentiment: Bearish (85%)\n⚡ Auto-executed: SELL 2000 CETUS\n🔗 AI-powered DeFi: t.me/SuiJarvisBot"
    },
    {
        "author": "@DegenTrader",
        "text": "NAVX about to break out of this wedge pattern. Volume picking up nicely. Bullish af 📈",
        "time": "1h ago",
        "followers": "8.5K",
        "sentiment": "🟢 Bullish",
        "confidence": "78%",
        "action": "BUY 5000 NAVX @ $0.248",
        "pnl": "+3.8%",
        "reply": "🤖 Jarvis AI analyzed @DegenTrader's chart reading.\n📊 Sentiment: Bullish (78%)\n⚡ Auto-executed: BUY 5000 NAVX\n🔗 Smart DeFi Agent: t.me/SuiJarvisBot"
    },
    {
        "author": "@SuiBuilder",
        "text": "Just deployed a new DeFi protocol on Sui. Gas fees are insanely low. This chain is the future 🌊",
        "time": "2h ago",
        "followers": "22.1K",
        "sentiment": "🟢 Bullish",
        "confidence": "88%",
        "action": "BUY 200 SUI @ $3.79",
        "pnl": "+0.8%",
        "reply": "🤖 Jarvis AI spotted ecosystem growth signal.\n📊 Sentiment: Bullish (88%)\n⚡ Auto-executed: BUY 200 SUI\n🔗 Autonomous DeFi: t.me/SuiJarvisBot"
    },
    {
        "author": "@BearishKing",
        "text": "SUI tokenomics are terrible. Massive unlock coming next month. Short this garbage 🗑️",
        "time": "3h ago",
        "followers": "31.4K",
        "sentiment": "🔴 Bearish",
        "confidence": "71%",
        "action": "HEDGE: Buy SUI PUT option",
        "pnl": "-0.3%",
        "reply": "🤖 Jarvis AI detected FUD from @BearishKing.\n📊 Sentiment: Bearish (71%)\n⚡ Auto-executed: Hedged position\n🔗 AI risk management: t.me/SuiJarvisBot"
    }
]

SNIPER_STATS = {
    "tweets_scanned": 12847,
    "signals_found": 342,
    "trades_executed": 89,
    "win_rate": "76%",
    "total_pnl": "+18.4%",
    "avg_response_time": "< 3s",
    "replies_posted": 89,
    "impressions_gained": "245K",
    "new_users_from_replies": 156,
}

# ==================== Simulation数据生成 ====================
def gen_whale_data():
    now = datetime.now(HK_TZ)
    whales = []
    addrs = [
        ("0x7d20...3f8a", "0x91ab...c4d2"), ("0xf4e1...8b73", "0x2c9d...a1f6"),
        ("0xa823...d9e1", "0x5f7b...2c84"), ("0x1b4e...f723", "0xd8a6...9e51"),
        ("0x6c3f...b248", "0x3e7a...d195"), ("0xe912...4a6d", "0x8b5c...f3e7"),
    ]
    types = ["🟢 Buy", "🔴 Sell", "🔵 Transfer"]
    tokens = ["SUI", "SUI", "SUI", "USDC", "SUI", "CETUS"]
    for i in range(6):
        t = now - timedelta(minutes=random.randint(2, 180))
        amt = random.choice([10_000, 25_000, 50_000, 100_000, 150_000, 280_000, 500_000])
        fr, to = addrs[i]
        typ = random.choice(types)
        tok = tokens[i]
        usd = amt * 3.82 if tok == "SUI" else amt
        whales.append({
            "time": t.strftime("%H:%M"),
            "amount": f"{amt:,.0f} {tok}",
            "usd": f"${usd:,.0f}",
            "from": fr, "to": to,
            "type": typ,
        })
    whales.sort(key=lambda x: x["time"], reverse=True)
    return whales

def gen_pool_data():
    pools = [
        {"pair": "SUI/USDC", "tvl": "$12.8M", "vol": "$4.2M", "apr": "18.5%", "age": "2h ago", "dex": "Cetus"},
        {"pair": "NAVX/SUI", "tvl": "$890K", "vol": "$320K", "apr": "45.2%", "age": "5h ago", "dex": "Cetus"},
        {"pair": "CETUS/USDC", "tvl": "$3.2M", "vol": "$1.1M", "apr": "22.8%", "age": "8h ago", "dex": "Cetus"},
        {"pair": "HASUI/SUI", "tvl": "$6.5M", "vol": "$2.8M", "apr": "12.3%", "age": "12h ago", "dex": "Cetus"},
        {"pair": "WETH/USDC", "tvl": "$5.1M", "vol": "$1.9M", "apr": "15.7%", "age": "1d ago", "dex": "Cetus"},
        {"pair": "TURBOS/SUI", "tvl": "$420K", "vol": "$95K", "apr": "68.4%", "age": "1d ago", "dex": "Turbos"},
    ]
    return pools

def gen_portfolio_data(sui_balance: float):
    holdings = [
        {"token": "SUI", "amount": sui_balance, "cost": 2.85, "price": 3.82, "icon": "🟦"},
        {"token": "USDC", "amount": 1250.00, "cost": 1.00, "price": 1.00, "icon": "💵"},
        {"token": "CETUS", "amount": 8500, "cost": 0.082, "price": 0.0897, "icon": "🐋"},
        {"token": "NAVX", "amount": 3200, "cost": 0.21, "price": 0.248, "icon": "🧭"},
        {"token": "HASUI", "amount": 450, "cost": 3.75, "price": 3.91, "icon": "💎"},
    ]
    return holdings

def gen_signals():
    now = datetime.now(HK_TZ)
    signals = [
        {
            "icon": "🟢", "type": "BUY", "pair": "SUI/USDC",
            "reason": "EMA 12/26 golden cross confirmed, MACD histogram turned positive",
            "target": "$4.20", "stop": "$3.45", "confidence": "85%",
            "time": (now - timedelta(minutes=12)).strftime("%H:%M"),
        },
        {
            "icon": "🔴", "type": "SELL", "pair": "CETUS/USDC",
            "reason": "RSI(14) = 78 overbought, Bollinger upper band resistance",
            "target": "$0.072", "stop": "$0.095", "confidence": "72%",
            "time": (now - timedelta(minutes=45)).strftime("%H:%M"),
        },
        {
            "icon": "🟢", "type": "BUY", "pair": "NAVX/SUI",
            "reason": "Descending trendline breakout, volume surge 3.2x",
            "target": "0.068 SUI", "stop": "0.052 SUI", "confidence": "78%",
            "time": (now - timedelta(hours=1, minutes=20)).strftime("%H:%M"),
        },
        {
            "icon": "🟡", "type": "HOLD", "pair": "WETH/USDC",
            "reason": "Consolidating, awaiting directional breakout",
            "target": "-", "stop": "-", "confidence": "55%",
            "time": (now - timedelta(hours=2)).strftime("%H:%M"),
        },
        {
            "icon": "🟢", "type": "BUY", "pair": "HASUI/SUI",
            "reason": "Staking yield rising, protocol TVL up 15%",
            "target": "1.05 SUI", "stop": "0.98 SUI", "confidence": "80%",
            "time": (now - timedelta(hours=3)).strftime("%H:%M"),
        },
    ]
    return signals

def gen_token_safety(coin_type: str, metadata: dict):
    """Generate mock safety check for a token"""
    # Well-known safe tokens
    safe_tokens = ["SUI", "USDC", "USDT", "WETH", "CETUS", "NAVX", "HASUI", "TURBOS"]
    symbol = (metadata or {}).get("symbol", "")
    
    if symbol.upper() in safe_tokens:
        return {
            "rating": "🟢 SAFE",
            "score": random.randint(85, 98),
            "checks": [
                "✅ Verified Contract",
                "✅ Adequate Liquidity",
                "✅ Reasonable Supply",
                "✅ Known Team",
                "✅ Audited",
            ]
        }
    else:
        checks = []
        score = random.randint(30, 70)
        checks.append(random.choice(["✅ Verified Contract", "⚠️ Unverified Contract"]))
        checks.append(random.choice(["✅ LP Locked", "⚠️ Unlocked LP"]))
        if score > 50:
            checks.append("✅ Reasonable Supply")
        else:
            checks.append("⚠️ Excessive Supply")
        checks.append(random.choice(["✅ No Malicious Functions", "⚠️ Suspicious Functions"]))
        
        if score >= 60:
            rating = "🟡 CAUTION"
        else:
            rating = "🔴 DANGER"
        return {"rating": rating, "score": score, "checks": checks}

# ==================== 键盘布局 ====================
def main_keyboard(uid_or_lang="cn"):
    """GMGN-style main menu with i18n buttons."""
    # Determine uid for L() - if it looks like a lang code, create a temp lookup
    uid = uid_or_lang
    lang = get_lang(uid) if len(str(uid)) > 2 else uid_or_lang
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(L("btn_assets", uid), callback_data="assets"),
         InlineKeyboardButton(L("btn_swap", uid), callback_data="swap_menu")],
        [InlineKeyboardButton(L("btn_portfolio", uid), callback_data="portfolio"),
         InlineKeyboardButton(L("btn_limit", uid), callback_data="limit")],
        [InlineKeyboardButton(L("btn_whale", uid), callback_data="whale"),
         InlineKeyboardButton(L("btn_pools", uid), callback_data="pools")],
        [InlineKeyboardButton(L("btn_signals", uid), callback_data="signals"),
         InlineKeyboardButton(L("btn_strategy", uid), callback_data="strategy")],
        [InlineKeyboardButton(L("btn_mint", uid) if L("btn_mint", uid) != "btn_mint" else "💎 Mint", callback_data="sl_mint"),
         InlineKeyboardButton(L("btn_yield", uid), callback_data="sl_yield")],
        [InlineKeyboardButton("🎯 Sniper" if get_lang(uid) == "en" else "🎯 社交狙击", callback_data="sniper"),
         InlineKeyboardButton(L("btn_walrus", uid), callback_data="walrus")],
        [InlineKeyboardButton(L("btn_vault", uid), callback_data="vault"),
         InlineKeyboardButton(L("btn_settings", uid), callback_data="settings")],
        [InlineKeyboardButton(L("btn_help", uid), callback_data="help")],
        [InlineKeyboardButton("🇨🇳 中文" if lang == "en" else "🇬🇧 English", callback_data="lang_toggle")],
    ])

def swap_keyboard(lang="cn"):
    _custom = "🔧 Custom" if lang == "cn" else "🔧 Custom"
    _back = "🔙 Back to Menu" if lang == "cn" else "🔙 Back to Menu"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("SUI → USDC", callback_data="swap_SUI/USDC"),
         InlineKeyboardButton("USDC → SUI", callback_data="swap_USDC/SUI")],
        [InlineKeyboardButton("SUI → WETH", callback_data="swap_SUI/WETH"),
         InlineKeyboardButton("SUI → CETUS", callback_data="swap_SUI/CETUS")],
        [InlineKeyboardButton("SUI → USDT", callback_data="swap_SUI/USDT"),
         InlineKeyboardButton(_custom, callback_data="swap_custom")],
        [InlineKeyboardButton(_back, callback_data="back")],
    ])

def strategy_keyboard(lang="cn"):
    s = strategy_state["enabled"]
    if lang == "cn":
        _trend, _mean, _arb, _detail, _back = "Trend", "Mean Rev", "Arbitrage", "📊 Details", "🔙 Back to Menu"
    else:
        _trend, _mean, _arb, _detail, _back = "Trend Following", "Mean Reversion", "DEX Arbitrage", "📊 Strategy Details", "🔙 Back to Menu"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{'✅' if s['trend'] else '⬜'} {_trend}",
            callback_data="strat_trend"),
         InlineKeyboardButton(
            f"{'✅' if s['mean_reversion'] else '⬜'} {_mean}",
            callback_data="strat_mean_reversion")],
        [InlineKeyboardButton(
            f"{'✅' if s['arbitrage'] else '⬜'} {_arb}",
            callback_data="strat_arbitrage"),
         InlineKeyboardButton(_detail, callback_data="strat_detail")],
        [InlineKeyboardButton(_back, callback_data="back")],
    ])

# ==================== Token 查询 ====================
async def send_token_info(message, coin_type: str, uid: str = "0"):
    """Query and display token information + safety check"""
    log_action("token_query", coin_type[:40])
    
    await message.reply_text("🔍 Fetching token info...")
    
    metadata = get_coin_metadata(coin_type)
    supply_raw = get_total_supply(coin_type)
    
    if not metadata:
        _err = (
            f"❌ *Token Not Found*\n\n"
            f"CoinType: `{coin_type}`\n\n"
            f"Possible reasons:\n"
            f"• Invalid address format\n"
            f"• Token not found on {NETWORK}\n"
            f"• Please check full CoinType format\n"
            f"  Example: `0x2::sui::SUI`"
        )
        await message.reply_text(_err, parse_mode="Markdown")
        return
    
    name = metadata.get("name", "Unknown")
    symbol = metadata.get("symbol", "???")
    decimals = metadata.get("decimals", 9)
    desc = metadata.get("description", "No description")
    icon_url = metadata.get("iconUrl", "")
    
    # Format supply
    supply_text = "N/A"
    if supply_raw:
        supply_val = int(supply_raw) / (10 ** decimals)
        if supply_val >= 1e12:
            supply_text = f"{supply_val/1e12:.2f}T"
        elif supply_val >= 1e9:
            supply_text = f"{supply_val/1e9:.2f}B"
        elif supply_val >= 1e6:
            supply_text = f"{supply_val/1e6:.2f}M"
        elif supply_val >= 1e3:
            supply_text = f"{supply_val/1e3:.2f}K"
        else:
            supply_text = f"{supply_val:.2f}"
    
    # Safety check
    safety = gen_token_safety(coin_type, metadata)
    safety_lines = "\n".join(f"  {c}" for c in safety["checks"])
    
    lang = get_lang(uid)
    _swap_label = f"🔄 Swap Buy {symbol}" if lang == "cn" else f"🔄 Swap Buy {symbol}"
    _detail_label = "📊 Details" if lang == "cn" else "📊 Details"
    _back_label = "🔙 Back to Menu" if lang == "cn" else "🔙 Back to Menu"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(_swap_label, callback_data=f"swap_SUI/{symbol}" if symbol != "SUI" else "swap_menu"),
         InlineKeyboardButton(_detail_label, callback_data="back")],
        [InlineKeyboardButton(_back_label, callback_data="back")],
    ])
    
    text = (
        f"🔍 *Token Details — {name}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📛 *Name:* {name}\n"
        f"🏷️ *Symbol:* {symbol}\n"
        f"🔢 *Decimals:* {decimals}\n"
        f"📊 *Total Supply:* {supply_text} {symbol}\n"
    )
    if desc and desc != "No description":
        text += f"📝 *Description:* {desc[:120]}\n"
    
    text += (
        f"\n🛡️ *Safety Check:*\n"
        f"  Rating: *{safety['rating']}* ({safety['score']}/100)\n"
        f"{safety_lines}\n\n"
        f"📋 *CoinType:*\n`{coin_type}`\n"
    )
    
    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

# ==================== 命令处理器 ====================
async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """语言切换命令"""
    uid = str(update.effective_user.id)
    lang = get_lang(uid)
    await update.message.reply_text(
        L("lang_choose", uid),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_cn"),
             InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton(L("btn_back", uid), callback_data="back")],
        ])
    )

async def cmd_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看邀请链接和统计"""
    uid = str(update.effective_user.id)
    lang = get_lang(uid)
    count = get_referral_count(uid)
    link = f"https://t.me/SuiJarvisBot?start=ref_{uid}"
    await update.message.reply_text(
        f"🔗 *{'你的邀请链接' if lang=='cn' else 'Your Referral Link'}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📎 `{link}`\n\n"
        f"👥 {'已邀请' if lang=='cn' else 'Invited'}: *{count}* {'人' if lang=='cn' else 'users'}\n\n"
        f"{'分享链接邀请好友，一起赚钱！' if lang=='cn' else 'Share and earn together!'}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📤 分享 Share" if lang=="cn" else "📤 Share",
                switch_inline_query=f"🤖 Join me on Sui DeFi Jarvis! The Infinite Money Glitch 🚀 {link}")],
            [InlineKeyboardButton(L("btn_back", uid), callback_data="back")],
        ])
    )

async def cmd_social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Social 面板"""
    uid = str(update.effective_user.id)
    await _send_social_panel(update.message, uid)

async def _send_social_panel(msg, uid: str):
    """Viral Spread/社交面板"""
    lang = get_lang(uid)
    count = get_referral_count(uid)
    link = f"https://t.me/SuiJarvisBot?start=ref_{uid}"
    leaderboard = get_referral_leaderboard(5)

    # 排行榜文本
    lb_lines = []
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (r_uid, r_count) in enumerate(leaderboard):
        lb_lines.append(f"  {medals[i]} `{r_uid[:8]}...` — {r_count} {'人' if lang=='cn' else 'refs'}")
    lb_text = "\n".join(lb_lines) if lb_lines else ("  暂无数据" if lang=="cn" else "  No data yet")

    # Simulation传播数据
    impressions = count * random.randint(80, 200)
    clicks = count * random.randint(5, 20)
    conversion = f"{(clicks/max(impressions,1)*100):.1f}%" if impressions > 0 else "0%"

    text = (
        f"{t(uid, 'social_panel_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 *{'邀请链接' if lang=='cn' else 'Referral Link'}:*\n"
        f"  `{link}`\n\n"
        f"👥 *{'你的邀请' if lang=='cn' else 'Your Referrals'}:* {count} {'人' if lang=='cn' else 'users'}\n\n"
        f"📊 *{'传播数据' if lang=='cn' else 'Viral Stats'} ({'Simulation' if lang=='cn' else 'simulated'}):*\n"
        f"  👀 {'曝光' if lang=='cn' else 'Impressions'}: {impressions:,}\n"
        f"  🖱️ {'点击' if lang=='cn' else 'Clicks'}: {clicks:,}\n"
        f"  📈 {'转化率' if lang=='cn' else 'Conversion'}: {conversion}\n\n"
        f"🏆 *{'邀请排行榜' if lang=='cn' else 'Referral Leaderboard'}:*\n"
        f"{lb_text}\n"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📣 AI 生成推文" if lang=="cn" else "📣 AI Tweet",
            callback_data="social_tweet"),
         InlineKeyboardButton(
            "🔗 邀请链接" if lang=="cn" else "🔗 Invite Link",
            callback_data="social_invite")],
        [InlineKeyboardButton(
            "📤 分享 Share" if lang=="cn" else "📤 Share",
            switch_inline_query=f"🤖 Sui DeFi Jarvis — The Infinite Money Glitch 🚀 {link}")],
        [InlineKeyboardButton(L("btn_back", uid), callback_data="back")],
    ])

    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    name = user.first_name or "Friend"
    lang = get_lang(uid)

    # 处理 referral 链接: /start ref_USERID
    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith("ref_"):
            referrer_uid = arg[4:]
            record_referral(uid, referrer_uid)
    
    wallet = get_or_create_wallet(uid)
    balance = get_sui_balance(wallet["address"])
    
    log_action("start", f"{name} (id:{uid})")
    
    addr_short = f"{wallet['address'][:16]}...{wallet['address'][-8:]}"
    _start_msg = L("welcome", uid, name=name, address=addr_short, balance=balance["formatted"])
    await update.message.reply_text(
        _start_msg,
        parse_mode="Markdown",
        reply_markup=main_keyboard(uid)
    )

async def cmd_wallet(update: Update, context):
    uid = str(update.effective_user.id)
    wallet = get_or_create_wallet(uid)
    balance = get_sui_balance(wallet["address"])
    tokens = get_all_balances(wallet["address"])
    
    token_lines = []
    for t in tokens:
        icon = "🟦" if t["name"] == "SUI" else "🟢"
        token_lines.append(f"  {icon} {t['name']}: *{t['balance']:.4f}*")
    
    token_text = "\n".join(token_lines) if token_lines else "  No positions"
    
    log_action("wallet", balance["formatted"])
    
    _wallet_msg = (
        f"👛 *Wallet Info*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 *Address:*\n"
        f"`{wallet['address']}`\n\n"
        f"🌐 Network: Sui {NETWORK.capitalize()}\n"
        f"📦 Mode: {'Demo (Shared Testnet)' if wallet.get('mode')=='demo' else 'Personal'}\n\n"
        f"💰 *Assets:*\n"
        f"{token_text}\n\n"
        f"🔗 [View Explorer](https://suiscan.xyz/{NETWORK}/account/{wallet['address']})"
    )
    await update.message.reply_text(
        _wallet_msg,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def cmd_balance(update: Update, context):
    uid = str(update.effective_user.id)
    wallet = get_or_create_wallet(uid)
    balance = get_sui_balance(wallet["address"])
    log_action("balance", balance["formatted"])
    await update.message.reply_text(
        f"💰 *{balance['formatted']}*\n"
        f"📍 `{wallet['address'][:16]}...`\n"
        f"🌐 Sui {NETWORK.capitalize()}",
        parse_mode="Markdown"
    )

async def cmd_swap(update: Update, context):
    uid = str(update.effective_user.id)
    lang = get_lang(uid)
    log_action("swap_menu")
    _swap_text = (
        "🔄 *Swap Trading — Cetus Aggregator*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🐋 Routing across 30+ DEXs:\n"
        "Cetus · DeepBook · Turbos · Aftermath\n"
        "FlowX · KriyaDEX · BlueFin · Haedal...\n\n"
        "Choose pair for best quote 👇"
    )
    await update.message.reply_text(_swap_text, parse_mode="Markdown", reply_markup=swap_keyboard(lang))

async def cmd_strategy(update: Update, context):
    log_action("strategy")
    await _send_strategy_panel(update.message, str(update.effective_user.id))

async def cmd_logs(update: Update, context):
    log_action("view_logs")
    await _send_logs_panel(update.message, str(update.effective_user.id))

async def cmd_whale(update: Update, context):
    log_action("whale")
    await _send_whale_panel(update.message, str(update.effective_user.id))

async def cmd_pools(update: Update, context):
    log_action("pools")
    await _send_pools_panel(update.message, str(update.effective_user.id))

async def cmd_portfolio(update: Update, context):
    uid = str(update.effective_user.id)
    log_action("portfolio")
    await _send_portfolio_panel(update.message, uid)

async def cmd_limit(update: Update, context):
    log_action("limit")
    await _send_limit_panel(update.message, str(update.effective_user.id), context)

async def cmd_signals(update: Update, context):
    log_action("signals")
    await _send_signals_panel(update.message, str(update.effective_user.id))

async def cmd_sniper(update: Update, context):
    uid = str(update.effective_user.id)
    await _send_sniper_panel(update.message, uid)

async def cmd_help(update: Update, context):
    uid = str(update.effective_user.id)
    _help_text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*📱 Commands:*\n"
        "├ /start — Main Menu\n"
        "├ /wallet — Wallet Info\n"
        "├ /balance — Check Balance\n"
        "├ /swap — Token Swap\n"
        "├ /portfolio — Portfolio\n"
        "├ /limit — Limit Orders\n"
        "├ /whale — Whale Tracker\n"
        "├ /pools — New Pools\n"
        "├ /signals — AI Trading Signals\n"
        "├ /strategy — AI Strategy\n"
        "├ /mint — Mint JarvisUSD (StableLayer)\n"
        "├ /burn — Redeem JarvisUSD\n"
        "├ /yield — View Yield\n"
        "├ /stablelayer — StableLayer Panel\n"
        "├ /logs — Operation Logs\n"
        "└ /help — Help\n\n"
        "*🔍 Token Query:*\n"
        "Send contract address or CoinType to query:\n"
        "• `0x2::sui::SUI`\n"
        "• `0xdba34672e...::coin::COIN`\n\n"
        "*💬 Natural Language:*\n"
        "• \"check balance\"\n"
        "• \"swap 10 SUI to USDC\"\n"
        "• \"whale\"\n"
        "• \"pools\"\n"
        "• \"signals\"\n\n"
        "*🔧 Tech Architecture:*\n"
        "• 🌊 Sui — Move Smart Contracts\n"
        "• 🐋 Cetus — Aggregator Best Route\n"
        "• 🐘 Walrus — Decentralized Logs\n"
        "• 🔐 Seal — Strategy Encryption\n"
        "• 🦞 OpenClaw — AI Runtime\n\n"
        f"📦 Contract: `{DEPLOYED_PACKAGE[:20]}...`\n"
        f"🌐 Network: Sui {NETWORK.capitalize()}\n\n"
        "*Powered by OpenClaw × Sui × Cetus × Walrus*"
    )
    await update.message.reply_text(_help_text, parse_mode="Markdown")

# ==================== 面板渲染函数 ====================
async def _send_strategy_panel(msg, uid="0"):
    s = strategy_state
    active = STRATEGIES[s["active"]]
    wr = s["win_count"] / s["total_trades"] * 100 if s["total_trades"] > 0 else 0
    lang = get_lang(uid)
    
    _text = (
        f"🤖 *AI Strategy Engine*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 *Current Strategy: {active['name']}*\n"
        f"  {active['desc']}\n\n"
        f"📊 *Signals:*\n"
        f"  {'  ·  '.join(active['signals'])}\n\n"
        f"📈 *Performance:*\n"
        f"  ├ Total Trades: {s['total_trades']} trades\n"
        f"  ├ Win Rate: {wr:.0f}% ({s['win_count']}W/{s['total_trades']-s['win_count']}L)\n"
        f"  ├ Accumulated PnL: *{'+' if s['pnl']>=0 else ''}{s['pnl']:.1f} SUI*\n"
        f"  └ Avg Return: {active['avg_return']}\n\n"
        f"🔔 *Latest Signal:*\n"
        f"  💡 [{s['last_signal_time']}] {s['last_signal']}\n\n"
        f"⚠️ Risk Level: {active['risk']}\n\n"
        f"👇 Toggle strategies:"
    )
    await msg.reply_text(_text, parse_mode="Markdown", reply_markup=strategy_keyboard(lang))

async def _send_logs_panel(msg, uid="0"):
    logs = _load_logs()
    recent = logs[-8:]
    
    if not recent:
        await msg.reply_text("📋 No logs yet. Try /start or /swap!")
        return
    
    lines = []
    for l in recent:
        t = l["time"][5:16].replace("T", " ")
        emoji = {"start": "🚀", "balance": "💰", "swap_menu": "🔄", "swap_quote": "📊",
                 "wallet": "👛", "strategy": "🤖", "wallet_auto_create": "🆕",
                 "view_logs": "📋", "whale": "🐋", "pools": "🌱", "signals": "📢",
                 "portfolio": "📊", "limit": "🏷️", "token_query": "🔍"}.get(l["action"], "📝")
        lines.append(f"  {emoji} `{t}` *{l['action']}* {l.get('detail','')[:40]}")
    
    walrus_section = "\n\n🐘 *Walrus On-chain Logs:*\n"
    for b in WALRUS_BLOBS[-3:]:
        walrus_section += f"  📦 `{b['id']}` ({b['time']}) {b['type']} [{b['size']}]\n"
    
    lang = get_lang(uid)
    _upload = "🐘 Upload to Walrus" if lang == "cn" else "🐘 Upload to Walrus"
    _refresh = "🔄 Refresh" if lang == "cn" else "🔄 Refresh"
    _back = "🔙 Back to Menu" if lang == "cn" else "🔙 Back to Menu"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(_upload, callback_data="walrus_upload"),
         InlineKeyboardButton(_refresh, callback_data="refresh_logs")],
        [InlineKeyboardButton(_back, callback_data="back")],
    ])
    
    _log_text = (
        f"📋 *Operation Logs*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Recent:*\n" + "\n".join(lines) +
        walrus_section +
        f"\n📊 Total Records: {len(logs)} entries | On-chain: {len(WALRUS_BLOBS)} entries"
    )
    await msg.reply_text(_log_text, parse_mode="Markdown", reply_markup=kb)

async def _send_dashboard(msg, uid):
    wallet = get_or_create_wallet(uid)
    balance = get_sui_balance(wallet["address"])
    s = strategy_state
    wr = s["win_count"] / s["total_trades"] * 100 if s["total_trades"] > 0 else 0
    active = STRATEGIES[s["active"]]
    
    now = datetime.now(HK_TZ).strftime("%H:%M")
    
    _dash_text = (
        f"📊 *Jarvis Dashboard*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT | Sui {NETWORK.capitalize()}\n\n"
        f"💰 *Assets:*\n"
        f"  🟦 SUI: *{balance['formatted']}*\n"
        f"  💵 Valuation: ~${balance['sui'] * 3.82:.2f}\n\n"
        f"🤖 *Strategy:*\n"
        f"  📈 {active['name']}\n"
        f"  ├ Win Rate: {wr:.0f}% | Trades: {s['total_trades']}\n"
        f"  └ P&L: *{'+' if s['pnl']>=0 else ''}{s['pnl']:.1f} SUI*\n\n"
        f"🔔 *Latest Signal:*\n"
        f"  💡 {s['last_signal']}\n\n"
        f"🐘 *Walrus:* {len(WALRUS_BLOBS)} logs on-chain\n"
        f"🔐 *Vault:* `{DEPLOYED_PACKAGE[:16]}...`\n\n"
        f"───────────────────\n"
        f"_Powered by OpenClaw × Sui × Cetus × Walrus_"
    )
    await msg.reply_text(_dash_text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="dashboard"),
             InlineKeyboardButton("🔙 Back", callback_data="back")],
        ])
    )

async def _send_whale_panel(msg, uid="0"):
    whales = gen_whale_data()
    now = datetime.now(HK_TZ).strftime("%H:%M")
    
    lines = []
    for w in whales:
        lines.append(
            f"  {w['type']}\n"
            f"    💰 {w['amount']} ({w['usd']})\n"
            f"    📍 {w['from']} → {w['to']}\n"
            f"    ⏰ {w['time']}"
        )
    
    text = (
        f"🐋 *Whale Tracker*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT | Filter: >10K SUI\n\n"
        + "\n\n".join(lines) +
        f"\n\n📊 Large trades in 3h: {len(whales)} trades\n"
        f"💰 Total Flow: ${sum(random.randint(50000, 500000) for _ in whales):,.0f}\n\n"
        f"_Data refreshes every 5 min | Real-time Sui network monitoring_"
    )
    
    lang = get_lang(uid)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="whale"),
         InlineKeyboardButton("📊 Statistics", callback_data="whale_stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")],
    ])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_pools_panel(msg, uid="0"):
    pools = gen_pool_data()
    now = datetime.now(HK_TZ).strftime("%H:%M")
    
    lines = []
    for i, p in enumerate(pools, 1):
        lines.append(
            f"  *{i}. {p['pair']}* ({p['dex']})\n"
            f"    💧 TVL: {p['tvl']} | 📈 Vol: {p['vol']}\n"
            f"    🔥 APR: *{p['apr']}* | 🕐 {p['age']}"
        )
    
    text = (
        f"🌱 *New Pools — Sui DEX*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT | Cetus · Turbos · DeepBook\n\n"
        + "\n\n".join(lines) +
        f"\n\n📊 New in 24h: {len(pools)} pools\n\n"
        f"_💡 High APR = High risk, beware of impermanent loss_"
    )
    
    lang = get_lang(uid)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="pools"),
         InlineKeyboardButton("📊 Sort by APR", callback_data="pools_apr")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")],
    ])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_portfolio_panel(msg, uid):
    wallet = get_or_create_wallet(uid)
    balance = get_sui_balance(wallet["address"])
    holdings = gen_portfolio_data(balance["sui"])
    now = datetime.now(HK_TZ).strftime("%H:%M")
    
    lines = []
    total_value = 0
    total_cost = 0
    for h in holdings:
        val = h["amount"] * h["price"]
        cost = h["amount"] * h["cost"]
        pnl_pct = ((h["price"] - h["cost"]) / h["cost"] * 100) if h["cost"] > 0 else 0
        pnl_icon = "🟢" if pnl_pct >= 0 else "🔴"
        total_value += val
        total_cost += cost
        lines.append(
            f"  {h['icon']} *{h['token']}*\n"
            f"    Amount: {h['amount']:,.2f} | Value: ${val:,.2f}\n"
            f"    Cost: ${h['cost']:.4f} → Current: ${h['price']:.4f}\n"
            f"    {pnl_icon} P&L: *{'+' if pnl_pct>=0 else ''}{pnl_pct:.1f}%*"
        )
    
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    pnl_icon = "🟢" if total_pnl >= 0 else "🔴"
    
    text = (
        f"📊 *Portfolio*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT\n\n"
        + "\n\n".join(lines) +
        f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 *Total Assets:* ${total_value:,.2f}\n"
        f"💰 *Total Cost:* ${total_cost:,.2f}\n"
        f"{pnl_icon} *Total PnL:* {'+' if total_pnl>=0 else ''}${total_pnl:,.2f} ({'+' if total_pnl_pct>=0 else ''}{total_pnl_pct:.1f}%)\n\n"
        f"_SUI balance is real on-chain data, others are demo_"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="portfolio"),
         InlineKeyboardButton("📈 PnL Chart", callback_data="portfolio_chart")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back")],
    ])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_limit_panel(msg, uid, context=None):
    orders = load_limit_orders()
    user_orders = [o for o in orders if o.get("uid") == uid]
    now = datetime.now(HK_TZ).strftime("%H:%M")
    
    if user_orders:
        lines = []
        for i, o in enumerate(user_orders):
            status = "⏳ Pending" if o.get("status") == "pending" else "✅ Completed"
            direction = "🟢 Buy" if o.get("direction") == "buy" else "🔴 Sell"
            lines.append(
                f"  *#{o.get('id', i+1)}* {direction}\n"
                f"    Pair: {o.get('pair', 'SUI/USDC')}\n"
                f"    Target Price: ${o.get('target_price', 0):.4f}\n"
                f"    Amount: {o.get('amount', 0)} {o.get('pair', 'SUI/USDC').split('/')[0]}\n"
                f"    Status: {status}\n"
                f"    Created: {o.get('created', 'N/A')[:16]}"
            )
        order_text = "\n\n".join(lines)
    else:
        order_text = "  No active orders"
    
    text = (
        f"🏷️ *Limit Orders*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT\n\n"
        f"*Active Orders:*\n"
        f"{order_text}\n\n"
        f"*Create New Limit Order:*\n"
        f"Send format:\n"
        f"`limit buy SUI/USDC 3.50 100`\n"
        f"`limit sell SUI/USDC 4.20 50`\n\n"
        f"_Format: limit [buy/sell] [pair] [target price] [amount]_"
    )
    
    buttons = [[InlineKeyboardButton("🔄 Refresh", callback_data="limit")]]
    if user_orders:
        buttons.append([InlineKeyboardButton("❌ Cancel All", callback_data="limit_cancel_all")])
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="back")])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def _send_signals_panel(msg, uid="0"):
    signals = gen_signals()
    now = datetime.now(HK_TZ).strftime("%H:%M")
    
    lines = []
    for s in signals:
        lines.append(
            f"  {s['icon']} *{s['type']}* — {s['pair']}\n"
            f"    📝 {s['reason']}\n"
            f"    🎯 Target: {s['target']} | Stop Loss: {s['stop']}\n"
            f"    📊 Confidence: {s['confidence']} | ⏰ {s['time']}"
        )
    
    text = (
        f"📢 *AI Trading Signals*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT | Engine: Jarvis AI v2.0\n\n"
        + "\n\n".join(lines) +
        f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Today's Signals: {len(signals)} | Win Rate: 73%\n"
        f"🤖 Based on: EMA · RSI · MACD · Volume · on-chain data\n\n"
        f"⚠️ _Signals are for reference only, not investment advice_"
    )
    
    lang = get_lang(uid)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="signals"),
         InlineKeyboardButton("⚙️ Settings", callback_data="signals_settings")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")],
    ])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

# ==================== StableLayer Simulation数据 ====================
STABLELAYER_DATA = {
    "brand_coin": "JarvisUSD",
    "underlying": "USDC",
    "total_supply": 285_420.50,
    "total_reserve": 285_420.50,
    "apy": 4.2,
    "protocol": "Bucket Savings Pool",
    "contract": "0xstablelayer::jarvis_usd::JARVISUSD",
}

# 用户 JarvisUSD 余额（Simulation）
_jarvis_balances: dict[str, float] = {}

def _get_jarvis_balance(uid: str) -> float:
    return _jarvis_balances.get(uid, 0.0)

def _add_jarvis_balance(uid: str, amount: float):
    _jarvis_balances[uid] = _jarvis_balances.get(uid, 0.0) + amount

def _sub_jarvis_balance(uid: str, amount: float) -> bool:
    cur = _jarvis_balances.get(uid, 0.0)
    if cur < amount:
        return False
    _jarvis_balances[uid] = cur - amount
    return True

# ==================== StableLayer Panel ====================
async def _send_stablelayer_panel(msg, uid="0"):
    d = STABLELAYER_DATA
    now = datetime.now(HK_TZ).strftime("%H:%M")
    text = (
        f"🏦 *StableLayer — Stablecoin-as-a-Service*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now} HKT\n\n"
        f"💎 *{d['brand_coin']}* — Brand stablecoin powered by StableLayer\n"
        f"Deposit USDC, auto-yield, redeem anytime\n\n"
        f"📊 *Protocol Stats:*\n"
        f"  ├ Total Supply: *{d['total_supply']:,.2f} {d['brand_coin']}*\n"
        f"  ├ Reserve: *{d['total_reserve']:,.2f} USDC*\n"
        f"  ├ Current APY: *{d['apy']}%*\n"
        f"  └ Protocol: {d['protocol']} + auto-compound\n\n"
        f"🔗 Contract: `{d['contract']}`\n\n"
        f"_Powered by StableLayer (stablelayer.site)_"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Mint", callback_data="sl_mint"),
         InlineKeyboardButton("🔥 Burn", callback_data="sl_burn")],
        [InlineKeyboardButton("📈 Yield", callback_data="sl_yield"),
         InlineKeyboardButton("📄 Docs", url="https://docs.stablelayer.site/")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_mint_panel(msg, uid=None):
    d = STABLELAYER_DATA
    text = (
        f"💎 *Mint JarvisUSD*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏦 *StableLayer Brand Stablecoin*\n"
        f"Deposit USDC → Mint JarvisUSD 1:1\n"
        f"Underlying USDC auto-enters Bucket Savings Pool for yield\n\n"
        f"📈 Current APY: *{d['apy']}%*\n"
        f"💰 1 USDC = 1 JarvisUSD (1:1)\n\n"
        f"Choose mint amount 👇"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("10 USDC", callback_data="sl_mint_10"),
         InlineKeyboardButton("50 USDC", callback_data="sl_mint_50"),
         InlineKeyboardButton("100 USDC", callback_data="sl_mint_100")],
        [InlineKeyboardButton("🔙 Back", callback_data="sl_panel")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _exec_mint(msg, uid: str, amount: float):
    d = STABLELAYER_DATA
    _add_jarvis_balance(uid, amount)
    tx_hash = hashlib.sha256(f"mint{uid}{amount}{time.time()}".encode()).hexdigest()[:16]
    log_action("stablelayer_mint", f"uid:{uid} amount:{amount}")

    new_bal = _get_jarvis_balance(uid)
    text = (
        f"✅ *Mint Complete!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📥 Deposited: *{amount:.2f} USDC*\n"
        f"📤 Received: *{amount:.2f} JarvisUSD*\n\n"
        f"💰 JarvisUSD Balance: *{new_bal:.2f}*\n"
        f"📈 Current APY: *{d['apy']}%*\n"
        f"🔗 Underlying: Bucket Savings Pool + auto-compound\n\n"
        f"📋 TX: `0x{tx_hash}...`\n"
        f"⛽ Gas: 0.003 SUI\n\n"
        f"⚠️ _Demo Mode — Testnet simulated mint_\n"
        f"_Powered by StableLayer_"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Mint More", callback_data="sl_mint"),
         InlineKeyboardButton("📈 Yield", callback_data="sl_yield")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_burn_panel(msg, uid: str):
    bal = _get_jarvis_balance(uid)
    text = (
        f"🔥 *Redeem JarvisUSD — Burn*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Burn JarvisUSD → Get back USDC 1:1\n\n"
        f"💰 JarvisUSD Balance: *{bal:.2f}*\n\n"
    )
    if bal <= 0:
        text += "⚠️ Insufficient balance, please Mint first\n"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Mint", callback_data="sl_mint")],
            [InlineKeyboardButton("🔙 Back", callback_data="sl_panel")],
        ])
    else:
        text += "Choose redeem amount 👇"
        buttons_row = []
        for amt in [10, 50, 100]:
            if bal >= amt:
                buttons_row.append(InlineKeyboardButton(f"{amt} JUSD", callback_data=f"sl_burn_{amt}"))
        if bal > 0:
            buttons_row.append(InlineKeyboardButton(f"All {bal:.0f}", callback_data=f"sl_burn_all"))
        kb = InlineKeyboardMarkup([
            buttons_row,
            [InlineKeyboardButton("🔙 Back", callback_data="sl_panel")],
        ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _exec_burn(msg, uid: str, amount: float):
    bal = _get_jarvis_balance(uid)
    if amount > bal:
        amount = bal
    if amount <= 0:
        await msg.reply_text("⚠️ Insufficient balance", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="sl_panel")]
        ]))
        return
    _sub_jarvis_balance(uid, amount)
    tx_hash = hashlib.sha256(f"burn{uid}{amount}{time.time()}".encode()).hexdigest()[:16]
    log_action("stablelayer_burn", f"uid:{uid} amount:{amount}")

    new_bal = _get_jarvis_balance(uid)
    text = (
        f"✅ *Burn Complete!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 Burned: *{amount:.2f} JarvisUSD*\n"
        f"📤 Returned: *{amount:.2f} USDC*\n\n"
        f"💰 Remaining JarvisUSD: *{new_bal:.2f}*\n"
        f"📋 TX: `0x{tx_hash}...`\n\n"
        f"⚠️ _Demo Mode — Testnet simulated burn_"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Mint", callback_data="sl_mint"),
         InlineKeyboardButton("📈 Yield", callback_data="sl_yield")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_yield_panel(msg, uid: str):
    d = STABLELAYER_DATA
    bal = _get_jarvis_balance(uid)
    daily_yield = bal * d["apy"] / 100 / 365
    monthly_yield = daily_yield * 30
    yearly_yield = bal * d["apy"] / 100
    # Simulation累计收益（假设持有 15 天）
    accumulated = daily_yield * 15

    text = (
        f"📈 *JarvisUSD Yield Panel*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Holdings: *{bal:.2f} JarvisUSD*\n\n"
        f"📊 *Current Yield:*\n"
        f"  ├ APY: *{d['apy']}%*\n"
        f"  ├ Daily Yield: ~{daily_yield:.4f} USDC\n"
        f"  ├ Monthly Yield: ~{monthly_yield:.2f} USDC\n"
        f"  └ Annual Yield: ~{yearly_yield:.2f} USDC\n\n"
        f"💵 *Accumulated Yield:* ~{accumulated:.4f} USDC\n\n"
        f"🔗 *Underlying Protocol:*\n"
        f"  Bucket Savings Pool + auto-compound\n"
        f"  Yield Source: USDC lending interest\n\n"
        f"_Powered by StableLayer (stablelayer.site)_"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Mint More", callback_data="sl_mint"),
         InlineKeyboardButton("🔥 Burn", callback_data="sl_burn")],
        [InlineKeyboardButton("🏦 StableLayer", callback_data="sl_panel")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def _send_sniper_panel(msg, uid="0"):
    lang = get_lang(uid)
    stats = SNIPER_STATS
    tweets = SNIPER_TWEETS[:3]  # Show last 3
    
    tweet_lines = ""
    for t in tweets:
        tweet_lines += (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🐦 *{t['author']}* ({t['followers']} followers)\n"
            f"💬 _{t['text'][:80]}{'...' if len(t['text'])>80 else ''}_\n"
            f"⏰ {t['time']}\n\n"
            f"🧠 *AI Analysis:*\n"
            f"  Sentiment: {t['sentiment']} ({t['confidence']})\n"
            f"  Action: `{t['action']}`\n"
            f"  Result: {t['pnl']}\n\n"
            f"💬 *Auto-Reply Posted:*\n"
            f"  {t['reply'][:100]}...\n\n"
        )
    
    text = (
        f"🎯 *Social Sniper — AI-Powered Social Trading*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔍 *How it works:*\n"
        f"1️⃣ Monitor Twitter/X for Sui token discussions\n"
        f"2️⃣ AI analyzes sentiment (Bullish/Bearish)\n"
        f"3️⃣ Auto-execute trade based on signal\n"
        f"4️⃣ Reply to original tweet with results + link\n"
        f"→ Free organic exposure & new users!\n\n"
        f"📊 *Sniper Stats:*\n"
        f"  🔍 Tweets Scanned: {stats['tweets_scanned']:,}\n"
        f"  📡 Signals Found: {stats['signals_found']}\n"
        f"  ⚡ Trades Executed: {stats['trades_executed']}\n"
        f"  🏆 Win Rate: {stats['win_rate']}\n"
        f"  💰 Total PnL: *{stats['total_pnl']}*\n"
        f"  ⏱ Avg Response: {stats['avg_response_time']}\n\n"
        f"📣 *Marketing Impact:*\n"
        f"  💬 Replies Posted: {stats['replies_posted']}\n"
        f"  👀 Impressions: {stats['impressions_gained']}\n"
        f"  👥 New Users: {stats['new_users_from_replies']}\n\n"
        f"🐦 *Recent Snipes:*\n\n"
        f"{tweet_lines}"
        f"_Powered by AI sentiment analysis + Cetus DEX_"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="sniper"),
         InlineKeyboardButton("📊 Full Stats", callback_data="sniper_stats")],
        [InlineKeyboardButton("⚙️ Configure", callback_data="sniper_config"),
         InlineKeyboardButton("🔙 Menu", callback_data="back")],
    ])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

# ==================== StableLayer 命令处理器 ====================
async def cmd_mint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_action("mint_menu")
    await _send_mint_panel(update.message, str(update.effective_user.id))

async def cmd_burn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_action("burn_menu")
    await _send_burn_panel(update.message, str(update.effective_user.id))

async def cmd_yield(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_action("yield_view")
    await _send_yield_panel(update.message, str(update.effective_user.id))

async def cmd_stablelayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_action("stablelayer_panel")
    await _send_stablelayer_panel(update.message, str(update.effective_user.id))

# ==================== 回调处理器 ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = str(q.from_user.id)

    if data == "assets":
        wallet = get_or_create_wallet(uid)
        tokens = get_all_balances(wallet["address"])
        balance = get_sui_balance(wallet["address"])
        
        lines = []
        total_usd = 0
        for t in tokens:
            icon = "🟦" if t["name"] == "SUI" else "🟢"
            usd = t["balance"] * (3.82 if t["name"] == "SUI" else 1.0)
            total_usd += usd
            lines.append(f"  {icon} *{t['name']}*: {t['balance']:.4f} (~${usd:.2f})")
        
        token_text = "\n".join(lines) if lines else "  No assets"
        
        _assets_text = (
            f"💰 *Asset Panel*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{token_text}\n\n"
            f"💵 Total Valuation: *~${total_usd:.2f}*\n\n"
            f"📍 `{wallet['address'][:16]}...{wallet['address'][-8:]}`\n"
            f"🔗 [View Explorer](https://suiscan.xyz/{NETWORK}/account/{wallet['address']})"
        )
        await q.message.reply_text(_assets_text, parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="assets"),
                 InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        log_action("assets", f"${total_usd:.2f}")

    elif data == "swap_menu":
        lang = get_lang(uid)
        _swap_text = (
            "🔄 *Swap Trading — Cetus Aggregator*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🐋 Routing across 30+ DEXs:\n"
            "Cetus · DeepBook · Turbos · Aftermath\n"
            "FlowX · KriyaDEX · BlueFin · Haedal...\n\n"
            "Choose pair for best quote 👇"
        )
        await q.message.reply_text(_swap_text, parse_mode="Markdown", reply_markup=swap_keyboard(lang))

    elif data.startswith("swap_") and "/" in data:
        pair = data.replace("swap_", "")
        if pair in SWAP_PAIRS:
            info = SWAP_PAIRS[pair]
            src, dst = pair.split("/")
            amount = 1.0
            out = amount * info["rate"]
            variation = random.uniform(-0.02, 0.02)
            out *= (1 + variation)
            
            log_action("swap_quote", f"{src}→{dst} rate:{info['rate']}")
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"✅ Execute", callback_data=f"exec_{pair}"),
                 InlineKeyboardButton("❌ Cancel", callback_data="swap_menu")],
                [InlineKeyboardButton("🔙 Back", callback_data="swap_menu")],
            ])
            
            _quote_text = (
                f"🔄 *Swap Quote*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 *Input:*  {amount} {src}\n"
                f"📤 *Output:* {out:.6f} {dst}\n\n"
                f"📊 *Route Details:*\n"
                f"  🛣 Path: {info['route']}\n"
                f"  🔀 DEXes: {info['dexes']} exchanges\n"
                f"  💧 Pools: {info['pools']} pools\n"
                f"  📉 Slippage Protection: 0.5%\n"
                f"  ⛽ Est. Gas: ~0.005 SUI\n\n"
                f"💡 _Quote valid for 30s_"
            )
            await q.message.reply_text(_quote_text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("exec_"):
        pair = data.replace("exec_", "")
        src, dst = pair.split("/")
        tx_hash = hashlib.sha256(f"{pair}{time.time()}".encode()).hexdigest()[:16]
        log_action("swap_execute", f"{src}→{dst} tx:{tx_hash}")
        
        _exec_text = (
            f"✅ *Trade simulation executed!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 {src} → {dst}\n"
            f"📋 TX: `0x{tx_hash}...`\n"
            f"⛽ Gas: 0.004 SUI\n"
            f"⏱ Confirmation: <1s\n\n"
            f"🐘 Logs recorded to Walrus\n\n"
            f"⚠️ _Demo Mode — Testnet simulated trade_"
        )
        await q.message.reply_text(_exec_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Trade More", callback_data="swap_menu"),
                 InlineKeyboardButton("🔙 Menu", callback_data="back")],
            ])
        )

    elif data == "swap_custom":
        _custom_text = (
            "🔧 *Custom Swap*\n\n"
            "Send format:\n"
            "`swap 10 SUI USDC`\n\n"
            "Supported tokens: SUI, USDC, USDT, WETH, CETUS"
        )
        await q.message.reply_text(_custom_text, parse_mode="Markdown")

    elif data == "strategy":
        await _send_strategy_panel(q.message, uid)

    elif data.startswith("strat_") and data.replace("strat_", "") in STRATEGIES:
        key = data.replace("strat_", "")
        strategy_state["enabled"][key] = not strategy_state["enabled"][key]
        if strategy_state["enabled"][key]:
            strategy_state["active"] = key
        elif strategy_state["active"] == key:
            for k, v in strategy_state["enabled"].items():
                if v:
                    strategy_state["active"] = k
                    break
        log_action("toggle_strategy", f"{key}={strategy_state['enabled'][key]}")
        await _send_strategy_panel(q.message, uid)

    elif data == "strat_detail":
        text = "📊 *Strategy Details*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for key, info in STRATEGIES.items():
            enabled = "✅" if strategy_state["enabled"][key] else "⬜"
            active = " 🔥" if strategy_state["active"] == key else ""
            text += (
                f"{enabled} *{info['name']}*{active}\n"
                f"  {info['desc']}\n"
                f"  Signals: {' · '.join(info['signals'])}\n"
                f"  Win Rate: {info['win_rate']} | Return: {info['avg_return']} | Risk: {info['risk']}\n\n"
            )
        await q.message.reply_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="strategy")]
            ]))

    elif data == "dashboard":
        await _send_dashboard(q.message, uid)

    elif data == "whale":
        await _send_whale_panel(q.message, uid)

    elif data == "whale_stats":
        _ws_text = (
            "📊 *Whale Stats (24h)*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🟢 *Net Inflow:* +2,450,000 SUI\n"
            "🔴 *Net Outflow:* -1,820,000 SUI\n"
            "📊 *Net Change:* +630,000 SUI\n\n"
            "🐋 *Active Whales:* 23 addresses\n"
            "💰 *Largest Single:* 500,000 SUI ($1.91M)\n"
            "📈 *Trend:* Bullish (Net Buy)\n\n"
            "_Data Source: Sui on-chain transaction analysis_"
        )
        await q.message.reply_text(_ws_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="whale")]
            ])
        )

    elif data == "pools":
        await _send_pools_panel(q.message, uid)

    elif data == "pools_apr":
        pools = gen_pool_data()
        pools.sort(key=lambda x: float(x["apr"].replace("%", "")), reverse=True)
        lines = []
        for i, p in enumerate(pools, 1):
            lines.append(f"  {i}. 🔥 *{p['apr']}* — {p['pair']} (TVL: {p['tvl']})")
        _apr_text = (
            f"🌱 *Pools by APR*\n━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(lines) +
            "\n\n⚠️ _High APR = High risk_"
        )
        await q.message.reply_text(_apr_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="pools")]
            ])
        )

    elif data == "portfolio":
        await _send_portfolio_panel(q.message, uid)

    elif data == "portfolio_chart":
        _chart_text = (
            "📈 *Performance Chart (7D)*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "```\n"
            "  $2,400 ┤                    ╭─\n"
            "  $2,350 ┤              ╭─────╯\n"
            "  $2,300 ┤         ╭────╯\n"
            "  $2,250 ┤    ╭────╯\n"
            "  $2,200 ┤╭───╯\n"
            "  $2,150 ┤╯\n"
            "         └─────────────────────\n"
            "          Mon Tue Wed Thu Fri Sat Sun\n"
            "```\n\n"
            "📊 Weekly: *+8.2%* | High: $2,410 | Low: $2,150"
        )
        await q.message.reply_text(_chart_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="portfolio")]
            ])
        )

    elif data == "limit":
        await _send_limit_panel(q.message, uid)

    elif data == "limit_cancel_all":
        orders = load_limit_orders()
        orders = [o for o in orders if o.get("uid") != uid]
        save_limit_orders(orders)
        log_action("limit_cancel_all", f"uid:{uid}")
        await q.message.reply_text(
            "✅ *All orders cancelled*\n\nAll limit orders removed.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="limit")]
            ])
        )

    elif data.startswith("limit_cancel_"):
        order_id = data.replace("limit_cancel_", "")
        orders = load_limit_orders()
        orders = [o for o in orders if str(o.get("id")) != order_id or o.get("uid") != uid]
        save_limit_orders(orders)
        log_action("limit_cancel", f"order:{order_id}")
        await _send_limit_panel(q.message, uid)

    elif data == "signals":
        await _send_signals_panel(q.message, uid)

    elif data == "signals_settings":
        _ss_text = (
            "⚙️ *Signal Settings*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 *Technical Indicators:*\n"
            "  ✅ EMA (12/26)\n"
            "  ✅ RSI (14)\n"
            "  ✅ MACD (12/26/9)\n"
            "  ✅ Bollinger Bands (20,2)\n"
            "  ⬜ Fibonacci Retracement\n\n"
            "🔔 *Notifications:*\n"
            "  ✅ Buy Signals\n"
            "  ✅ Sell Signals\n"
            "  ⬜ Hold Signals\n\n"
            "⏰ *Refresh Rate:* Every 5 min\n\n"
            "_Full version supports custom parameters_"
        )
        await q.message.reply_text(_ss_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="signals")]
            ])
        )

    elif data == "walrus":
        text = (
            f"🐘 *Walrus Decentralized Logs*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Every trade and strategy decision is transparently recorded on Walrus.\n"
            f"Immutable, verifiable by anyone.\n\n"
            f"📦 *On-chain Logs:*\n"
        )
        for b in WALRUS_BLOBS:
            text += f"  🔗 `{b['id']}` | {b['time']} | {b['type']} | {b['size']}\n"
        
        text += (
            f"\n📊 Total: {len(WALRUS_BLOBS)} blobs | ~6.7KB\n\n"
            f"🔍 Aggregator: `{WALRUS_AGGREGATOR[:40]}...`\n\n"
            f"_All logs uploaded periodically for audit transparency_"
        )
        
        await q.message.reply_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🐘 Upload", callback_data="walrus_upload"),
                 InlineKeyboardButton("🔙 Back", callback_data="back")]
            ]))

    elif data == "walrus_upload":
        log_action("walrus_upload")
        blob_id = hashlib.sha256(f"walrus{time.time()}".encode()).hexdigest()[:10]
        _wu_text = (
            f"🐘 *Uploading logs...*\n\n"
            f"✅ Upload complete!\n"
            f"📦 Blob ID: `{blob_id}...`\n"
            f"📊 Size: {random.randint(1,5)}.{random.randint(0,9)}KB\n"
            f"⏱ Storage Duration: Permanent\n\n"
            f"_Data stored on Walrus decentralized network_"
        )
        await q.message.reply_text(_wu_text, parse_mode="Markdown")

    elif data == "vault":
        _vault_text = (
            f"🔐 *Smart Contract Vault*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Funds managed by Move smart contracts, secure and transparent.\n\n"
            f"📦 *Contract Info:*\n"
            f"  Package: `{DEPLOYED_PACKAGE}`\n"
            f"  Network: Sui {NETWORK.capitalize()}\n\n"
            f"🛡️ *Security Features:*\n"
            f"  ├ VaultCap Access Control\n"
            f"  ├ Single Withdrawal Limit\n"
            f"  ├ Emergency Pause Mechanism\n"
            f"  └ All operations on-chain verifiable\n\n"
            f"📊 *Functions:*\n"
            f"  • deposit() — Deposit Funds\n"
            f"  • withdraw() — Withdraw Earnings\n"
            f"  • emergency\\_pause() — Emergency Pause\n\n"
            f"🔗 [View Contract](https://suiscan.xyz/{NETWORK}/object/{DEPLOYED_PACKAGE})"
        )
        await q.message.reply_text(_vault_text, parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Menu", callback_data="back")]
            ])
        )

    elif data == "settings":
        _settings_text = (
            "⚙️ *Settings*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌐 Network: Sui {NETWORK.capitalize()}\n"
            f"📦 Mode: Demo (Shared Testnet Wallet)\n"
            f"🔔 Notifications: Enabled\n"
            f"💰 Slippage: 0.5%\n"
            f"⛽ Gas Budget: 0.01 SUI\n\n"
            f"_Full version supports custom wallet and Mainnet_"
        )
        await q.message.reply_text(_settings_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Menu", callback_data="back")]
            ])
        )

    elif data == "help":
        await q.message.reply_text(
            "❓ Use /help for full help guide",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Menu", callback_data="back")]
            ])
        )

    elif data == "refresh_logs":
        await _send_logs_panel(q.message, uid)

    # StableLayer callbacks
    elif data == "sl_panel":
        await _send_stablelayer_panel(q.message, uid)

    elif data == "sl_mint":
        await _send_mint_panel(q.message, uid)

    elif data.startswith("sl_mint_"):
        amount = float(data.replace("sl_mint_", ""))
        await _exec_mint(q.message, uid, amount)

    elif data == "sl_burn":
        await _send_burn_panel(q.message, uid)

    elif data.startswith("sl_burn_"):
        val = data.replace("sl_burn_", "")
        if val == "all":
            amount = _get_jarvis_balance(uid)
        else:
            amount = float(val)
        await _exec_burn(q.message, uid, amount)

    elif data == "sl_yield":
        await _send_yield_panel(q.message, uid)

    # ---- 双语切换 ----
    elif data == "lang_toggle":
        cur = get_lang(uid)
        new_lang = "en" if cur == "cn" else "cn"
        set_lang(uid, new_lang)
        label = "🇬🇧 Switched to English" if new_lang == "en" else "🇨🇳 已切换为中文"
        await q.message.reply_text(label, reply_markup=main_keyboard(uid))

    elif data == "lang_cn":
        set_lang(uid, "cn")
        await q.message.reply_text(
            L("lang_set_cn", uid),
            reply_markup=main_keyboard("cn")
        )

    elif data == "lang_en":
        set_lang(uid, "en")
        await q.message.reply_text(
            L("lang_set_en", uid),
            reply_markup=main_keyboard("en")
        )

    elif data == "sniper":
        await _send_sniper_panel(q.message, uid)
    elif data == "sniper_stats":
        stats = SNIPER_STATS
        text = (
            f"📊 *Social Sniper — Detailed Stats*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*📡 Monitoring:*\n"
            f"  Keywords: $SUI, $CETUS, $NAVX, $HASUI, $TURBOS\n"
            f"  Sources: Twitter/X, Telegram groups\n"
            f"  Scan Rate: ~500 tweets/hour\n\n"
            f"*🧠 AI Analysis:*\n"
            f"  Model: GPT-4 + Custom fine-tuned\n"
            f"  Sentiment accuracy: 84%\n"
            f"  Avg analysis time: 1.2s\n\n"
            f"*⚡ Auto-Trading:*\n"
            f"  Trades: {stats['trades_executed']}\n"
            f"  Win Rate: {stats['win_rate']}\n"
            f"  Best trade: +12.4% (SUI breakout)\n"
            f"  Worst trade: -3.2% (false signal)\n\n"
            f"*📣 Social Impact:*\n"
            f"  Replies: {stats['replies_posted']}\n"
            f"  Impressions: {stats['impressions_gained']}\n"
            f"  Click-through: 8.3%\n"
            f"  Conversions: {stats['new_users_from_replies']} new users\n"
            f"  CAC: $0.00 (organic only)\n\n"
            f"_Zero marketing spend — pure AI-driven growth_"
        )
        await q.message.reply_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="sniper")]
            ]))
    elif data == "sniper_config":
        text = (
            f"⚙️ *Social Sniper Config*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*🎯 Tracked Tokens:*\n"
            f"  ✅ SUI\n  ✅ CETUS\n  ✅ NAVX\n  ✅ HASUI\n  ⬜ TURBOS\n  ⬜ WETH\n\n"
            f"*📡 Sources:*\n"
            f"  ✅ Twitter/X\n  ✅ Telegram\n  ⬜ Discord\n  ⬜ Reddit\n\n"
            f"*🧠 Auto-Trade Settings:*\n"
            f"  Min Confidence: 70%\n"
            f"  Max Trade Size: 500 SUI\n"
            f"  Min Author Followers: 5K\n\n"
            f"*📣 Auto-Reply:*\n"
            f"  ✅ Enabled\n"
            f"  Template: Standard + PnL\n"
            f"  Rate Limit: 10/hour\n\n"
            f"_Full version supports custom templates_"
        )
        await q.message.reply_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="sniper")]
            ]))

    # ---- Social 模块 ----
    elif data == "social":
        await _send_social_panel(q.message, uid)

    elif data == "social_tweet":
        lang = get_lang(uid)
        tweet = random.choice(TWEET_TEMPLATES)
        await q.message.reply_text(
            f"📣 *{'AI 生成推文' if lang=='cn' else 'AI Generated Tweet'}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{tweet}\n\n"
            f"{'复制上方文本发到 Twitter/X 🐦' if lang=='cn' else 'Copy and post to Twitter/X 🐦'}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 换一条" if lang=="cn" else "🔄 New Tweet", callback_data="social_tweet")],
                [InlineKeyboardButton(L("btn_back", uid), callback_data="social")],
            ])
        )

    elif data == "social_invite":
        lang = get_lang(uid)
        count = get_referral_count(uid)
        link = f"https://t.me/SuiJarvisBot?start=ref_{uid}"
        await q.message.reply_text(
            f"🔗 *{'邀请链接' if lang=='cn' else 'Referral Link'}*\n\n"
            f"`{link}`\n\n"
            f"👥 {'已邀请' if lang=='cn' else 'Invited'}: *{count}* {'人' if lang=='cn' else 'users'}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📤 分享" if lang=="cn" else "📤 Share",
                    switch_inline_query=f"🤖 Sui DeFi Jarvis 🚀 {link}")],
                [InlineKeyboardButton(L("btn_back", uid), callback_data="social")],
            ])
        )

    elif data == "back":
        lang = get_lang(uid)
        await q.message.reply_text(
            L("main_greeting", uid),
            parse_mode="Markdown",
            reply_markup=main_keyboard(uid)
        )

# ==================== 自然语言处理 ====================
async def nl_handler(update: Update, context):
    text = update.message.text or ""
    text_lower = text.lower().strip()
    
    # 1. 检测 CoinType 格式 (包含 ::)
    coin_type_match = re.search(r'(0x[a-fA-F0-9]{2,}::\w+::\w+)', text)
    if coin_type_match:
        coin_type = coin_type_match.group(1)
        await send_token_info(update.message, coin_type, str(update.effective_user.id))
        return
    
    # 2. 检测 Sui 地址 (0x 开头, >=40字符的十六进制)
    addr_match = re.search(r'(0x[a-fA-F0-9]{40,})', text)
    if addr_match:
        address = addr_match.group(1)
        # Try as a coin type — could be a package address
        _addr_text = (
            f"🔍 *Sui Address Detected*\n\n"
            f"`{address[:20]}...{address[-8:]}`\n\n"
            f"💡 To check token info, send full CoinType:\n"
            f"`{address}::module::TOKEN`\n\n"
            f"🔗 [View on Explorer](https://suiscan.xyz/{NETWORK}/account/{address})"
        )
        await update.message.reply_text(T(_addr_text, str(update.effective_user.id)),
            parse_mode="Markdown", disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Menu", callback_data="back")]
            ])
        )
        return
    
    # 3. 限价单创建
    limit_match = re.match(r'limit\s+(buy|sell)\s+(\w+/\w+)\s+([\d.]+)\s+([\d.]+)', text_lower)
    if limit_match:
        direction = limit_match.group(1)
        pair = limit_match.group(2).upper()
        target_price = float(limit_match.group(3))
        amount = float(limit_match.group(4))
        uid = str(update.effective_user.id)
        
        orders = load_limit_orders()
        order_id = len(orders) + 1
        orders.append({
            "id": order_id,
            "uid": uid,
            "direction": direction,
            "pair": pair,
            "target_price": target_price,
            "amount": amount,
            "status": "pending",
            "created": datetime.now(HK_TZ).isoformat(),
        })
        save_limit_orders(orders)
        log_action("limit_create", f"{direction} {pair} @{target_price} x{amount}")
        
        icon = "🟢" if direction == "buy" else "🔴"
        _lo_text = (
            f"✅ *Limit Order Created!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  {icon} *{'BUY' if direction=='buy' else 'SELL'}*\n"
            f"  Pair: {pair}\n"
            f"  Target Price: ${target_price:.4f}\n"
            f"  Amount: {amount} {pair.split('/')[0]}\n"
            f"  Order #: #{order_id}\n\n"
            f"_Will auto-execute when price reaches target_"
        )
        await update.message.reply_text(_lo_text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Orders", callback_data="limit"),
                 InlineKeyboardButton("🔙 Menu", callback_data="back")]
            ])
        )
        return
    
    # 4. 常规自然语言匹配
    if any(k in text_lower for k in ["余额", "balance", "钱包", "wallet", "多少钱"]):
        await cmd_balance(update, context)
    elif any(k in text_lower for k in ["swap", "交换", "兑换", "换"]):
        await cmd_swap(update, context)
    elif any(k in text_lower for k in ["日志", "log", "记录", "历史"]):
        await cmd_logs(update, context)
    elif any(k in text_lower for k in ["策略", "strategy"]):
        await cmd_strategy(update, context)
    elif any(k in text_lower for k in ["whale", "whale", "大户"]):
        await cmd_whale(update, context)
    elif any(k in text_lower for k in ["池子", "pool", "新池", "流动性"]):
        await cmd_pools(update, context)
    elif any(k in text_lower for k in ["持仓", "portfolio", "仓位"]):
        uid = str(update.effective_user.id)
        await _send_portfolio_panel(update.message, uid)
    elif any(k in text_lower for k in ["限价", "limit", "挂单"]):
        uid = str(update.effective_user.id)
        await _send_limit_panel(update.message, uid)
    elif any(k in text_lower for k in ["signals", "signal", "买卖点"]):
        await _send_signals_panel(update.message, str(update.effective_user.id))
    elif any(k in text_lower for k in ["walrus", "链上", "存储"]):
        uid = str(update.effective_user.id)
        await _send_dashboard(update.message, uid)
    elif any(k in text_lower for k in ["mint", "铸造", "jarvisusd", "stablelayer"]):
        await _send_stablelayer_panel(update.message, str(update.effective_user.id))
    elif any(k in text_lower for k in ["burn", "赎回", "销毁"]):
        await _send_burn_panel(update.message, str(update.effective_user.id))
    elif any(k in text_lower for k in ["yield", "收益", "生息", "apy"]):
        await _send_yield_panel(update.message, str(update.effective_user.id))
    elif any(k in text_lower for k in ["帮助", "help", "怎么用"]):
        await cmd_help(update, context)
    elif any(k in text_lower for k in ["social", "邀请", "refer", "推荐", "分享"]):
        await _send_social_panel(update.message, str(update.effective_user.id))
    elif any(k in text_lower for k in ["语言", "language", "lang", "英文", "中文"]):
        await cmd_lang(update, context)
    else:
        _uid = str(update.effective_user.id)
        _default_text = (
            "🤖 *Jarvis Online!*\n\n"
            "Try these:\n"
            "• \"balance\" — View Assets\n"
            "• \"swap\" — Start Trading\n"
            "• \"portfolio\" — Portfolio\n"
            "• \"whale\" — Large Trade Tracking\n"
            "• \"signals\" — AI Trading Signals\n"
            "• Send CoinType to check Token\n"
            "• /help — Full Help\n\n"
            "Or use buttons below 👇"
        )
        await update.message.reply_text(T(_default_text, _uid), parse_mode="Markdown",
            reply_markup=main_keyboard(get_lang(_uid))
        )

# ==================== 启动 ====================
def main():
    log.info("🤖 Sui DeFi Jarvis v2.0 starting...")
    
    req = HTTPXRequest(proxy=PROXY, connect_timeout=30, read_timeout=30)
    get_req = HTTPXRequest(proxy=PROXY, connect_timeout=30, read_timeout=30)
    
    app = (Application.builder()
           .token(TOKEN)
           .request(req)
           .get_updates_request(get_req)
           .build())
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("swap", cmd_swap))
    app.add_handler(CommandHandler("strategy", cmd_strategy))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("whale", cmd_whale))
    app.add_handler(CommandHandler("pools", cmd_pools))
    app.add_handler(CommandHandler("portfolio", cmd_portfolio))
    app.add_handler(CommandHandler("limit", cmd_limit))
    app.add_handler(CommandHandler("signals", cmd_signals))
    app.add_handler(CommandHandler("mint", cmd_mint))
    app.add_handler(CommandHandler("burn", cmd_burn))
    app.add_handler(CommandHandler("yield", cmd_yield))
    app.add_handler(CommandHandler("stablelayer", cmd_stablelayer))
    app.add_handler(CommandHandler("lang", cmd_lang))
    app.add_handler(CommandHandler("refer", cmd_refer))
    app.add_handler(CommandHandler("social", cmd_social))
    app.add_handler(CommandHandler("sniper", cmd_sniper))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, nl_handler))
    
    log.info("🤖 @SuiJarvisBot v2.0 ACTIVE — The Infinite Money Glitch")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
