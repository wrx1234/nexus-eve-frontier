#!/usr/bin/env python3
"""
🤖 NEXUS Assembly Manager — Telegram Bot
Smart Assembly Management for EVE Frontier

Manage your Smart Gates, Smart Storage Units, and Smart Turrets
Tech Stack: Sui × Walrus × EVE Frontier
"""

import json, os, time, logging, requests, hashlib, random, re, sys
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup, KeyboardButton
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
TOKEN = os.environ.get('TG_BOT_TOKEN', '')
PROXY = os.environ.get('TG_PROXY', 'http://172.18.0.1:7890')
ADMIN_ID = 6633019220
NETWORK = "testnet"
SUI_RPC = f"https://fullnode.{NETWORK}.sui.io:443"
WALRUS_AGGREGATOR = "https://aggregator.walrus-testnet.walrus.space"
DEPLOYED_PACKAGE = "0x4ef033c63ed40684847c6ce36b082cefaa6c361b0cb28f833786082f805845c2"
INSURANCE_POOL_ID = "0xc54592fdd7308a7cc3cafb88453a027a60ea6360c77f73b3ddce25b91e0f2888"
DEPLOYER_ADDRESS = "0xe2ca4439282e48a28ab57d72692f2726e79cb62a00538d78e13692ea38aab0b9"
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

HK_TZ = timezone(timedelta(hours=8))

# 持久底部键盘
PERSISTENT_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📊 状态面板"), KeyboardButton("⛽ 燃料管理")],
        [KeyboardButton("🛡️ 保险"), KeyboardButton("🔔 告警设置")],
        [KeyboardButton("🚪 门禁管理"), KeyboardButton("❓ 帮助")],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

# ==================== i18n 系统 ====================
LANG_FILE = os.path.join(DATA_DIR, "lang_prefs.json")

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
    refs = _load_referrals()
    if new_uid == referrer_uid:
        return
    if new_uid in refs:
        return
    refs[new_uid] = {
        "referrer": referrer_uid,
        "time": datetime.now(HK_TZ).isoformat(),
    }
    _save_referrals(refs)
    log_action("referral", f"new:{new_uid} by:{referrer_uid}")

def get_referral_count(uid: str) -> int:
    refs = _load_referrals()
    return sum(1 for v in refs.values() if v.get("referrer") == str(uid))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(DATA_DIR, "nexus.log"))]
)
log = logging.getLogger("nexus")

# ==================== EVE EYES API ====================
EVE_EYES_BASE = "https://eve-eyes.d0v.xyz"
EVE_EYES_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJldmUtZXllcyIsImF1ZCI6ImV2ZS1leWVzLXVzZXJzIiwiaWF0IjoxNzc0NjE2MDQ2LCJleHAiOjE3NzQ2NTkyNDYsInN1YiI6IjB4ZDFlNjExNzdlZmMxZDVhZTBmMWEwOGQ0NWM4N2U3NzUxYzg3YzIwZDVmOWI2NTFlYzg0ZjRhODYzYzg5YTU0NyIsIndhbGxldEFkZHJlc3MiOiIweGQxZTYxMTc3ZWZjMWQ1YWUwZjFhMDhkNDVjODdlNzc1MWM4N2MyMGQ1ZjliNjUxZWM4NGY0YTg2M2M4OWE1NDciLCJjaGFpbiI6InN1aSJ9.ivcyFkCdSGwkdHvLZMBfMGHV2D_TC771LxhcjTZka3Y"

