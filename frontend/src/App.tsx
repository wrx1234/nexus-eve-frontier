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
  IconArrowsExchange, IconChartLine, IconFish, IconPlant,
  IconTag, IconRobot, IconChartPie, IconLock,
} from '@tabler/icons-react'
import {
  Waves, Anchor, HardDrive, Shield, Brain, ArrowLeftRight,
  Target, TrendingUp, Briefcase, Zap, ShieldCheck, BarChart3,
  Crosshair, ArrowRight, Copy, CheckIcon,
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
    { title: t('Smart Swap', '智能交易'), description: t('Optimal routing across 30+ DEXs via Cetus Aggregator', '通过 Cetus 聚合器跨 30+ DEX 最优路由'), icon: <IconArrowsExchange size={28} /> },
    { title: t('AI Signals', 'AI 信号'), description: t('EMA, RSI, MACD multi-indicator analysis with real-time alerts', 'EMA/RSI/MACD 多指标分析，实时预警'), icon: <IconChartLine size={28} /> },
    { title: t('Whale Tracker', '鲸鱼追踪'), description: t('Monitor large on-chain transactions in real-time', '实时监控链上大额交易动向'), icon: <IconFish size={28} /> },
    { title: t('Pool Discovery', '新池发现'), description: t('First to spot high-yield liquidity pools', '第一时间发现高收益流动性池'), icon: <IconPlant size={28} /> },
    { title: t('Limit Orders', '限价单'), description: t('Set target price, auto-execute when reached', '设定目标价，到价自动执行'), icon: <IconTag size={28} /> },
    { title: t('Strategy Engine', '策略引擎'), description: t('Trend following, mean reversion, arbitrage — fully automated', '趋势跟踪/均值回归/套利——全自动执行'), icon: <IconRobot size={28} /> },
    { title: t('Portfolio', '持仓管理'), description: t('Real-time portfolio tracking with PnL analytics', '实时持仓追踪，盈亏分析'), icon: <IconChartPie size={28} /> },
    { title: t('Vault', '链上金库'), description: t('Move smart contract secured asset management', 'Move 智能合约保障资产安全'), icon: <IconLock size={28} /> },
  ]

  const sniperSteps = [
    { step: t('Monitor', '监控'), title: t('Monitor', '监控'), content: t('Scan Twitter/X 24/7 for Sui ecosystem token discussions. AI identifies relevant tweets from KOLs and traders.', '全天候扫描 Twitter/X 上 Sui 生态代币讨论，AI 识别 KOL 和交易员的相关推文。'), image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800' },
    { step: t('Analyze', '分析'), title: t('Analyze', '分析'), content: t('GPT-4 powered sentiment analysis determines Bullish/Bearish direction with confidence scoring.', 'GPT-4 驱动的情感分析，判断看涨/看跌方向并给出置信度评分。'), image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800' },
    { step: t('Execute', '执行'), title: t('Execute', '执行'), content: t('Auto-execute trades via Cetus DEX when confidence > 70%. Lightning-fast < 3s response.', '置信度 >70% 时通过 Cetus DEX 自动执行交易，闪电般 <3s 响应。'), image: 'https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=800' },
    { step: t('Engage', '互动'), title: t('Engage', '互动'), content: t('Reply to original tweet with trade results + invite link. Free organic exposure → growth flywheel.', '在原推文下回复交易结果 + 邀请链接。免费有机曝光 → 增长飞轮。'), image: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800' },
  ]

  const sniperStats = [
    { value: '12,847', label: t('Tweets Scanned', '推文已扫描') },
    { value: '342', label: t('Signals Found', '信号已发现') },
    { value: '$0', label: t('Marketing Cost', '营销成本') },
    { value: '245K', label: t('Impressions', '曝光量') },
  ]

  const archCards = [
    { name: 'Sui', Icon: Waves, description: t('Layer 1 blockchain with parallel execution and sub-second finality', 'Layer 1 区块链，并行执行，亚秒级确认'), className: 'lg:row-start-1 lg:row-end-3 lg:col-start-1 lg:col-end-2', href: 'https://docs.sui.io/' },
    { name: 'Cetus', Icon: Anchor, description: t('DEX aggregator routing across 30+ protocols for best price', 'DEX 聚合器，跨 30+ 协议寻找最优价格'), className: 'lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2', href: 'https://www.cetus.zone/' },
    { name: 'Walrus', Icon: HardDrive, description: t('Decentralized storage for transparent, immutable operation logs', '去中心化存储，透明不可篡改的操作日志'), className: 'lg:col-start-2 lg:col-end-3 lg:row-start-2 lg:row-end-3', href: 'https://docs.sui.io/' },
    { name: 'Seal', Icon: Shield, description: t('On-chain encryption for secure strategy data storage', '链上加密，安全存储策略数据'), className: 'lg:col-start-3 lg:col-end-4 lg:row-start-1 lg:row-end-2', href: 'https://move-language.github.io/move/' },
    { name: 'OpenClaw', Icon: Brain, description: t('AI runtime powering autonomous agent decision-making', 'AI 运行时，驱动自主 Agent 决策'), className: 'lg:col-start-3 lg:col-end-4 lg:row-start-2 lg:row-end-3', href: 'https://docs.openclaw.ai/' },
  ]

  const stableCategories = [
    { id: 1, title: 'JarvisUSD', subtitle: t('Branded stablecoin: deposit USDC, auto-yield, instant redeem', '品牌稳定币：存入 USDC，自动生息，随时赎回'), icon: <ArrowRight className="w-8 h-8" />, featured: true },
    { id: 2, title: t('Yield Vault', '收益金库'), subtitle: t('Automated yield optimization across Sui DeFi protocols', '跨 Sui DeFi 协议自动收益优化'), icon: <TrendingUp className="w-8 h-8" /> },
    { id: 3, title: t('Risk Shield', '风控盾'), subtitle: t('Multi-layer risk management with real-time monitoring', '多层风控，实时监控'), icon: <ShieldCheck className="w-8 h-8" /> },
  ]

  const securityFeatures = [
    { icon: <HardDrive className="size-6" />, title: t('Walrus Logs', 'Walrus 日志'), description: t('Every trade, every decision — permanently stored on decentralized storage', '每笔交易、每个决策——永久存储在去中心化存储上') },
    { icon: <Shield className="size-6" />, title: t('Move Vault', 'Move 金库'), description: t('Smart contract secured vault with multi-sig and time-lock', 'Move 智能合约金库，多签 + 时间锁保护') },
    { icon: <BarChart3 className="size-6" />, title: t('On-Chain Verifiable', '链上可验证'), description: t('All operations traceable on Sui blockchain explorer', '所有操作可在 Sui 区块链浏览器上追溯验证') },
  ]

  const LogoIcon = ({ letter, bg }: { letter: string; bg: string }) => (
    <div className={`w-9 h-9 flex items-center justify-center rounded-full font-bold text-white text-sm ${bg}`}>{letter}</div>
  )

  const dashQuickActions = [
    { icon: ArrowLeftRight, title: 'Swap', description: t('Trade tokens', '交易代币') },
    { icon: Crosshair, title: 'Sniper', description: t('Social trading', '社交交易') },
    { icon: TrendingUp, title: 'Yield', description: t('Earn returns', '赚取收益') },
    { icon: Briefcase, title: 'Portfolio', description: t('View holdings', '查看持仓') },
  ]
  const dashActivity = [
    { icon: <LogoIcon letter="S" bg="bg-blue-600" />, title: 'SUI → CETUS Swap', time: '2 hours ago', amount: 42.50 },
    { icon: <LogoIcon letter="🎯" bg="bg-purple-600" />, title: 'Social Sniper: @SuiWhale_', time: '4 hours ago', amount: 18.20 },
    { icon: <LogoIcon letter="Y" bg="bg-green-600" />, title: 'Yield Harvest', time: '1 day ago', amount: 3.80 },
  ]
  const dashServices = [
    { icon: Zap, title: t('Auto Strategy', '自动策略'), description: t('AI-managed trading strategies', 'AI 管理交易策略'), isPremium: true },
    { icon: Target, title: 'Social Sniper', description: t('Twitter monitoring & auto-trade', 'Twitter 监控 + 自动交易'), hasAction: true },
    { icon: TrendingUp, title: t('Yield Optimizer', '收益优化'), description: t('Cross-protocol yield farming', '跨协议收益耕作') },
  ]

  const copyLink = () => {
    navigator.clipboard.writeText('https://t.me/SuiJarvisBot')
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="min-h-screen bg-[#09090b] text-white">
      {/* ===== LOADING SCREEN ===== */}
      {loading && (
        <div className={`fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#09090b] transition-opacity duration-500 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
          <svg width="64" height="64" viewBox="0 0 36 44" fill="none" className="mb-8" style={{ animation: 'sui-pulse 1.5s ease-in-out infinite' }}>
            <path d="M15 2.3a2.1 2.1 0 0 1 2.4 0l13.4 9.6c.3.2.4.6.4 1v21.6a1.5 1.5 0 0 1-.4 1.1L17.4 45.3a2.1 2.1 0 0 1-2.4 0L1.6 35.6c-.3-.2-.4-.6-.4-1V13c0-.5.1-.9.4-1.1L15 2.3Z" fill="#4da2ff"/>
          </svg>
          <p className="text-lg font-mono text-neutral-300 mb-6 tracking-wider">Initializing Sui Jarvis...</p>
          <p className="text-xs text-neutral-600 mb-8 tracking-widest">Just A Rather Very Intelligent System on Sui</p>
          <div className="w-64 h-1 bg-neutral-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" style={{ animation: 'loading-bar 2.2s ease-in-out forwards' }} />
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
          <a href="#" className="text-lg font-bold tracking-tight">Sui DeFi Jarvis</a>
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm text-neutral-400 hover:text-white transition">Features</a>
            <a href="#sniper" className="text-sm text-neutral-400 hover:text-white transition">Sniper</a>
            <a href="#architecture" className="text-sm text-neutral-400 hover:text-white transition">Architecture</a>
            <a href="#dashboard" className="text-sm text-neutral-400 hover:text-white transition">Dashboard</a>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setLang(lang === 'en' ? 'cn' : 'en')}
              className="text-sm px-3 py-1.5 rounded-md border border-neutral-700 hover:bg-neutral-800 transition">
              {lang === 'en' ? '🇨🇳 中文' : '🇬🇧 EN'}
            </button>
            <a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener"
              className="hidden md:inline-flex text-sm px-4 py-2 rounded-md bg-white text-black font-medium hover:bg-neutral-200 transition">
              {t('Launch Bot', '启动 Bot')}
            </a>
          </div>
        </nav>
      </header>

      {/* ===== HERO ===== */}
      <section className="relative min-h-[80vh] flex items-center overflow-hidden">
        <Spotlight className="-top-40 left-0 md:left-60 md:-top-20" fill="white" />
        <div className="mx-auto max-w-6xl px-4 flex flex-col md:flex-row items-center w-full gap-8 py-20">
          <div className="flex-1 relative z-10">
            <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400">
              {t('The Infinite Money Glitch', '无限印钞机')}
            </motion.h1>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="mt-2 text-xl md:text-2xl text-neutral-300">
              {t('Your Autonomous AI DeFi Agent on Sui', 'Sui 链上自主 AI DeFi 代理')}
            </motion.p>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="mt-4 text-neutral-400 max-w-lg">
              {t('AI-powered. Fully autonomous. Zero-cost growth. Jarvis monitors, analyzes, trades, and markets — all on autopilot.',
                'AI 驱动、全自动、零成本增长。Jarvis 自动监控、分析、交易、营销——全程自动驾驶。')}
            </motion.p>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="mt-8 flex gap-4">
              <a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener">
                <GlassButton size="default">{t('⚡ Launch Bot', '⚡ 启动 Bot')}</GlassButton>
              </a>
              <a href="https://github.com/wrx1234/sui-hackathon" target="_blank" rel="noopener">
                <GlassButton size="default">{t('View on GitHub', '查看 GitHub')}</GlassButton>
              </a>
            </motion.div>
          </div>
          <div className="flex-1 relative h-[400px] md:h-[500px]">
            {/* Sui logo overlay */}
            <div className="absolute top-1/3 left-1/2 -translate-x-1/2 z-10 opacity-20 pointer-events-none">
              <svg width="48" height="48" viewBox="0 0 784 784" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M579.2 269.1a227 227 0 0 0-53.7-73l-6.8-6.2L408.1 89.4a55.4 55.4 0 0 0-73.2 0L224.3 189.9l-6.8 6.2a227 227 0 0 0-53.7 73A221.2 221.2 0 0 0 145 355.5c0 50.8 17.3 99.3 49 138.6l160.7 199.4a39.4 39.4 0 0 0 61.5 0l160.8-199.4a221 221 0 0 0 49-138.6 221.2 221.2 0 0 0-18.8-86.4h-28Zm-207.7 374c-5.6-7-48.6-61.5-48.6-128.2a48.7 48.7 0 0 1 97.4 0c0 66.7-43 121.2-48.6 128.2h-.2Zm141.2-179.8a177.6 177.6 0 0 1-19.7 36.6l-86.7 107.5c14.8-33.7 23-70 23-103.5a90.8 90.8 0 0 0-181.6 0c0 33.5 8.2 69.8 23 103.5l-86.7-107.5a177.6 177.6 0 0 1-19.7-36.6 178 178 0 0 1-14.9-71.8A180 180 0 0 1 190 277.3l3.8-3.5 3.2-2.9 174.5-157 174.5 157 3.2 2.9 3.8 3.5a180 180 0 0 1 44.6 114.2 178 178 0 0 1-14.9 71.8h-60Z" fill="#a8d4ff"/>
              </svg>
            </div>
            <SplineScene scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode" className="w-full h-full" />
          </div>
        </div>
      </section>

      {/* ===== FEATURES (8-grid) ===== */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">{t('Core Features', '核心功能')}</h2>
          <p className="text-center text-neutral-400 mb-10">{t('Everything you need for autonomous DeFi trading', '自主 DeFi 交易所需的一切')}</p>
          <FeaturesWithHoverEffects features={features8} />
        </div>
      </section>

      {/* ===== SOCIAL SNIPER (highlight!) ===== */}
      <section id="sniper" className="py-20 bg-gradient-to-b from-[#09090b] via-indigo-950/10 to-[#09090b]">
        <FeatureSteps
          features={sniperSteps}
          title={t('🎯 Social Sniper — AI-Powered Growth Engine', '🎯 社交狙击 — AI 驱动增长引擎')}
          autoPlayInterval={4000}
        />
        {/* Stats bar */}
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 mt-12 px-8">
          {sniperStats.map((s, i) => (
            <motion.div key={i} className="text-center" initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <p className="text-3xl md:text-4xl font-bold text-indigo-400">{s.value}</p>
              <p className="text-sm text-neutral-400 mt-1">{s.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ===== ARCHITECTURE (BentoGrid) ===== */}
      <section id="architecture" className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">{t('Tech Stack', '技术架构')}</h2>
          <p className="text-center text-neutral-400 mb-10">{t('Built on the best of Web3', '构建于 Web3 最佳技术栈')}</p>
          <BentoGrid className="lg:grid-rows-2">
            {archCards.map(c => (
              <BentoCard key={c.name} name={c.name} className={c.className} Icon={c.Icon}
                description={c.description} href={c.href} cta={t('Learn more', '了解更多')}
                background={<div className="absolute inset-0 bg-gradient-to-br from-neutral-900 to-black" />} />
            ))}
          </BentoGrid>
        </div>
      </section>

      {/* ===== STABLELAYER ===== */}
      <section className="py-10">
        <CategoryList
          title={t('Integrated with', '深度集成')}
          subtitle="StableLayer"
          categories={stableCategories}
          headerIcon={<Zap className="w-8 h-8" />}
        />
      </section>

      {/* ===== SECURITY ===== */}
      <Features2
        title={t('Security & Transparency', '安全与透明')}
        subtitle={t('Trust through technology', '以技术构建信任')}
        features={securityFeatures}
      />

      {/* ===== DASHBOARD ===== */}
      <section id="dashboard" className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">{t('Live Dashboard', '实时仪表盘')}</h2>
          <p className="text-center text-neutral-400 mb-10">{t('Your DeFi command center', '你的 DeFi 指挥中心')}</p>
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
              <code className="text-sm text-indigo-400">https://t.me/SuiJarvisBot</code>
            </pre>
          </div>
          <div className="flex justify-center gap-4 mt-8">
            <a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener" className="px-6 py-3 rounded-full bg-white text-black font-medium hover:bg-neutral-200 transition">
              {t('Launch Bot', '启动 Bot')}
            </a>
            <a href="https://github.com/wrx1234/sui-hackathon" target="_blank" rel="noopener" className="px-6 py-3 rounded-full border border-neutral-700 hover:bg-neutral-800 transition">
              GitHub
            </a>
          </div>
          <p className="text-center text-neutral-600 text-sm mt-12">
            Built by AI Agents, supervised by humans.<br />© 2026 Sui DeFi Jarvis
          </p>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <Footer />
    </div>
  )
}

export default App
