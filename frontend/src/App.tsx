import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { SplineScene } from '@/components/ui/splite'
import { Spotlight } from '@/components/ui/spotlight'
import { GlassButton } from '@/components/ui/glass-button'
import { FeaturesWithHoverEffects } from '@/components/ui/feature-hover'
import { FeatureSteps } from '@/components/ui/feature-steps'
import { BentoGrid, BentoCard } from '@/components/ui/bento-grid'
import { CategoryList } from '@/components/ui/category-list'
import { Features2 } from '@/components/ui/features-2'
import { FinancialDashboard } from '@/components/ui/financial-dashboard'
import {
  IconDashboard, IconGasStation, IconCoin, IconShield,
  IconDoor, IconChartLine, IconNotebook, IconMessage,
} from '@tabler/icons-react'
import {
  Waves, Anchor, HardDrive, Shield, Brain, ArrowLeftRight,
  Target, TrendingUp, Briefcase, Zap, ShieldCheck, BarChart3,
  Crosshair, ArrowRight, Copy, CheckIcon, Bot, Globe, Database,
} from 'lucide-react'
import { Footer } from '@/components/ui/Footer'

function App() {
  const [lang, setLang] = useState<'en' | 'cn'>('en')
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(true)
  const [fadeOut, setFadeOut] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setFadeOut(true)
      setTimeout(() => setLoading(false), 600)
    }, 2500)
    return () => clearTimeout(timer)
  }, [])
  const t = (en: string, cn: string) => lang === 'en' ? en : cn

  // ==================== DATA ====================
  const features8 = [
    { title: t('Assembly Dashboard', '组装体仪表盘'), description: t('Real-time status of all your Smart Assemblies', '所有智能组装体的实时状态'), icon: <IconDashboard size={28} /> },
    { title: t('Smart Fuel Management', '智能燃料管理'), description: t('AI monitors and auto-refuels before depletion', 'AI 监控并在耗尽前自动补充燃料'), icon: <IconGasStation size={28} /> },
    { title: t('Automated Trading', '自动交易'), description: t('Buy/sell resources at optimal prices via Storage Units', '通过存储单元以最优价格买卖资源'), icon: <IconCoin size={28} /> },
    { title: t('Defense Alerts', '防御警报'), description: t('Instant notifications when Turrets detect threats', '炮塔检测到威胁时即时通知'), icon: <IconShield size={28} /> },
    { title: t('Gate Control', '星门控制'), description: t('Dynamic toll pricing, whitelists, and access rules', '动态通行费定价、白名单和访问规则'), icon: <IconDoor size={28} /> },
    { title: t('Revenue Tracking', '收入追踪'), description: t('Daily/weekly reports on gate fees and trade profits', '每日/每周星门费用和交易利润报告'), icon: <IconChartLine size={28} /> },
    { title: t('Walrus Audit Log', 'Walrus 审计日志'), description: t('Every AI decision recorded on decentralized storage', '每个 AI 决策都记录在去中心化存储上'), icon: <IconNotebook size={28} /> },
    { title: t('Natural Language', '自然语言'), description: t('"Raise gate toll by 20%" - manage via plain text', '"把星门通行费提高20%" - 用自然语言管理'), icon: <IconMessage size={28} /> },
  ]

  const ecosystemSteps = [
    { step: t('Connect', '连接'), title: t('Connect', '连接'), content: t('Link your EVE Frontier wallet and Smart Assemblies to NEXUS via Telegram. One-click setup, instant monitoring.', '通过 Telegram 将你的 EVE Frontier 钱包和智能组装体连接到 NEXUS。一键设置，即时监控。'), image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800' },
    { step: t('Monitor', '监控'), title: t('Monitor', '监控'), content: t('AI continuously tracks fuel levels, gate traffic, turret alerts, and market prices across all your assemblies.', 'AI 持续追踪所有组装体的燃料水平、星门流量、炮塔警报和市场价格。'), image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800' },
    { step: t('Automate', '自动化'), title: t('Automate', '自动化'), content: t('Set rules and let NEXUS handle the rest: auto-refuel, dynamic pricing, trade execution - all logged on Walrus.', '设置规则，让 NEXUS 处理其余事务：自动补充燃料、动态定价、交易执行 - 全部记录在 Walrus 上。'), image: 'https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=800' },
    { step: t('Grow', '增长'), title: t('Grow', '增长'), content: t('Invite other station owners. Referral rewards + shared intelligence network. Your fleet grows stronger together.', '邀请其他空间站拥有者。推荐奖励 + 共享情报网络。你的舰队一起变得更强大。'), image: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800' },
  ]

  const ecosystemStats = [
    { value: '15,000+', label: t('Indexed Transactions', '已索引交易') },
    { value: '295,000+', label: t('Move Calls Tracked', 'Move 调用追踪') },
    { value: '1', label: t('Deployed Insurance Contract', '已部署保险合约') },
    { value: '6', label: t('Bot Modules', 'Bot 模块') },
  ]

  const archCards = [
    { name: 'Telegram Bot', Icon: Bot, description: t('User-friendly chat interface for managing all assembly operations via natural language', '用户友好的聊天界面，通过自然语言管理所有组装体操作'), className: 'lg:row-start-1 lg:row-end-3 lg:col-start-1 lg:col-end-2', href: 'https://t.me/EVENexusBot' },
    { name: 'AI Decision Engine', Icon: Brain, description: t('GPT-powered intelligence for market analysis, threat assessment, and autonomous decision-making', 'GPT 驱动的智能引擎，用于市场分析、威胁评估和自主决策'), className: 'lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2', href: '#' },
    { name: 'Sui Move Contracts', Icon: Waves, description: t('On-chain smart contracts for secure asset management and automated transactions', '链上智能合约，用于安全资产管理和自动化交易'), className: 'lg:col-start-2 lg:col-end-3 lg:row-start-2 lg:row-end-3', href: 'https://docs.sui.io/' },
    { name: 'EVE Frontier API', Icon: Globe, description: t('Direct integration with EVE Frontier World API for real-time game state data', '与 EVE Frontier World API 直接集成，获取实时游戏状态数据'), className: 'lg:col-start-3 lg:col-end-4 lg:row-start-1 lg:row-end-2', href: 'https://docs.evefrontier.com/' },
    { name: 'Walrus Storage', Icon: Database, description: t('Decentralized storage for immutable audit logs of every AI decision and transaction', '去中心化存储，不可篡改地记录每个 AI 决策和交易'), className: 'lg:col-start-3 lg:col-end-4 lg:row-start-2 lg:row-end-3', href: 'https://docs.sui.io/' },
  ]

  const viralCategories = [
    { id: 1, title: t('Referral System', '推荐系统'), subtitle: t('Invite station owners, earn rewards when they join NEXUS', '邀请空间站拥有者，他们加入 NEXUS 时获得奖励'), icon: <ArrowRight className="w-8 h-8" />, featured: true },
    { id: 2, title: t('Fleet Intelligence', '舰队情报'), subtitle: t('Shared market data and threat alerts across allied stations', '联盟空间站间共享市场数据和威胁警报'), icon: <TrendingUp className="w-8 h-8" /> },
    { id: 3, title: t('Leaderboard', '排行榜'), subtitle: t('Compete on revenue, efficiency, and defense metrics', '在收入、效率和防御指标上竞争'), icon: <ShieldCheck className="w-8 h-8" /> },
  ]

  const securityFeatures = [
    { icon: <HardDrive className="size-6" />, title: t('Walrus Audit Trail', 'Walrus 审计追踪'), description: t('Every AI decision, every trade - permanently recorded on decentralized storage for full accountability', '每个 AI 决策、每笔交易 - 永久记录在去中心化存储上，完全可追责') },
    { icon: <Shield className="size-6" />, title: t('Move Contract Security', 'Move 合约安全'), description: t('Audited Move smart contracts with multi-sig authorization and configurable risk limits', '经审计的 Move 智能合约，多签授权和可配置的风控限制') },
    { icon: <BarChart3 className="size-6" />, title: t('Risk Management', '风险控制'), description: t('AI-powered risk assessment with spending caps, cooldown periods, and anomaly detection', 'AI 驱动的风险评估，支出上限、冷却期和异常检测') },
  ]

  const dashQuickActions = [
    { icon: ArrowLeftRight, title: t('Trade', '交易'), description: t('Buy/sell resources', '买卖资源') },
    { icon: Crosshair, title: t('Defense', '防御'), description: t('Turret status', '炮塔状态') },
    { icon: TrendingUp, title: t('Revenue', '收入'), description: t('Gate fees & profits', '星门费用和利润') },
    { icon: Briefcase, title: t('Assemblies', '组装体'), description: t('All stations', '所有空间站') },
  ]
  const dashActivity = [
    { icon: <div className="w-9 h-9 flex items-center justify-center rounded-full font-bold text-white text-sm bg-cyan-600">⛽</div>, title: t('Auto-Refuel: Station Alpha', '自动补充燃料：Alpha 站'), time: '2 hours ago', amount: 42.50 },
    { icon: <div className="w-9 h-9 flex items-center justify-center rounded-full font-bold text-white text-sm bg-purple-600">🚪</div>, title: t('Gate Toll Collected', '星门通行费收取'), time: '4 hours ago', amount: 18.20 },
    { icon: <div className="w-9 h-9 flex items-center justify-center rounded-full font-bold text-white text-sm bg-green-600">💰</div>, title: t('Resource Trade: Iron → Fuel', '资源交易：铁 → 燃料'), time: '1 day ago', amount: 3.80 },
  ]
  const dashServices = [
    { icon: Zap, title: t('Auto Pilot', '自动驾驶'), description: t('AI-managed assembly operations', 'AI 管理组装体运营'), isPremium: true },
    { icon: Target, title: t('Threat Monitor', '威胁监控'), description: t('Real-time turret & defense alerts', '实时炮塔和防御警报'), hasAction: true },
    { icon: TrendingUp, title: t('Revenue Optimizer', '收入优化'), description: t('Dynamic gate pricing & trade timing', '动态星门定价和交易时机') },
  ]

  const copyLink = () => {
    navigator.clipboard.writeText('https://t.me/EVENexusBot')
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="min-h-screen bg-[#09090b] text-white">
      {/* ===== LOADING SCREEN ===== */}
      {loading && (
        <div className={`fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#09090b] transition-opacity duration-500 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
          <div className="mb-8 text-5xl font-bold tracking-widest text-cyan-400" style={{ animation: 'sui-pulse 1.5s ease-in-out infinite' }}>
            ⬡
          </div>
          <p className="text-lg font-mono text-neutral-300 mb-6 tracking-wider">Initializing NEXUS...</p>
          <p className="text-xs text-neutral-600 mb-8 tracking-widest">Neural EXecutive for Unified Stations</p>
          <div className="w-64 h-1 bg-neutral-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full" style={{ animation: 'loading-bar 2.2s ease-in-out forwards' }} />
          </div>
          <style>{`
            @keyframes loading-bar { 0% { width: 0% } 60% { width: 70% } 100% { width: 100% } }
            @keyframes sui-pulse { 0%,100% { opacity: 0.5; transform: scale(0.95) } 50% { opacity: 1; transform: scale(1.05) } }
          `}</style>
        </div>
      )}

      {/* ===== HEADER ===== */}
      <header className="sticky top-0 z-50 w-full border-b border-neutral-800/50 bg-[#09090b]/80 backdrop-blur-lg">
        <nav className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4">
          <a href="#" className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-400">NEXUS</a>
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm text-neutral-400 hover:text-white transition">Features</a>
            <a href="#ecosystem" className="text-sm text-neutral-400 hover:text-white transition">{t('Ecosystem', '生态')}</a>
            <a href="#architecture" className="text-sm text-neutral-400 hover:text-white transition">Architecture</a>
            <a href="#dashboard" className="text-sm text-neutral-400 hover:text-white transition">Dashboard</a>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setLang(lang === 'en' ? 'cn' : 'en')}
              className="text-sm px-3 py-1.5 rounded-md border border-neutral-700 hover:bg-neutral-800 transition">
              {lang === 'en' ? '🇨🇳 中文' : '🇬🇧 EN'}
            </button>
            <a href="https://t.me/EVENexusBot" target="_blank" rel="noopener"
              className="hidden md:inline-flex text-sm px-4 py-2 rounded-md bg-cyan-500 text-black font-medium hover:bg-cyan-400 transition">
              {t('Launch Bot', '启动 Bot')}
            </a>
          </div>
        </nav>
      </header>

      {/* ===== HERO ===== */}
      <section className="relative min-h-[80vh] flex items-center overflow-hidden">
        <Spotlight className="-top-40 left-0 md:left-60 md:-top-20" fill="cyan" />
        <div className="mx-auto max-w-6xl px-4 flex flex-col md:flex-row items-center w-full gap-8 py-20">
          <div className="flex-1 relative z-10">
            <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-cyan-300 to-blue-500">
              NEXUS
            </motion.h1>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="mt-2 text-lg md:text-xl text-cyan-300/80 font-mono tracking-wide">
              Neural EXecutive for Unified Stations
            </motion.p>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
              className="mt-1 text-xl md:text-2xl text-neutral-300">
              {t('Your 24/7 AI Assembly Manager', '你的 24/7 AI 组装体管理器')}
            </motion.p>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="mt-4 text-neutral-400 max-w-lg">
              {t('AI-powered Smart Assembly management for EVE Frontier. Monitor fuel, automate trades, defend your base - with real on-chain data via EVE EYES integration. 24/7.',
                'AI 驱动的 EVE Frontier 智能组装体管理。监控燃料、自动交易、防御基地 - 通过 EVE EYES 集成获取真实链上数据。全天候运行。')}
            </motion.p>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="mt-8 flex gap-4">
              <a href="https://t.me/EVENexusBot" target="_blank" rel="noopener">
                <GlassButton size="default">{t('⚡ Launch Bot', '⚡ 启动 Bot')}</GlassButton>
              </a>
              <a href="https://github.com/CryptoMaN-Kamel/eve-frontier-hackathon" target="_blank" rel="noopener">
                <GlassButton size="default">{t('View on GitHub', '查看 GitHub')}</GlassButton>
              </a>
            </motion.div>
          </div>
          <div className="flex-1 relative h-[400px] md:h-[500px]">
            {/* NEXUS hex logo overlay */}
            <div className="absolute top-1/3 left-1/2 -translate-x-1/2 z-10 opacity-20 pointer-events-none">
              <div className="text-7xl text-cyan-400">⬡</div>
            </div>
            <SplineScene scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode" className="w-full h-full" />
          </div>
        </div>
      </section>

      {/* ===== FEATURES (8-grid) ===== */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">{t('Core Features', '核心功能')}</h2>
          <p className="text-center text-neutral-400 mb-10">{t('Everything you need to manage Smart Assemblies in EVE Frontier', '管理 EVE Frontier 智能组装体所需的一切')}</p>
          <FeaturesWithHoverEffects features={features8} />
        </div>
      </section>

      {/* ===== ECOSYSTEM INTEGRATION ===== */}
      <section id="ecosystem" className="py-20 bg-gradient-to-b from-[#09090b] via-cyan-950/10 to-[#09090b]">
        <FeatureSteps
          features={ecosystemSteps}
          title={t('🌐 Ecosystem Integration - From Wallet to Autopilot', '🌐 生态集成 - 从钱包到自动驾驶')}
          autoPlayInterval={4000}
        />
        {/* Stats bar */}
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 mt-12 px-8">
          {ecosystemStats.map((s, i) => (
            <motion.div key={i} className="text-center" initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <p className="text-3xl md:text-4xl font-bold text-cyan-400">{s.value}</p>
              <p className="text-sm text-neutral-400 mt-1">{s.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ===== ARCHITECTURE (BentoGrid) ===== */}
      <section id="architecture" className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">{t('NEXUS Architecture', 'NEXUS 架构')}</h2>
          <p className="text-center text-neutral-400 mb-10">{t('Built on Sui × EVE Frontier', '构建于 Sui × EVE Frontier')}</p>
          <BentoGrid className="lg:grid-rows-2">
            {archCards.map(c => (
              <BentoCard key={c.name} name={c.name} className={c.className} Icon={c.Icon}
                description={c.description} href={c.href} cta={t('Learn more', '了解更多')}
                background={<div className="absolute inset-0 bg-gradient-to-br from-neutral-900 to-black" />} />
            ))}
          </BentoGrid>
        </div>
      </section>

      {/* ===== VIRAL GROWTH ENGINE ===== */}
      <section className="py-10">
        <CategoryList
          title={t('Viral Growth Engine', '裂变增长引擎')}
          subtitle={t('Grow Your Fleet', '扩展你的舰队')}
          categories={viralCategories}
          headerIcon={<Zap className="w-8 h-8" />}
        />
      </section>

      {/* ===== SECURITY ===== */}
      <Features2
        title={t('Security & Risk Control', '安全与风控')}
        subtitle={t('Move contracts + AI-powered risk management', 'Move 合约 + AI 驱动风险管理')}
        features={securityFeatures}
      />

      {/* ===== DASHBOARD ===== */}
      <section id="dashboard" className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">{t('Assembly Dashboard', '组装体仪表盘')}</h2>
          <p className="text-center text-neutral-400 mb-10">{t('Your EVE Frontier command center', '你的 EVE Frontier 指挥中心')}</p>
          <FinancialDashboard quickActions={dashQuickActions} recentActivity={dashActivity} financialServices={dashServices} />
        </div>
      </section>

      {/* ===== CTA FOOTER ===== */}
      <section className="py-20">
        <div className="max-w-md mx-auto px-4">
          <div className="relative">
            <div className="flex items-center justify-between px-4 py-2 bg-neutral-800/50 border border-neutral-700 rounded-t-lg">
              <div className="flex space-x-2">
                <div className="h-3 w-3 rounded-full bg-red-500" />
                <div className="h-3 w-3 rounded-full bg-yellow-500" />
                <div className="h-3 w-3 rounded-full bg-green-500" />
              </div>
              <button onClick={copyLink} className="text-neutral-400 hover:text-white transition p-1">
                {copied ? <CheckIcon className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
              </button>
            </div>
            <pre className="p-4 rounded-b-lg bg-neutral-900 border-x border-b border-neutral-700 overflow-x-auto font-mono">
              <code className="text-sm text-cyan-400">https://t.me/EVENexusBot</code>
            </pre>
          </div>
          <div className="flex justify-center gap-4 mt-8">
            <a href="https://t.me/EVENexusBot" target="_blank" rel="noopener" className="px-6 py-3 rounded-full bg-cyan-500 text-black font-medium hover:bg-cyan-400 transition">
              {t('Launch Bot', '启动 Bot')}
            </a>
            <a href="https://github.com/CryptoMaN-Kamel/eve-frontier-hackathon" target="_blank" rel="noopener" className="px-6 py-3 rounded-full border border-neutral-700 hover:bg-neutral-800 transition">
              GitHub
            </a>
          </div>
          <p className="text-center text-neutral-600 text-sm mt-12">
            EVE Frontier × Sui Hackathon 2026<br />Built by AI Agents, supervised by humans.<br />© 2026 NEXUS
          </p>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <Footer />
    </div>
  )
}

export default App