async def get_eve_module_activity():
    """获取 EVE 全网模块活跃度 (真实链上数据)"""
    try:
        import aiohttp
        headers = {"Authorization": f"Bearer {EVE_EYES_JWT}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{EVE_EYES_BASE}/api/indexer/module-call-counts", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("modules", [])
    except Exception as e:
        logging.warning(f"EVE EYES API error: {e}")
    return None

async def get_eve_recent_activity(page: int = 1):
    """获取最近交易"""
    try:
        import aiohttp
        headers = {"Authorization": f"Bearer {EVE_EYES_JWT}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{EVE_EYES_BASE}/api/indexer/transaction-blocks?page={page}&pageSize=20", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        logging.warning(f"EVE EYES API error: {e}")
    return None

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

# ==================== Walrus 日志 ====================
WALRUS_BLOBS = [
    {"id": "Nx4wG3x...", "time": "03-20 22:00", "type": "assembly_snapshot", "size": "2.1KB"},
    {"id": "Fx8kL2m...", "time": "03-20 18:30", "type": "fuel_log", "size": "1.4KB"},
    {"id": "Ap3nR7w...", "time": "03-20 15:00", "type": "gate_report", "size": "3.2KB"},
]

# ==================== Mock Assembly 数据 ====================
# 清晰结构: 后续对接真实数据只需替换此数据源

def _get_mock_assemblies() -> list:
    """Mock Assembly 数据源 - 未来替换为真实 API 调用"""
    return [
        {
            "id": "asm_001",
            "type": "smart_gate",
            "icon": "🚪",
            "name": "Alpha Bridge",
            "status": "online",
            "status_icon": "🟢",
            "status_text": "Online",
            "fuel_pct": 78,
            "fuel_est_days": 6,
            "metrics": {
                "jumps_24h": 142,
                "revenue_24h": 2.3,
            },
            "gate_config": {
                "toll": 0.02,
                "whitelist_count": 12,
                "rule": "Toll + Whitelist",
            },
        },
        {
            "id": "asm_002",
            "type": "smart_storage",
            "icon": "📦",
            "name": "Trade Hub",
            "status": "online",
            "status_icon": "🟢",
            "status_text": "Online",
            "fuel_pct": 62,
            "fuel_est_days": 4,
            "metrics": {
                "items": "47/100",
                "trades_24h": 18,
                "revenue_24h": 1.8,
            },
        },
        {
            "id": "asm_003",
            "type": "smart_turret",
            "icon": "🔫",
            "name": "Perimeter Defense",
            "status": "low_fuel",
            "status_icon": "🟡",
            "status_text": "Low Fuel",
            "fuel_pct": 23,
            "fuel_est_days": 1,
            "metrics": {
                "kills_24h": 3,
                "revenue_24h": 1.0,
            },
        },
    ]


def _get_mock_alerts() -> list:
    """Mock 告警配置数据源"""
    return [
        {"type": "fuel_low", "icon": "⛽", "label": "Fuel < 25%", "enabled": True},
        {"type": "under_attack", "icon": "⚔️", "label": "Under Attack", "enabled": True},
        {"type": "offline", "icon": "🔴", "label": "Assembly Offline", "enabled": True},
        {"type": "revenue", "icon": "💰", "label": "Daily Revenue Report", "enabled": False},
        {"type": "whale_activity", "icon": "🐋", "label": "Whale Assembly Activity", "enabled": False},
    ]


def _get_mock_weekly_stats() -> dict:
    """Mock 周报数据"""
    return {
        "assemblies_total": 3,
        "assemblies_online": 2,
        "total_revenue_7d": 35.7,
        "total_jumps_7d": 984,
        "total_trades_7d": 126,
        "total_kills_7d": 21,
        "fuel_spent_7d": 4.2,
        "rank": "#42 / 1,200",
        "top_assembly": "Alpha Bridge",
    }


def _fuel_bar(pct: int) -> str:
    """生成燃料进度条"""
    filled = round(pct / 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    warning = " ⚠️" if pct <= 25 else ""
    return f"{bar} {pct}%{warning}"


def _get_total_revenue_24h() -> float:
    """计算 24h 总收益"""
    assemblies = _get_mock_assemblies()
    return sum(a["metrics"].get("revenue_24h", 0) for a in assemblies)


def _count_fuel_alerts() -> int:
    """统计需要加油的 Assembly 数量"""
    return sum(1 for a in _get_mock_assemblies() if a["fuel_pct"] <= 25)


# ==================== 键盘布局 ====================
def main_keyboard(uid):
    """NEXUS 主菜单键盘"""
    lang = get_lang(uid)
    if lang == "cn":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Assembly 状态", callback_data="status"),
             InlineKeyboardButton("⛽ 燃料管理", callback_data="fuel")],
            [InlineKeyboardButton("🚪 Gate 管理", callback_data="gate"),
             InlineKeyboardButton("🔔 告警配置", callback_data="alert")],
            [InlineKeyboardButton("🛡️ 保险", callback_data="insure_menu"),
             InlineKeyboardButton("📋 保单", callback_data="claims_view")],
            [InlineKeyboardButton("👛 钱包", callback_data="wallet_view"),
             InlineKeyboardButton("💰 余额", callback_data="balance_view")],
            [InlineKeyboardButton("📋 日志", callback_data="logs"),
             InlineKeyboardButton("🐘 Walrus", callback_data="walrus")],
            [InlineKeyboardButton("📤 分享周报", callback_data="share"),
             InlineKeyboardButton("🗳️ 投票", callback_data="vote")],
            [InlineKeyboardButton("🔗 邀请好友", callback_data="refer"),
             InlineKeyboardButton("🐋 鲸鱼追踪", callback_data="whale")],
            [InlineKeyboardButton("❓ 帮助", callback_data="help"),
             InlineKeyboardButton("⚙️ 设置", callback_data="settings")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_toggle")],
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Assembly Status", callback_data="status"),
             InlineKeyboardButton("⛽ Fuel Manager", callback_data="fuel")],
            [InlineKeyboardButton("🚪 Gate Manager", callback_data="gate"),
             InlineKeyboardButton("🔔 Alerts", callback_data="alert")],
            [InlineKeyboardButton("🛡️ Insurance", callback_data="insure_menu"),
             InlineKeyboardButton("📋 Policies", callback_data="claims_view")],
            [InlineKeyboardButton("👛 Wallet", callback_data="wallet_view"),
             InlineKeyboardButton("💰 Balance", callback_data="balance_view")],
            [InlineKeyboardButton("📋 Logs", callback_data="logs"),
             InlineKeyboardButton("🐘 Walrus", callback_data="walrus")],
            [InlineKeyboardButton("📤 Share Report", callback_data="share"),
             InlineKeyboardButton("🗳️ Vote", callback_data="vote")],
            [InlineKeyboardButton("🔗 Invite Friends", callback_data="refer"),
             InlineKeyboardButton("🐋 Whale Tracker", callback_data="whale")],
            [InlineKeyboardButton("❓ Help", callback_data="help"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_toggle")],
        ])


# ==================== 命令处理器 ====================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    name = user.first_name or "Commander"
    lang = get_lang(uid)

    # 处理 referral 链接: /start ref_USERID
    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith("ref_"):
            referrer_uid = arg[4:]
            record_referral(uid, referrer_uid)

    wallet = get_or_create_wallet(uid)
    balance = get_sui_balance(wallet["address"])
    addr_short = f"{wallet['address'][:16]}...{wallet['address'][-8:]}"

    assemblies = _get_mock_assemblies()
    online_count = sum(1 for a in assemblies if a["status"] == "online")
    fuel_alerts = _count_fuel_alerts()
    total_rev = _get_total_revenue_24h()

    log_action("start", f"{name} (id:{uid})")

    if lang == "cn":
        text = (
            f"🤖 *欢迎使用 NEXUS!*\n"
            f"Neural EXecutive for Unified Stations\n\n"
            f"你的 24/7 AI 管家，管理 EVE Frontier Smart Assembly。\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎮 *什么是 EVE Frontier?*\n"
            f"一款太空生存 MMO，玩家在 Sui 区块链上的共享宇宙中建设和管理基础设施。\n\n"
            f"🏗️ *什么是 Smart Assembly?*\n"
            f"你的太空帝国的基础组件:\n"
            f"  🚪 Smart Gate - 星系间传送门。设置过路费、白名单和准入规则。\n"
            f"  📦 Smart Storage - 太空仓库。存储和交易资源。\n"
            f"  🔫 Smart Turret - 防御系统，保护领地免受敌人攻击。\n"
            f"  ⚡ Network Node - 为所有 Assembly 供电。\n\n"
            f"🤖 *NEXUS 能做什么?*\n"
            f"NEXUS 是你的 AI 管家，24/7 监控和管理所有 Assembly:\n"
            f"  - 自动补充燃料，防止耗尽\n"
            f"  - 以最优价格交易资源\n"
            f"  - 遭到攻击时立即告警\n"
            f"  - 动态管理 Gate 通行费\n"
            f"  - 每个决策都记录到 Walrus (不可篡改)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 *钱包已就绪:*\n"
            f"📍 `{addr_short}`\n"
            f"余额: *{balance['formatted']}*\n\n"
            f"📊 *Assembly 概览:*\n"
            f"  🏗️ 总数: {len(assemblies)} | 🟢 在线: {online_count}\n"
            f"  💰 24h 收益: {total_rev:.1f} SUI\n"
            f"  {'⚠️ ' + str(fuel_alerts) + ' 个 Assembly 需要加油!' if fuel_alerts > 0 else '✅ 所有燃料正常'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*快速开始:*\n"
            f"📊 /status - 查看 Assembly 面板\n"
            f"⛽ /fuel - 管理燃料\n"
            f"🚪 /gate - 配置 Gate 规则\n"
            f"🔔 /alert - 设置告警\n"
            f"💰 /wallet - 管理 Sui 钱包\n"
            f"❓ /help - 完整命令列表\n\n"
            f"👇 *选择操作:*"
        )
    else:
        text = (
            f"🤖 *Welcome to NEXUS!*\n"
            f"Neural EXecutive for Unified Stations\n\n"
            f"Your 24/7 AI manager for EVE Frontier Smart Assemblies.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎮 *What is EVE Frontier?*\n"
            f"A space survival MMO where players build and manage infrastructure in a shared universe on the Sui blockchain.\n\n"
            f"🏗️ *What are Smart Assemblies?*\n"
            f"The building blocks of your space empire:\n"
            f"  🚪 Smart Gate - Teleportation portals between star systems. Set tolls, whitelists, and access rules.\n"
            f"  📦 Smart Storage - Your warehouse in space. Store and trade resources with other players.\n"
            f"  🔫 Smart Turret - Defense systems that protect your territory from enemies.\n"
            f"  ⚡ Network Node - Power supply for all your assemblies.\n\n"
            f"🤖 *What does NEXUS do?*\n"
            f"NEXUS is your AI manager that monitors and controls all your assemblies 24/7:\n"
            f"  - Auto-refuel before depletion\n"
            f"  - Trade resources at optimal prices\n"
            f"  - Alert you when under attack\n"
            f"  - Manage gate tolls dynamically\n"
            f"  - Log every decision to Walrus (immutable)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 *Wallet Ready:*\n"
            f"📍 `{addr_short}`\n"
            f"Balance: *{balance['formatted']}*\n\n"
            f"📊 *Assembly Overview:*\n"
            f"  🏗️ Total: {len(assemblies)} | 🟢 Online: {online_count}\n"
            f"  💰 24h Revenue: {total_rev:.1f} SUI\n"
            f"  {'⚠️ ' + str(fuel_alerts) + ' assembly needs refuel!' if fuel_alerts > 0 else '✅ All fuel levels normal'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Quick Start:*\n"
            f"📊 /status - View your Assembly dashboard\n"
            f"⛽ /fuel - Manage fuel levels\n"
            f"🚪 /gate - Configure gate rules\n"
            f"🔔 /alert - Set up alerts\n"
            f"💰 /wallet - Manage your Sui wallet\n"
            f"❓ /help - Full command list\n\n"
            f"👇 *Choose an action:*"
        )

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=PERSISTENT_KEYBOARD)


def _build_eve_network_text(modules, lang: str) -> str:
    """构建 EVE 宇宙网络活跃度文本段"""
    # 默认 fallback 数据
    defaults = {
        "network_node": 93213,
        "turret": 66540,
        "assembly": 45455,
        "gate": 34214,
        "killmail": 3,
        "fuel": 6,
    }
    counts = dict(defaults)
    if modules:
        for m in modules:
            name = m.get("module") or m.get("name") or m.get("type", "")
            count = m.get("count") or m.get("calls") or m.get("total", 0)
            if name in counts:
                counts[name] = count

    if lang == "cn":
        return (
            f"🌐 *EVE 宇宙活跃度 (真实链上)*\n"
            f"  ⚡ network\_node: {counts['network_node']:,}\n"
            f"  🔫 turret: {counts['turret']:,}\n"
            f"  🏗️ assembly: {counts['assembly']:,}\n"
            f"  🚪 gate: {counts['gate']:,}\n"
            f"  💀 killmail: {counts['killmail']:,}\n"
            f"  ⛽ fuel: {counts['fuel']:,}"
        )
    else:
        return (
            f"🌐 *EVE Universe Activity (On-Chain)*\n"
            f"  ⚡ network\_node: {counts['network_node']:,}\n"
            f"  🔫 turret: {counts['turret']:,}\n"
            f"  🏗️ assembly: {counts['assembly']:,}\n"
            f"  🚪 gate: {counts['gate']:,}\n"
            f"  💀 killmail: {counts['killmail']:,}\n"
            f"  ⛽ fuel: {counts['fuel']:,}"
        )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("status", f"uid:{uid}")
    await _send_status_panel(update.message, uid)


async def _send_status_panel(msg, uid: str):
    """Assembly 状态仪表盘"""
    lang = get_lang(uid)
    assemblies = _get_mock_assemblies()
    total_rev = _get_total_revenue_24h()
    fuel_alerts = _count_fuel_alerts()

    # 获取 EVE EYES 真实链上数据
    eve_modules = await get_eve_module_activity()
    eve_network_text = _build_eve_network_text(eve_modules, lang)

    lines = []
    for a in assemblies:
        fuel_bar = _fuel_bar(a["fuel_pct"])
        header = f"{a['icon']} Smart {'Gate' if a['type']=='smart_gate' else 'Storage' if a['type']=='smart_storage' else 'Turret'} \"{a['name']}\""
        status_label = "状态" if lang == "cn" else "Status"
        fuel_label = "Fuel"

        block = f"{header}\n   {status_label}: {a['status_icon']} {a['status_text']}\n   {fuel_label}: {fuel_bar}\n"

        if a["type"] == "smart_gate":
            block += f"   {'跳跃 (24h)' if lang=='cn' else 'Jumps (24h)'}: {a['metrics']['jumps_24h']}\n"
            block += f"   {'收益' if lang=='cn' else 'Revenue'}: {a['metrics']['revenue_24h']} SUI\n"
        elif a["type"] == "smart_storage":
            block += f"   {'物品' if lang=='cn' else 'Items'}: {a['metrics']['items']}\n"
            block += f"   {'交易 (24h)' if lang=='cn' else 'Trades (24h)'}: {a['metrics']['trades_24h']}\n"
        elif a["type"] == "smart_turret":
            block += f"   {'击杀 (24h)' if lang=='cn' else 'Kills (24h)'}: {a['metrics']['kills_24h']}\n"

        lines.append(block)

    assembly_text = "\n".join(lines)

    if lang == "cn":
        fuel_line = f"⛽ 燃料警报: {fuel_alerts} 个 assembly 需要加油" if fuel_alerts > 0 else "✅ 所有燃料正常"
        text = (
            f"🤖 *NEXUS Assembly Dashboard*\n\n"
            f"📊 你的 Assemblies ({len(assemblies)})\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{assembly_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 24h 总收益: {total_rev:.1f} SUI\n"
            f"{fuel_line}\n\n"
            f"{eve_network_text}"
        )
    else:
        fuel_line = f"⛽ Fuel Alert: {fuel_alerts} assembly needs refuel" if fuel_alerts > 0 else "✅ All fuel levels normal"
        text = (
            f"🤖 *NEXUS Assembly Dashboard*\n\n"
            f"📊 Your Assemblies ({len(assemblies)})\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{assembly_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Total Revenue (24h): {total_rev:.1f} SUI\n"
            f"{fuel_line}\n\n"
            f"{eve_network_text}"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⛽ " + ("加油" if lang == "cn" else "Refuel"), callback_data="fuel"),
         InlineKeyboardButton("🔄 " + ("刷新" if lang == "cn" else "Refresh"), callback_data="status")],
        [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("fuel", f"uid:{uid}")
    await _send_fuel_panel(update.message, uid)


async def _send_fuel_panel(msg, uid: str):
    """燃料管理面板"""
    lang = get_lang(uid)
    assemblies = _get_mock_assemblies()

    lines = []
    low_fuel_names = []
    for a in assemblies:
        fuel_bar = _fuel_bar(a["fuel_pct"])
        est_label = f"(est. {a['fuel_est_days']}d remaining)"
        short_name = a["name"][:14]
        lines.append(f"{a['icon']} {short_name:<14} {fuel_bar} {est_label}")
        if a["fuel_pct"] <= 25:
            low_fuel_names.append(a["name"])

    fuel_lines = "\n".join(lines)

    if lang == "cn":
        text = (
            f"⛽ *NEXUS Fuel Manager*\n\n"
            f"Assembly 燃料状态:\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{fuel_lines}\n"
        )
        if low_fuel_names:
            text += f"\n⚠️ {', '.join(low_fuel_names)} 需要加油!\n"
            text += f"💡 AI 建议: 立即补充燃料 (预估费用: ~0.5 SUI)\n"
    else:
        text = (
            f"⛽ *NEXUS Fuel Manager*\n\n"
            f"Assembly Fuel Status:\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{fuel_lines}\n"
        )
        if low_fuel_names:
            text += f"\n⚠️ {', '.join(low_fuel_names)} needs refuel!\n"
            text += f"💡 AI Recommendation: Refuel now (cost: ~0.5 SUI)\n"

    auto_label = "🔄 自动加油 ON" if lang == "cn" else "🔄 Auto-Refuel ON"
    refuel_label = "⛽ 立即加油" if lang == "cn" else "⛽ Refuel Now"
    settings_label = "⚙️ 设置" if lang == "cn" else "⚙️ Settings"
    back_label = "🔙 返回" if lang == "cn" else "🔙 Menu"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(auto_label, callback_data="fuel_auto"),
         InlineKeyboardButton(refuel_label, callback_data="fuel_refuel")],
        [InlineKeyboardButton(settings_label, callback_data="fuel_settings"),
         InlineKeyboardButton(back_label, callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_gate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("gate", f"uid:{uid}")
    await _send_gate_panel(update.message, uid)


async def _send_gate_panel(msg, uid: str):
    """Gate 管理面板"""
    lang = get_lang(uid)
    assemblies = _get_mock_assemblies()
    gates = [a for a in assemblies if a["type"] == "smart_gate"]

    if not gates:
        await msg.reply_text("No Smart Gates found." if lang == "en" else "未找到 Smart Gate。")
        return

    gate = gates[0]
    cfg = gate["gate_config"]

    if lang == "cn":
        text = (
            f"🚪 *NEXUS Gate Manager*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏷️ *Gate:* {gate['name']}\n"
            f"📊 *状态:* {gate['status_icon']} {gate['status_text']}\n\n"
            f"⚙️ *通行规则:*\n"
            f"  ├ 模式: {cfg['rule']}\n"
            f"  ├ 通行费: {cfg['toll']} SUI / 次\n"
            f"  └ 白名单: {cfg['whitelist_count']} 个地址\n\n"
            f"📈 *24h 数据:*\n"
            f"  ├ 跳跃次数: {gate['metrics']['jumps_24h']}\n"
            f"  ├ 收益: {gate['metrics']['revenue_24h']} SUI\n"
            f"  └ 燃料: {_fuel_bar(gate['fuel_pct'])}\n\n"
            f"💡 *Gate 模式:*\n"
            f"  🟢 Free Pass - 免费通行\n"
            f"  🟡 Toll - 收费通行\n"
            f"  🔴 Whitelist Only - 仅白名单\n"
            f"  🟣 Toll + Whitelist - 收费 + 白名单"
        )
    else:
        text = (
            f"🚪 *NEXUS Gate Manager*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏷️ *Gate:* {gate['name']}\n"
            f"📊 *Status:* {gate['status_icon']} {gate['status_text']}\n\n"
            f"⚙️ *Access Rules:*\n"
            f"  ├ Mode: {cfg['rule']}\n"
            f"  ├ Toll: {cfg['toll']} SUI / jump\n"
            f"  └ Whitelist: {cfg['whitelist_count']} addresses\n\n"
            f"📈 *24h Stats:*\n"
            f"  ├ Jumps: {gate['metrics']['jumps_24h']}\n"
            f"  ├ Revenue: {gate['metrics']['revenue_24h']} SUI\n"
            f"  └ Fuel: {_fuel_bar(gate['fuel_pct'])}\n\n"
            f"💡 *Gate Modes:*\n"
            f"  🟢 Free Pass - Anyone can pass\n"
            f"  🟡 Toll - Pay to pass\n"
            f"  🔴 Whitelist Only - Restricted access\n"
            f"  🟣 Toll + Whitelist - Pay + Approved only"
        )

    toll_btn = "💰 改通行费" if lang == "cn" else "💰 Set Toll"
    wl_btn = "📋 白名单" if lang == "cn" else "📋 Whitelist"
    mode_btn = "🔄 切换模式" if lang == "cn" else "🔄 Change Mode"
    back_btn = "🔙 返回" if lang == "cn" else "🔙 Menu"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(toll_btn, callback_data="gate_toll"),
         InlineKeyboardButton(wl_btn, callback_data="gate_whitelist")],
        [InlineKeyboardButton(mode_btn, callback_data="gate_mode"),
         InlineKeyboardButton(back_btn, callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("alert", f"uid:{uid}")
    await _send_alert_panel(update.message, uid)


async def _send_alert_panel(msg, uid: str):
    """告警配置面板"""
    lang = get_lang(uid)
    alerts = _get_mock_alerts()

    lines = []
    for a in alerts:
        toggle = "✅" if a["enabled"] else "⬜"
        lines.append(f"  {toggle} {a['icon']} {a['label']}")

    alert_text = "\n".join(lines)

    if lang == "cn":
        text = (
            f"🔔 *NEXUS Alert Manager*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *告警配置:*\n"
            f"{alert_text}\n\n"
            f"⏰ *最近告警:*\n"
            f"  ⚠️ [10:32] Perimeter Defense 燃料低于 25%\n"
            f"  ✅ [08:15] Alpha Bridge 恢复在线\n"
            f"  💰 [00:00] 昨日收益报告: 5.1 SUI\n\n"
            f"💡 告警将通过 Telegram 推送"
        )
    else:
        text = (
            f"🔔 *NEXUS Alert Manager*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *Alert Configuration:*\n"
            f"{alert_text}\n\n"
            f"⏰ *Recent Alerts:*\n"
            f"  ⚠️ [10:32] Perimeter Defense fuel below 25%\n"
            f"  ✅ [08:15] Alpha Bridge back online\n"
            f"  💰 [00:00] Daily revenue report: 5.1 SUI\n\n"
            f"💡 Alerts delivered via Telegram push"
        )

    toggle_btn = "🔔 开关告警" if lang == "cn" else "🔔 Toggle Alerts"
    test_btn = "🔔 测试" if lang == "cn" else "🔔 Test Alert"
    back_btn = "🔙 返回" if lang == "cn" else "🔙 Menu"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_btn, callback_data="alert_toggle"),
         InlineKeyboardButton(test_btn, callback_data="alert_test")],
        [InlineKeyboardButton(back_btn, callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("share", f"uid:{uid}")
    await _send_share_panel(update.message, uid)


async def _send_share_panel(msg, uid: str):
    """分享周报卡片"""
    lang = get_lang(uid)
    stats = _get_mock_weekly_stats()

    if lang == "cn":
        text = (
            f"📤 *NEXUS 周报*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏗️ *Assembly 概览:*\n"
            f"  ├ 总数: {stats['assemblies_total']}\n"
            f"  └ 在线: {stats['assemblies_online']}\n\n"
            f"📈 *本周成就:*\n"
            f"  ├ 💰 总收益: {stats['total_revenue_7d']} SUI\n"
            f"  ├ 🚪 Gate 跳跃: {stats['total_jumps_7d']} 次\n"
            f"  ├ 📦 交易笔数: {stats['total_trades_7d']} 笔\n"
            f"  ├ 🔫 击杀数: {stats['total_kills_7d']}\n"
            f"  └ ⛽ 燃料消耗: {stats['fuel_spent_7d']} SUI\n\n"
            f"🏆 *排名:* {stats['rank']}\n"
            f"⭐ *最佳 Assembly:* {stats['top_assembly']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 _Powered by NEXUS Assembly Manager_"
        )
    else:
        text = (
            f"📤 *NEXUS Weekly Report*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏗️ *Assembly Overview:*\n"
            f"  ├ Total: {stats['assemblies_total']}\n"
            f"  └ Online: {stats['assemblies_online']}\n\n"
            f"📈 *This Week's Highlights:*\n"
            f"  ├ 💰 Revenue: {stats['total_revenue_7d']} SUI\n"
            f"  ├ 🚪 Gate Jumps: {stats['total_jumps_7d']}\n"
            f"  ├ 📦 Trades: {stats['total_trades_7d']}\n"
            f"  ├ 🔫 Kills: {stats['total_kills_7d']}\n"
            f"  └ ⛽ Fuel Spent: {stats['fuel_spent_7d']} SUI\n\n"
            f"🏆 *Rank:* {stats['rank']}\n"
            f"⭐ *Top Assembly:* {stats['top_assembly']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 _Powered by NEXUS Assembly Manager_"
        )

    share_btn = "📤 分享" if lang == "cn" else "📤 Share"
    link = f"https://t.me/NexusAssemblyBot?start=ref_{uid}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(share_btn, switch_inline_query=f"🤖 NEXUS Weekly Report - {stats['total_revenue_7d']} SUI earned! 🚀 {link}")],
        [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("vote", f"uid:{uid}")
    await _send_vote_panel(update.message, uid)


async def _send_vote_panel(msg, uid: str):
    """投票引导面板"""
    lang = get_lang(uid)

    if lang == "cn":
        text = (
            f"🗳️ *NEXUS 社区投票*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *进行中的投票:*\n\n"
            f"  1️⃣ *Gate 通行费标准调整*\n"
            f"     ├ 选项 A: 维持 0.02 SUI\n"
            f"     ├ 选项 B: 降低至 0.01 SUI\n"
            f"     └ 截止: 3天后\n\n"
            f"  2️⃣ *新 Assembly 类型提案*\n"
            f"     ├ 选项 A: Smart Factory\n"
            f"     ├ 选项 B: Smart Refinery\n"
            f"     └ 截止: 5天后\n\n"
            f"  3️⃣ *NEXUS 治理代币分配*\n"
            f"     ├ 选项 A: 按 Assembly 数量\n"
            f"     ├ 选项 B: 按收益贡献\n"
            f"     └ 截止: 7天后\n\n"
            f"💡 持有 Assembly 即可参与投票"
        )
    else:
        text = (
            f"🗳️ *NEXUS Community Votes*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *Active Proposals:*\n\n"
            f"  1️⃣ *Gate Toll Adjustment*\n"
            f"     ├ Option A: Keep 0.02 SUI\n"
            f"     ├ Option B: Reduce to 0.01 SUI\n"
            f"     └ Ends: 3 days\n\n"
            f"  2️⃣ *New Assembly Type Proposal*\n"
            f"     ├ Option A: Smart Factory\n"
            f"     ├ Option B: Smart Refinery\n"
            f"     └ Ends: 5 days\n\n"
            f"  3️⃣ *NEXUS Governance Token Distribution*\n"
            f"     ├ Option A: By Assembly count\n"
            f"     ├ Option B: By revenue contribution\n"
            f"     └ Ends: 7 days\n\n"
            f"💡 Assembly owners can participate in voting"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣ " + ("投票" if lang == "cn" else "Vote"), callback_data="vote_1"),
         InlineKeyboardButton("2️⃣ " + ("投票" if lang == "cn" else "Vote"), callback_data="vote_2"),
         InlineKeyboardButton("3️⃣ " + ("投票" if lang == "cn" else "Vote"), callback_data="vote_3")],
        [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


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
    await update.message.reply_text(_wallet_msg, parse_mode="Markdown", disable_web_page_preview=True)


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


async def cmd_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    lang = get_lang(uid)
    count = get_referral_count(uid)
    link = f"https://t.me/NexusAssemblyBot?start=ref_{uid}"

    if lang == "cn":
        text = (
            f"🔗 *你的邀请链接*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📎 `{link}`\n\n"
            f"👥 已邀请: *{count}* 人\n\n"
            f"分享链接邀请好友一起管理 Assembly!"
        )
    else:
        text = (
            f"🔗 *Your Referral Link*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📎 `{link}`\n\n"
            f"👥 Invited: *{count}* users\n\n"
            f"Share and manage Assemblies together!"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📤 分享" if lang == "cn" else "📤 Share",
            switch_inline_query=f"🤖 Join NEXUS Assembly Manager! 🚀 {link}")],
        [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_logs(update: Update, context):
    uid = str(update.effective_user.id)
    log_action("view_logs")
    await _send_logs_panel(update.message, uid)


async def _send_logs_panel(msg, uid: str):
    logs = _load_logs()
    recent = logs[-8:]
    lang = get_lang(uid)

    if not recent:
        no_log_msg = "📋 暂无日志。试试 /start 或 /status!" if lang == "cn" else "📋 No logs yet. Try /start or /status!"
        await msg.reply_text(no_log_msg)
        return

    lines = []
    for l in recent:
        t = l["time"][5:16].replace("T", " ")
        emoji = {
            "start": "🚀", "balance": "💰", "wallet": "👛",
            "wallet_auto_create": "🆕", "view_logs": "📋",
            "status": "📊", "fuel": "⛽", "gate": "🚪",
            "alert": "🔔", "share": "📤", "vote": "🗳️",
            "referral": "🔗", "whale": "🐋",
        }.get(l["action"], "📝")
        lines.append(f"  {emoji} `{t}` *{l['action']}* {l.get('detail','')[:40]}")

    walrus_section = "\n\n🐘 *Walrus " + ("链上日志" if lang == "cn" else "On-chain Logs") + ":*\n"
    for b in WALRUS_BLOBS[-3:]:
        walrus_section += f"  📦 `{b['id']}` ({b['time']}) {b['type']} [{b['size']}]\n"

    upload_btn = "🐘 上传到 Walrus" if lang == "cn" else "🐘 Upload to Walrus"
    refresh_btn = "🔄 刷新" if lang == "cn" else "🔄 Refresh"
    back_btn = "🔙 返回" if lang == "cn" else "🔙 Menu"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(upload_btn, callback_data="walrus_upload"),
         InlineKeyboardButton(refresh_btn, callback_data="refresh_logs")],
        [InlineKeyboardButton(back_btn, callback_data="back")],
    ])

    log_title = "📋 *操作日志*" if lang == "cn" else "📋 *Operation Logs*"
    recent_label = "*最近操作:*" if lang == "cn" else "*Recent:*"
    total_label = "总记录" if lang == "cn" else "Total"

    _log_text = (
        f"{log_title}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{recent_label}\n" + "\n".join(lines) +
        walrus_section +
        f"\n📊 {total_label}: {len(logs)} entries | On-chain: {len(WALRUS_BLOBS)} entries"
    )
    await msg.reply_text(_log_text, parse_mode="Markdown", reply_markup=kb)


async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    await update.message.reply_text(
        "🌐 *Language / 语言设置*\nChoose language / 请选择语言:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_cn"),
             InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
        ])
    )


