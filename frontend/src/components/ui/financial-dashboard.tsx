import * as React from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, History, Library, Search } from 'lucide-react';
import { cn } from '@/lib/utils';

type QuickAction = { icon: React.ElementType; title: string; description: string };
type Activity = { icon: React.ReactNode; title: string; time: string; amount: number };
type Service = { icon: React.ElementType; title: string; description: string; isPremium?: boolean; hasAction?: boolean };

interface FinancialDashboardProps {
  quickActions: QuickAction[]; recentActivity: Activity[]; financialServices: Service[];
}

const IconWrapper = ({ icon: Icon, className }: { icon: React.ElementType; className?: string }) => (
  <div className={cn('p-2 rounded-full flex items-center justify-center', className)}><Icon className="w-5 h-5" /></div>
);

const containerVariants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { staggerChildren: 0.1 } } };
const itemVariants = { hidden: { opacity: 0, y: 15 }, visible: { opacity: 1, y: 0 } };

export const FinancialDashboard: React.FC<FinancialDashboardProps> = ({ quickActions, recentActivity, financialServices }) => (
  <motion.div initial="hidden" animate="visible" variants={containerVariants}
    className="bg-neutral-950 text-white rounded-2xl border border-neutral-800 shadow-sm max-w-2xl mx-auto font-sans"
  >
    <div className="p-4 md:p-6">
      <motion.div variants={itemVariants} className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500" />
        <input type="text" placeholder="Search transactions, or type a command..."
          className="bg-neutral-900 w-full border border-neutral-800 rounded-lg pl-10 pr-4 py-2.5 text-sm outline-none focus:border-neutral-600" />
        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center text-xs font-mono text-neutral-500 bg-neutral-800 p-1 rounded-md">⌘K</kbd>
      </motion.div>
      <motion.div variants={containerVariants} className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {quickActions.map((a, i) => (
          <motion.div key={i} variants={itemVariants} whileHover={{ scale: 1.05 }}
            className="group text-center p-3 rounded-xl cursor-pointer transition-colors hover:bg-neutral-800">
            <IconWrapper icon={a.icon} className="mx-auto mb-2 bg-neutral-800 group-hover:bg-neutral-700" />
            <p className="text-sm font-medium">{a.title}</p>
            <p className="text-xs text-neutral-500">{a.description}</p>
          </motion.div>
        ))}
      </motion.div>
      <motion.div variants={itemVariants} className="mb-6">
        <div className="flex items-center gap-2 mb-4"><History className="w-5 h-5 text-neutral-500" /><h2 className="text-sm font-semibold">Recent activity</h2></div>
        <motion.ul variants={containerVariants} className="space-y-4">
          {recentActivity.map((a, i) => (
            <motion.li key={i} variants={itemVariants} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {React.isValidElement(a.icon) ? a.icon : <IconWrapper icon={a.icon as React.ElementType} className="bg-neutral-800 text-neutral-400" />}
                <div><p className="font-medium text-sm">{a.title}</p><p className="text-xs text-neutral-500">{a.time}</p></div>
              </div>
              <div className={cn('text-sm font-mono p-1 px-2 rounded',
                a.amount > 0 ? 'text-green-400 bg-green-500/10' : 'text-red-400 bg-red-500/10'
              )}>{a.amount > 0 ? '+' : '-'}${Math.abs(a.amount).toFixed(2)}</div>
            </motion.li>
          ))}
        </motion.ul>
      </motion.div>
      <motion.div variants={itemVariants}>
        <div className="flex items-center gap-2 mb-4"><Library className="w-5 h-5 text-neutral-500" /><h2 className="text-sm font-semibold">Services</h2></div>
        <motion.div variants={containerVariants} className="space-y-2">
          {financialServices.map((s, i) => (
            <motion.div key={i} variants={itemVariants} whileHover={{ scale: 1.02 }}
              className="flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all hover:bg-neutral-800">
              <div className="flex items-center gap-3">
                <IconWrapper icon={s.icon} className="bg-neutral-800" />
                <div>
                  <p className="font-medium text-sm flex items-center gap-2">
                    {s.title}
                    {s.isPremium && <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full">Premium</span>}
                  </p>
                  <p className="text-xs text-neutral-500">{s.description}</p>
                </div>
              </div>
              {s.hasAction && <ChevronRight className="w-5 h-5 text-neutral-500" />}
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  </motion.div>
);