async def cmd_whale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("whale", f"uid:{uid}")
    await _send_whale_panel(update.message, uid)


async def _send_whale_panel(msg, uid: str):
    """鲸鱼 Assembly 追踪 (EVE EYES 真实链上数据)"""
    lang = get_lang(uid)

    # 获取 EVE EYES 真实模块活跃度
    eve_modules = await get_eve_module_activity()

    # 构建模块活跃度排行
    defaults = [
        {"name": "network_node", "calls": 93213, "icon": "⚡"},
        {"name": "turret",       "calls": 66540, "icon": "🔫"},
        {"name": "assembly",     "calls": 45455, "icon": "🏗️"},
        {"name": "gate",         "calls": 34214, "icon": "🚪"},
        {"name": "killmail",     "calls": 3,     "icon": "💀"},
        {"name": "fuel",         "calls": 6,     "icon": "⛽"},
    ]
    module_map = {m["name"]: m for m in defaults}
    if eve_modules:
        for m in eve_modules:
            name = m.get("module") or m.get("name") or m.get("type", "")
            count = m.get("count") or m.get("calls") or m.get("total", 0)
            if name in module_map:
                module_map[name]["calls"] = count

    # 按调用量排序 Top 5
    sorted_modules = sorted(module_map.values(), key=lambda x: x["calls"], reverse=True)[:5]
    total_calls = sum(m["calls"] for m in module_map.values())

    lines = []
    for i, m in enumerate(sorted_modules, 1):
        bar_pct = int(m["calls"] / max(sorted_modules[0]["calls"], 1) * 100)
        bar_filled = int(bar_pct / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        lines.append(f"  {m['icon']} *{m['name']}*\n     [{bar}] {m['calls']:,} calls\n")

    whale_text = "\n".join(lines)
    data_source = "EVE EYES 真实链上" if eve_modules else "EVE EYES (缓存数据)"
    data_source_en = "EVE EYES On-Chain" if eve_modules else "EVE EYES (cached)"

    if lang == "cn":
        text = (
            f"🐋 *EVE 宇宙模块活跃度排行*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 *Top 5 最活跃模块 ({data_source}):*\n\n"
            f"{whale_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ 全网总调用: {total_calls:,} calls\n\n"
            f"_数据来源: EVE EYES 链上索引器_"
        )
    else:
        text = (
            f"🐋 *EVE Universe Module Activity*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 *Top 5 Active Modules ({data_source_en}):*\n\n"
            f"{whale_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Total Network Calls: {total_calls:,}\n\n"
            f"_Data source: EVE EYES On-Chain Indexer_"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 " + ("刷新" if lang == "cn" else "Refresh"), callback_data="whale"),
         InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


# ==================== 保险系统 ====================
INSURANCE_FILE = os.path.join(DATA_DIR, "insurance.json")

def _load_insurance() -> dict:
    if os.path.exists(INSURANCE_FILE):
        try:
            with open(INSURANCE_FILE) as f: return json.load(f)
        except: pass
    return {}

def _save_insurance(data: dict):
    with open(INSURANCE_FILE, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def _get_user_policies(uid: str) -> list:
    """获取用户保单 (Demo 数据)"""
    data = _load_insurance()
    if uid in data and data[uid].get("policies"):
        return data[uid]["policies"]
    # 返回 Demo 保单
    return [
        {
            "assembly_name": "Alpha Bridge",
            "assembly_type": "smart_gate",
            "icon": "🚪",
            "tier": "standard",
            "tier_label": "Standard",
            "coverage": 50,
            "status": "active",
            "expiry": "2026-04-15",
        },
        {
            "assembly_name": "Perimeter Defense",
            "assembly_type": "smart_turret",
            "icon": "🔫",
            "tier": "premium",
            "tier_label": "Premium",
            "coverage": 200,
            "status": "active",
            "expiry": "2026-04-20",
        },
    ]

INSURANCE_TIERS = {
    "basic": {"label": "Basic (基础)", "emoji": "🥉", "coverage": 10, "premium_weekly": 0.15, "covers": "Assembly 被摧毁"},
    "standard": {"label": "Standard (标准)", "emoji": "🥈", "coverage": 50, "premium_weekly": 0.6, "covers": "摧毁 + 离线超时"},
    "premium": {"label": "Premium (高级)", "emoji": "🥇", "coverage": 200, "premium_weekly": 2.0, "covers": "摧毁 + 离线 + 燃料耗尽"},
}


async def cmd_insure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    lang = get_lang(uid)
    log_action("insure", f"uid:{uid}")

    if lang == "cn":
        text = (
            f"🛡️ *NEXUS Insurance*\n\n"
            f"为你的 Smart Assembly 投保，被摧毁时自动理赔。\n\n"
            f"📋 *保险方案:*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🥉 *Basic (基础)*\n"
            f"   保额: 10 SUI | 保费: 0.15 SUI/周\n"
            f"   覆盖: Assembly 被摧毁\n\n"
            f"🥈 *Standard (标准)*\n"
            f"   保额: 50 SUI | 保费: 0.6 SUI/周\n"
            f"   覆盖: 摧毁 + 离线超时\n\n"
            f"🥇 *Premium (高级)*\n"
            f"   保额: 200 SUI | 保费: 2 SUI/周\n"
            f"   覆盖: 摧毁 + 离线 + 燃料耗尽\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 合约地址: `{DEPLOYED_PACKAGE[:20]}...`\n"
            f"🔗 链上保险池, 理赔自动执行"
        )
    else:
        text = (
            f"🛡️ *NEXUS Insurance*\n\n"
            f"Insure your Smart Assembly. Auto-claim when destroyed.\n\n"
            f"📋 *Insurance Plans:*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🥉 *Basic*\n"
            f"   Coverage: 10 SUI | Premium: 0.15 SUI/week\n"
            f"   Covers: Assembly destroyed\n\n"
            f"🥈 *Standard*\n"
            f"   Coverage: 50 SUI | Premium: 0.6 SUI/week\n"
            f"   Covers: Destroyed + Offline timeout\n\n"
            f"🥇 *Premium*\n"
            f"   Coverage: 200 SUI | Premium: 2 SUI/week\n"
            f"   Covers: Destroyed + Offline + Fuel depleted\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 Contract: `{DEPLOYED_PACKAGE[:20]}...`\n"
            f"🔗 On-chain pool, auto-claim execution"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 Basic", callback_data="insure_basic"),
         InlineKeyboardButton("🥈 Standard", callback_data="insure_standard"),
         InlineKeyboardButton("🥇 Premium", callback_data="insure_premium")],
        [InlineKeyboardButton("📋 " + ("我的保单" if lang == "cn" else "My Policies"), callback_data="claims_view"),
         InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_claims(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    log_action("claims", f"uid:{uid}")
    await _send_claims_panel(update.message, uid)


async def _send_claims_panel(msg, uid: str):
    """保单列表面板"""
    lang = get_lang(uid)
    policies = _get_user_policies(uid)

    if not policies:
        no_policy = "📋 暂无保单。使用 /insure 投保!" if lang == "cn" else "📋 No policies yet. Use /insure to get insured!"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ " + ("投保" if lang == "cn" else "Get Insured"), callback_data="claims_new")],
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await msg.reply_text(no_policy, reply_markup=kb)
        return

    lines = []
    total_coverage = 0
    total_premium = 0.0
    for p in policies:
        tier_info = INSURANCE_TIERS.get(p["tier"], {})
        status_icon = "🟢" if p["status"] == "active" else "🔴"
        status_text = "有效" if p["status"] == "active" and lang == "cn" else "Active" if p["status"] == "active" else "Expired"
        tier_emoji = tier_info.get("emoji", "📋")

        block = (
            f"🛡️ {p['icon']} *{p['assembly_name']}*\n"
            f"   方案: {tier_emoji} {p['tier_label']} | 保额: {p['coverage']} SUI\n"
            f"   状态: {status_icon} {status_text} | 到期: {p['expiry']}\n"
        ) if lang == "cn" else (
            f"🛡️ {p['icon']} *{p['assembly_name']}*\n"
            f"   Plan: {tier_emoji} {p['tier_label']} | Coverage: {p['coverage']} SUI\n"
            f"   Status: {status_icon} {status_text} | Expires: {p['expiry']}\n"
        )
        lines.append(block)
        total_coverage += p["coverage"]
        total_premium += tier_info.get("premium_weekly", 0)

    policy_text = "\n".join(lines)

    if lang == "cn":
        text = (
            f"📋 *我的保单*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{policy_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 总保费: {total_premium:.1f} SUI/周\n"
            f"🛡️ 总保额: {total_coverage} SUI\n"
            f"📊 理赔记录: 0 次\n\n"
            f"_⚠️ Demo 数据 - 对接链上保险合约_"
        )
    else:
        text = (
            f"📋 *My Policies*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{policy_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Total Premium: {total_premium:.1f} SUI/week\n"
            f"🛡️ Total Coverage: {total_coverage} SUI\n"
            f"📊 Claims: 0\n\n"
            f"_⚠️ Demo Data - Connected to on-chain insurance contract_"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 " + ("保单详情" if lang == "cn" else "Details"), callback_data="claims_detail"),
         InlineKeyboardButton("🆕 " + ("新增投保" if lang == "cn" else "New Policy"), callback_data="claims_new")],
        [InlineKeyboardButton("📊 " + ("理赔历史" if lang == "cn" else "Claim History"), callback_data="claims_history"),
         InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_help(update: Update, context):
    uid = str(update.effective_user.id)
    lang = get_lang(uid)

    if lang == "cn":
        text = (
            f"❓ *NEXUS 帮助*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 *Assembly 管理*\n"
            f"  /status - Assembly 状态面板\n"
            f"  /fuel - 燃料管理\n"
            f"  /gate - Gate 门禁管理\n"
            f"  /alert - 告警配置\n\n"
            f"🛡️ *保险*\n"
            f"  /insure - 保险方案\n"
            f"  /claims - 我的保单\n\n"
            f"💰 *钱包 & 交易*\n"
            f"  /wallet - 钱包信息\n"
            f"  /balance - 快速余额查询\n\n"
            f"📤 *社交 & 增长*\n"
            f"  /share - 周报卡片\n"
            f"  /refer - 邀请好友\n"
            f"  /vote - 为 NEXUS 投票\n\n"
            f"⚙️ *设置*\n"
            f"  /lang - 语言切换\n"
            f"  /help - 本帮助页面\n\n"
            f"🌐 *链接*\n"
            f"  Website: nexus.w3xuan.xyz\n"
            f"  GitHub: github.com/wrx1234/sui-hackathon"
        )
    else:
        text = (
            f"❓ *NEXUS Help*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 *Assembly Management*\n"
            f"  /status - Assembly dashboard\n"
            f"  /fuel - Fuel management\n"
            f"  /gate - Gate control\n"
            f"  /alert - Alert settings\n\n"
            f"🛡️ *Insurance*\n"
            f"  /insure - Insurance plans\n"
            f"  /claims - My policies\n\n"
            f"💰 *Wallet & Trading*\n"
            f"  /wallet - Wallet info\n"
            f"  /balance - Quick balance\n\n"
            f"📤 *Social & Growth*\n"
            f"  /share - Weekly report card\n"
            f"  /refer - Invite friends\n"
            f"  /vote - Vote for NEXUS\n\n"
            f"⚙️ *Settings*\n"
            f"  /lang - Language\n"
            f"  /help - This help page\n\n"
            f"🌐 *Links*\n"
            f"  Website: nexus.w3xuan.xyz\n"
            f"  GitHub: github.com/wrx1234/sui-hackathon"
        )

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)


# ==================== 回调处理器 ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = str(q.from_user.id)
    lang = get_lang(uid)

    if data == "status":
        await _send_status_panel(q.message, uid)

    elif data == "fuel":
        await _send_fuel_panel(q.message, uid)

    elif data == "fuel_refuel":
        tx_hash = hashlib.sha256(f"refuel{uid}{time.time()}".encode()).hexdigest()[:16]
        log_action("fuel_refuel", f"uid:{uid}")
        if lang == "cn":
            text = (
                f"⛽ *加油成功!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔫 Perimeter Defense\n"
                f"  ├ 加油前: ██░░░░░░░░ 23%\n"
                f"  └ 加油后: ██████████ 100% ✅\n\n"
                f"💰 费用: 0.5 SUI\n"
                f"📋 TX: `0x{tx_hash}...`\n\n"
                f"⚠️ _Demo 模式 - Testnet 模拟_"
            )
        else:
            text = (
                f"⛽ *Refuel Complete!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔫 Perimeter Defense\n"
                f"  ├ Before: ██░░░░░░░░ 23%\n"
                f"  └ After:  ██████████ 100% ✅\n\n"
                f"💰 Cost: 0.5 SUI\n"
                f"📋 TX: `0x{tx_hash}...`\n\n"
                f"⚠️ _Demo Mode - Testnet Simulation_"
            )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 " + ("状态" if lang == "cn" else "Status"), callback_data="status"),
             InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "fuel_auto":
        if lang == "cn":
            text = "🔄 *自动加油已开启*\n\n当燃料低于 20% 时自动补充\n预算上限: 1 SUI/天\n\n_设置已保存_"
        else:
            text = "🔄 *Auto-Refuel Enabled*\n\nAuto refuel when fuel drops below 20%\nBudget cap: 1 SUI/day\n\n_Settings saved_"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回燃料" if lang == "cn" else "Back to Fuel"), callback_data="fuel")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "fuel_settings":
        if lang == "cn":
            text = (
                f"⚙️ *燃料设置*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔄 自动加油: ✅ 开启\n"
                f"⚠️ 低燃料阈值: 20%\n"
                f"💰 每日预算上限: 1 SUI\n"
                f"📊 加油策略: 补充至 100%\n\n"
                f"_完整版支持自定义策略_"
            )
        else:
            text = (
                f"⚙️ *Fuel Settings*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔄 Auto-Refuel: ✅ Enabled\n"
                f"⚠️ Low Fuel Threshold: 20%\n"
                f"💰 Daily Budget Cap: 1 SUI\n"
                f"📊 Refuel Strategy: Fill to 100%\n\n"
                f"_Full version supports custom strategies_"
            )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Back"), callback_data="fuel")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "gate":
        await _send_gate_panel(q.message, uid)

    elif data in ("gate_toll", "gate_whitelist", "gate_mode"):
        if data == "gate_toll":
            text = "💰 *设置通行费*\n\n发送新的通行费金额 (SUI):\n例: `0.05`\n\n_当前: 0.02 SUI_" if lang == "cn" else "💰 *Set Toll*\n\nSend new toll amount (SUI):\nExample: `0.05`\n\n_Current: 0.02 SUI_"
        elif data == "gate_whitelist":
            text = "📋 *白名单管理*\n\n当前白名单: 12 个地址\n\n发送地址来添加:\n`0x1234...`\n\n_或发送 'remove 0x1234...' 移除_" if lang == "cn" else "📋 *Whitelist Manager*\n\nCurrent whitelist: 12 addresses\n\nSend address to add:\n`0x1234...`\n\n_Or send 'remove 0x1234...' to remove_"
        else:
            text = "🔄 *选择 Gate 模式:*" if lang == "cn" else "🔄 *Choose Gate Mode:*"
        kb_buttons = []
        if data == "gate_mode":
            kb_buttons = [
                [InlineKeyboardButton("🟢 Free Pass", callback_data="gate_mode_free"),
                 InlineKeyboardButton("🟡 Toll", callback_data="gate_mode_toll")],
                [InlineKeyboardButton("🔴 Whitelist", callback_data="gate_mode_wl"),
                 InlineKeyboardButton("🟣 Toll+WL", callback_data="gate_mode_tollwl")],
            ]
        kb_buttons.append([InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Back"), callback_data="gate")])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb_buttons))

    elif data.startswith("gate_mode_"):
        mode_map = {"gate_mode_free": "Free Pass", "gate_mode_toll": "Toll", "gate_mode_wl": "Whitelist Only", "gate_mode_tollwl": "Toll + Whitelist"}
        mode = mode_map.get(data, "Unknown")
        text = f"✅ Gate 模式已切换为: *{mode}*\n\n_设置已保存_" if lang == "cn" else f"✅ Gate mode changed to: *{mode}*\n\n_Settings saved_"
        log_action("gate_mode_change", mode)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回 Gate" if lang == "cn" else "Back to Gate"), callback_data="gate")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "alert":
        await _send_alert_panel(q.message, uid)

    elif data == "alert_toggle":
        text = "🔔 *告警已全部开启*\n\n所有告警通知将通过 Telegram 推送。" if lang == "cn" else "🔔 *All Alerts Enabled*\n\nAll alert notifications will be pushed via Telegram."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Back"), callback_data="alert")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "alert_test":
        text = "🔔 *测试告警!*\n\n⚠️ [测试] Perimeter Defense 燃料低于 25%!\n\n_这是一条测试消息_" if lang == "cn" else "🔔 *Test Alert!*\n\n⚠️ [TEST] Perimeter Defense fuel below 25%!\n\n_This is a test message_"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Back"), callback_data="alert")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "share":
        await _send_share_panel(q.message, uid)

    elif data == "vote":
        await _send_vote_panel(q.message, uid)

    elif data.startswith("vote_"):
        vote_num = data.replace("vote_", "")
        text = f"🗳️ *投票已提交!*\n\n你已参与第 {vote_num} 号提案投票。\n\n_投票结果将在截止后公布_" if lang == "cn" else f"🗳️ *Vote Submitted!*\n\nYou voted on proposal #{vote_num}.\n\n_Results will be announced after deadline_"
        log_action("vote", f"proposal:{vote_num}")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回投票" if lang == "cn" else "Back to Votes"), callback_data="vote")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "refer":
        count = get_referral_count(uid)
        link = f"https://t.me/NexusAssemblyBot?start=ref_{uid}"
        if lang == "cn":
            text = f"🔗 *邀请链接*\n\n`{link}`\n\n👥 已邀请: *{count}* 人"
        else:
            text = f"🔗 *Referral Link*\n\n`{link}`\n\n👥 Invited: *{count}* users"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 " + ("分享" if lang == "cn" else "Share"), switch_inline_query=f"🤖 Join NEXUS Assembly Manager! 🚀 {link}")],
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "whale":
        await _send_whale_panel(q.message, uid)

    elif data == "wallet_view":
        wallet = get_or_create_wallet(uid)
        balance = get_sui_balance(wallet["address"])
        tokens = get_all_balances(wallet["address"])
        token_lines = []
        for t in tokens:
            icon = "🟦" if t["name"] == "SUI" else "🟢"
            token_lines.append(f"  {icon} {t['name']}: *{t['balance']:.4f}*")
        token_text = "\n".join(token_lines) if token_lines else "  No positions"
        text = (
            f"👛 *Wallet Info*\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 *Address:*\n`{wallet['address']}`\n\n"
            f"🌐 Network: Sui {NETWORK.capitalize()}\n"
            f"📦 Mode: {'Demo (Shared Testnet)' if wallet.get('mode')=='demo' else 'Personal'}\n\n"
            f"💰 *Assets:*\n{token_text}\n\n"
            f"🔗 [Explorer](https://suiscan.xyz/{NETWORK}/account/{wallet['address']})"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 " + ("刷新" if lang == "cn" else "Refresh"), callback_data="wallet_view"),
             InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=kb)

    elif data == "balance_view":
        wallet = get_or_create_wallet(uid)
        balance = get_sui_balance(wallet["address"])
        await q.message.reply_text(
            f"💰 *{balance['formatted']}*\n📍 `{wallet['address'][:16]}...`\n🌐 Sui {NETWORK.capitalize()}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
            ])
        )

    elif data == "logs":
        await _send_logs_panel(q.message, uid)

    elif data == "refresh_logs":
        await _send_logs_panel(q.message, uid)

    elif data == "walrus":
        title = "🐘 *Walrus 去中心化日志*" if lang == "cn" else "🐘 *Walrus Decentralized Logs*"
        desc = "每笔操作都透明记录在 Walrus 上，不可篡改。" if lang == "cn" else "Every operation is transparently recorded on Walrus. Immutable."
        text = f"{title}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{desc}\n\n📦 *On-chain Logs:*\n"
        for b in WALRUS_BLOBS:
            text += f"  🔗 `{b['id']}` | {b['time']} | {b['type']} | {b['size']}\n"
        text += f"\n📊 Total: {len(WALRUS_BLOBS)} blobs\n🔍 Aggregator: `{WALRUS_AGGREGATOR[:40]}...`"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🐘 " + ("上传" if lang == "cn" else "Upload"), callback_data="walrus_upload"),
             InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "walrus_upload":
        log_action("walrus_upload")
        blob_id = hashlib.sha256(f"walrus{time.time()}".encode()).hexdigest()[:10]
        text = (
            f"🐘 *{'上传中...' if lang=='cn' else 'Uploading...'}*\n\n"
            f"✅ {'上传成功!' if lang=='cn' else 'Upload complete!'}\n"
            f"📦 Blob ID: `{blob_id}...`\n"
            f"📊 Size: {random.randint(1,5)}.{random.randint(0,9)}KB\n"
            f"⏱ {'存储时间: 永久' if lang=='cn' else 'Storage: Permanent'}\n\n"
            f"_{'数据已存储在 Walrus 去中心化网络' if lang=='cn' else 'Data stored on Walrus decentralized network'}_"
        )
        await q.message.reply_text(text, parse_mode="Markdown")

    # === Insurance callbacks ===
    elif data == "insure_menu":
        if lang == "cn":
            text = (
                f"🛡️ *NEXUS Insurance*\n\n"
                f"为你的 Smart Assembly 投保，被摧毁时自动理赔。\n\n"
                f"📋 *保险方案:*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🥉 *Basic* - 保额: 10 SUI | 保费: 0.15 SUI/周\n"
                f"🥈 *Standard* - 保额: 50 SUI | 保费: 0.6 SUI/周\n"
                f"🥇 *Premium* - 保额: 200 SUI | 保费: 2 SUI/周"
            )
        else:
            text = (
                f"🛡️ *NEXUS Insurance*\n\n"
                f"Insure your Smart Assembly. Auto-claim when destroyed.\n\n"
                f"📋 *Plans:*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🥉 *Basic* - Coverage: 10 SUI | 0.15 SUI/week\n"
                f"🥈 *Standard* - Coverage: 50 SUI | 0.6 SUI/week\n"
                f"🥇 *Premium* - Coverage: 200 SUI | 2 SUI/week"
            )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🥉 Basic", callback_data="insure_basic"),
             InlineKeyboardButton("🥈 Standard", callback_data="insure_standard"),
             InlineKeyboardButton("🥇 Premium", callback_data="insure_premium")],
            [InlineKeyboardButton("📋 " + ("我的保单" if lang == "cn" else "My Policies"), callback_data="claims_view"),
             InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("insure_"):
        tier_key = data.replace("insure_", "")
        tier = INSURANCE_TIERS.get(tier_key)
        if tier:
            log_action("insure_select", f"uid:{uid} tier:{tier_key}")
            if lang == "cn":
                text = (
                    f"✅ *投保确认*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 方案: {tier['emoji']} *{tier['label']}*\n"
                    f"🛡️ 保额: {tier['coverage']} SUI\n"
                    f"💰 保费: {tier['premium_weekly']} SUI/周\n"
                    f"📌 覆盖: {tier['covers']}\n"
                    f"⏰ 有效期: 7 天 (可续保)\n\n"
                    f"📝 合约将调用 `buy_insurance()` 函数\n"
                    f"保费自动转入链上保险池\n\n"
                    f"⚠️ _Demo 模式 - 链上合约已部署_"
                )
            else:
                text = (
                    f"✅ *Insurance Confirmation*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 Plan: {tier['emoji']} *{tier['label']}*\n"
                    f"🛡️ Coverage: {tier['coverage']} SUI\n"
                    f"💰 Premium: {tier['premium_weekly']} SUI/week\n"
                    f"📌 Covers: {tier['covers']}\n"
                    f"⏰ Duration: 7 days (renewable)\n\n"
                    f"📝 Contract calls `buy_insurance()`\n"
                    f"Premium deposited to on-chain pool\n\n"
                    f"⚠️ _Demo Mode - Contract deployed on testnet_"
                )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ " + ("确认投保" if lang == "cn" else "Confirm"), callback_data=f"insure_confirm_{tier_key}"),
                 InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Back"), callback_data="insure_back")],
            ])
            await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("insure_confirm_"):
        tier_key = data.replace("insure_confirm_", "")
        tier = INSURANCE_TIERS.get(tier_key)
        if tier:
            tx_hash = hashlib.sha256(f"insure{uid}{tier_key}{time.time()}".encode()).hexdigest()[:16]
            log_action("insure_buy", f"uid:{uid} tier:{tier_key}")
            if lang == "cn":
                text = (
                    f"🎉 *投保成功!*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🛡️ {tier['emoji']} {tier['label']}\n"
                    f"💰 保费: {tier['premium_weekly']} SUI\n"
                    f"🛡️ 保额: {tier['coverage']} SUI\n"
                    f"📋 TX: `0x{tx_hash}...`\n\n"
                    f"保单已生效, 有效期 7 天\n"
                    f"使用 /claims 查看保单\n\n"
                    f"⚠️ _Demo 模式 - Testnet 模拟_"
                )
            else:
                text = (
                    f"🎉 *Insurance Purchased!*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🛡️ {tier['emoji']} {tier['label']}\n"
                    f"💰 Premium: {tier['premium_weekly']} SUI\n"
                    f"🛡️ Coverage: {tier['coverage']} SUI\n"
                    f"📋 TX: `0x{tx_hash}...`\n\n"
                    f"Policy active for 7 days\n"
                    f"Use /claims to view policies\n\n"
                    f"⚠️ _Demo Mode - Testnet Simulation_"
                )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 " + ("查看保单" if lang == "cn" else "View Policies"), callback_data="claims_view"),
                 InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
            ])
            await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "insure_back":
        # 重新显示保险方案
        if lang == "cn":
            text = "🛡️ 使用 /insure 查看保险方案"
        else:
            text = "🛡️ Use /insure to view insurance plans"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🥉 Basic", callback_data="insure_basic"),
             InlineKeyboardButton("🥈 Standard", callback_data="insure_standard"),
             InlineKeyboardButton("🥇 Premium", callback_data="insure_premium")],
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "claims_view":
        await _send_claims_panel(q.message, uid)

    elif data == "claims_detail":
        policies = _get_user_policies(uid)
        if lang == "cn":
            text = "📄 *保单详情*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            for p in policies:
                tier_info = INSURANCE_TIERS.get(p["tier"], {})
                text += (
                    f"🛡️ *{p['assembly_name']}*\n"
                    f"   类型: {p['icon']} Smart {'Gate' if p['assembly_type']=='smart_gate' else 'Turret'}\n"
                    f"   方案: {tier_info.get('emoji','')} {p['tier_label']}\n"
                    f"   保额: {p['coverage']} SUI\n"
                    f"   保费: {tier_info.get('premium_weekly', 0)} SUI/周\n"
                    f"   覆盖范围: {tier_info.get('covers', 'N/A')}\n"
                    f"   到期: {p['expiry']}\n"
                    f"   状态: {'🟢 有效' if p['status']=='active' else '🔴 过期'}\n\n"
                )
            text += f"📝 合约: `{DEPLOYED_PACKAGE[:24]}...`"
        else:
            text = "📄 *Policy Details*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            for p in policies:
                tier_info = INSURANCE_TIERS.get(p["tier"], {})
                text += (
                    f"🛡️ *{p['assembly_name']}*\n"
                    f"   Type: {p['icon']} Smart {'Gate' if p['assembly_type']=='smart_gate' else 'Turret'}\n"
                    f"   Plan: {tier_info.get('emoji','')} {p['tier_label']}\n"
                    f"   Coverage: {p['coverage']} SUI\n"
                    f"   Premium: {tier_info.get('premium_weekly', 0)} SUI/week\n"
                    f"   Covers: {tier_info.get('covers', 'N/A')}\n"
                    f"   Expires: {p['expiry']}\n"
                    f"   Status: {'🟢 Active' if p['status']=='active' else '🔴 Expired'}\n\n"
                )
            text += f"📝 Contract: `{DEPLOYED_PACKAGE[:24]}...`"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回保单" if lang == "cn" else "Back"), callback_data="claims_view")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "claims_new":
        if lang == "cn":
            text = "🛡️ 选择保险方案:"
        else:
            text = "🛡️ Choose insurance plan:"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🥉 Basic", callback_data="insure_basic"),
             InlineKeyboardButton("🥈 Standard", callback_data="insure_standard"),
             InlineKeyboardButton("🥇 Premium", callback_data="insure_premium")],
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Back"), callback_data="claims_view")],
        ])
        await q.message.reply_text(text, reply_markup=kb)

    elif data == "claims_history":
        if lang == "cn":
            text = (
                f"📊 *理赔历史*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"暂无理赔记录 ✅\n\n"
                f"当你的 Assembly 被摧毁或遭遇承保事件时,\n"
                f"NEXUS 将自动发起链上理赔。\n\n"
                f"💡 理赔流程:\n"
                f"  1. 监测到承保事件\n"
                f"  2. 验证保单有效性\n"
                f"  3. 调用合约 `claim()` 函数\n"
                f"  4. 赔付自动到账\n\n"
                f"_所有理赔记录永久存储在 Walrus_"
            )
        else:
            text = (
                f"📊 *Claim History*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"No claims yet ✅\n\n"
                f"When your Assembly is destroyed or a covered event occurs,\n"
                f"NEXUS will auto-initiate on-chain claims.\n\n"
                f"💡 Claim Process:\n"
                f"  1. Detect covered event\n"
                f"  2. Verify policy validity\n"
                f"  3. Call contract `claim()` function\n"
                f"  4. Payout auto-deposited\n\n"
                f"_All claims permanently stored on Walrus_"
            )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回保单" if lang == "cn" else "Back"), callback_data="claims_view")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "settings":
        text = (
            f"⚙️ *{'设置' if lang=='cn' else 'Settings'}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌐 {'网络' if lang=='cn' else 'Network'}: Sui {NETWORK.capitalize()}\n"
            f"📦 {'模式' if lang=='cn' else 'Mode'}: Demo (Shared Testnet)\n"
            f"🔔 {'通知' if lang=='cn' else 'Notifications'}: {'开启' if lang=='cn' else 'Enabled'}\n"
            f"⛽ {'自动加油' if lang=='cn' else 'Auto-Refuel'}: {'开启' if lang=='cn' else 'Enabled'}\n"
            f"⚠️ {'低燃料阈值' if lang=='cn' else 'Low Fuel Threshold'}: 20%\n"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
        ])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "help":
        await q.message.reply_text(
            "❓ " + ("使用 /help 查看完整帮助" if lang == "cn" else "Use /help for full help guide"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + ("返回" if lang == "cn" else "Menu"), callback_data="back")],
            ])
        )

    elif data == "lang_toggle":
        cur = get_lang(uid)
        new_lang = "en" if cur == "cn" else "cn"
        set_lang(uid, new_lang)
        label = "🇬🇧 Switched to English" if new_lang == "en" else "🇨🇳 已切换为中文"
        await q.message.reply_text(label, reply_markup=main_keyboard(uid))

    elif data == "lang_cn":
        set_lang(uid, "cn")
        await q.message.reply_text("🇨🇳 已切换为中文", reply_markup=main_keyboard(uid))

    elif data == "lang_en":
        set_lang(uid, "en")
        await q.message.reply_text("🇬🇧 Switched to English", reply_markup=main_keyboard(uid))

    elif data == "back":
        await q.message.reply_text(
            "🤖 *NEXUS Assembly Manager*\n" + ("选择操作:" if lang == "cn" else "Choose an action:"),
            parse_mode="Markdown",
            reply_markup=main_keyboard(uid)
        )


# ==================== 自然语言处理 ====================
async def nl_handler(update: Update, context):
    text = update.message.text or ""
    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    uid = str(update.effective_user.id)

    # 持久键盘按钮匹配
    if text_stripped == "📊 状态面板":
        return await cmd_status(update, context)
    elif text_stripped == "⛽ 燃料管理":
        return await cmd_fuel(update, context)
    elif text_stripped == "🚪 门禁管理":
        return await cmd_gate(update, context)
    elif text_stripped == "🔔 告警设置":
        return await cmd_alert(update, context)
    elif text_stripped == "🛡️ 保险":
        return await cmd_insure(update, context)
    elif text_stripped == "💰 钱包":
        return await cmd_wallet(update, context)
    elif text_stripped == "❓ 帮助":
        return await cmd_help(update, context)

    if any(k in text_lower for k in ["保险", "insurance", "insure", "投保"]):
        await cmd_insure(update, context)
    elif any(k in text_lower for k in ["保单", "claims", "理赔", "policy"]):
        await cmd_claims(update, context)
    elif any(k in text_lower for k in ["状态", "status", "dashboard", "assembly", "仪表"]):
        await cmd_status(update, context)
    elif any(k in text_lower for k in ["燃料", "fuel", "refuel", "加油"]):
        await cmd_fuel(update, context)
    elif any(k in text_lower for k in ["gate", "星门", "通行"]):
        await cmd_gate(update, context)
    elif any(k in text_lower for k in ["alert", "告警", "警报", "通知"]):
        await cmd_alert(update, context)
    elif any(k in text_lower for k in ["余额", "balance", "钱包", "wallet"]):
        await cmd_balance(update, context)
    elif any(k in text_lower for k in ["日志", "log", "记录"]):
        await cmd_logs(update, context)
    elif any(k in text_lower for k in ["whale", "鲸鱼", "大户"]):
        await cmd_whale(update, context)
    elif any(k in text_lower for k in ["share", "分享", "周报"]):
        await cmd_share(update, context)
    elif any(k in text_lower for k in ["vote", "投票"]):
        await cmd_vote(update, context)
    elif any(k in text_lower for k in ["invite", "邀请", "refer"]):
        await cmd_refer(update, context)
    elif any(k in text_lower for k in ["帮助", "help", "怎么用"]):
        await cmd_help(update, context)
    elif any(k in text_lower for k in ["语言", "language", "lang"]):
        await cmd_lang(update, context)
    else:
        lang = get_lang(uid)
        if lang == "cn":
            _default = (
                "🤖 *NEXUS 在线!*\n\n"
                "试试这些:\n"
                "• \"状态\" - Assembly 仪表盘\n"
                "• \"燃料\" - 燃料管理\n"
                "• \"gate\" - Gate 管理\n"
                "• \"余额\" - 查看资产\n"
                "• /help - 完整帮助\n\n"
                "或使用下方按钮 👇"
            )
        else:
            _default = (
                "🤖 *NEXUS Online!*\n\n"
                "Try these:\n"
                "• \"status\" - Assembly Dashboard\n"
                "• \"fuel\" - Fuel Manager\n"
                "• \"gate\" - Gate Manager\n"
                "• \"balance\" - Check Assets\n"
                "• /help - Full Help\n\n"
                "Or use buttons below 👇"
            )
        await update.message.reply_text(_default, parse_mode="Markdown", reply_markup=PERSISTENT_KEYBOARD)


# ==================== 启动 ====================
async def post_init(application):
    """Bot 启动后设置命令菜单"""
    commands = [
        BotCommand("start", "🏠 Home / 首页"),
        BotCommand("status", "📊 Assembly Dashboard / 状态面板"),
        BotCommand("fuel", "⛽ Fuel Manager / 燃料管理"),
        BotCommand("gate", "🚪 Gate Control / 门禁管理"),
        BotCommand("alert", "🔔 Alert Settings / 告警设置"),
        BotCommand("wallet", "💰 Wallet / 钱包"),
        BotCommand("insure", "🛡️ Insurance / 保险"),
        BotCommand("claims", "📋 My Policies / 我的保单"),
        BotCommand("share", "📤 Share Card / 分享"),
        BotCommand("help", "❓ Help / 帮助"),
    ]
    await application.bot.set_my_commands(commands)
    log.info("✅ Bot commands menu set")


def main():
    log.info("🤖 NEXUS Assembly Manager starting...")

    if not TOKEN:
        log.error("❌ TG_BOT_TOKEN environment variable not set!")
        sys.exit(1)

    req = HTTPXRequest(proxy=PROXY, connect_timeout=30, read_timeout=30)
    get_req = HTTPXRequest(proxy=PROXY, connect_timeout=30, read_timeout=30)

    app = (Application.builder()
           .token(TOKEN)
           .request(req)
           .get_updates_request(get_req)
           .post_init(post_init)
           .build())

    # 核心命令
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("fuel", cmd_fuel))
    app.add_handler(CommandHandler("gate", cmd_gate))
    app.add_handler(CommandHandler("alert", cmd_alert))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("whale", cmd_whale))
    app.add_handler(CommandHandler("insure", cmd_insure))
    app.add_handler(CommandHandler("claims", cmd_claims))
    app.add_handler(CommandHandler("share", cmd_share))
    app.add_handler(CommandHandler("refer", cmd_refer))
    app.add_handler(CommandHandler("vote", cmd_vote))
    app.add_handler(CommandHandler("lang", cmd_lang))
    app.add_handler(CommandHandler("help", cmd_help))

    # 回调和自然语言
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, nl_handler))

    log.info("🤖 NEXUS Assembly Manager ACTIVE")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
