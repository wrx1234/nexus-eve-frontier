import React from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { MenuToggleIcon } from '@/components/ui/menu-toggle-icon';
import { createPortal } from 'react-dom';
import {
	NavigationMenu,
	NavigationMenuContent,
	NavigationMenuItem,
	NavigationMenuLink,
	NavigationMenuList,
	NavigationMenuTrigger,
} from '@/components/ui/navigation-menu';
import { type LucideIcon } from 'lucide-react';
import {
	CodeIcon,
	GlobeIcon,
	LayersIcon,
	UserPlusIcon,
	Users,
	Star,
	FileText,
	Shield,
	RotateCcw,
	Handshake,
	Leaf,
	HelpCircle,
	BarChart,
	PlugIcon,
} from 'lucide-react';

type LinkItem = {
	title: string;
	href: string;
	icon: LucideIcon;
	description?: string;
};

interface HeaderProps {
	lang: 'en' | 'cn';
	onLangChange: (lang: 'en' | 'cn') => void;
}

export function Header({ lang, onLangChange }: HeaderProps) {
	const [open, setOpen] = React.useState(false);
	const scrolled = useScroll(10);

	React.useEffect(() => {
		if (open) {
			document.body.style.overflow = 'hidden';
		} else {
			document.body.style.overflow = '';
		}
		return () => {
			document.body.style.overflow = '';
		};
	}, [open]);

	const navItems = [
		{ href: '#features', label: lang === 'en' ? 'Features' : '功能' },
		{ href: '#sniper', label: lang === 'en' ? 'Sniper' : '狙击' },
		{ href: '#architecture', label: lang === 'en' ? 'Architecture' : '架构' },
		{ href: '#dashboard', label: lang === 'en' ? 'Dashboard' : '仪表盘' },
	];

	return (
		<header
			className={cn('sticky top-0 z-50 w-full border-b border-transparent', {
				'bg-background/95 supports-[backdrop-filter]:bg-background/50 border-border backdrop-blur-lg':
					scrolled,
			})}
		>
			<nav className="mx-auto flex h-14 w-full max-w-7xl items-center justify-between px-4">
				<div className="flex items-center gap-5">
					<a href="#" className="hover:bg-accent rounded-md p-2">
						<span className="text-xl font-bold bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">
							Sui DeFi Jarvis
						</span>
					</a>
					<NavigationMenu className="hidden md:flex">
						<NavigationMenuList>
							{navItems.map((item) => (
								<NavigationMenuItem key={item.href}>
									<NavigationMenuLink className="px-4" asChild>
										<a href={item.href} className="hover:bg-accent rounded-md p-2">
											{item.label}
										</a>
									</NavigationMenuLink>
								</NavigationMenuItem>
							))}
						</NavigationMenuList>
					</NavigationMenu>
				</div>
				<div className="hidden items-center gap-2 md:flex">
					<Button 
						variant="ghost" 
						size="sm" 
						onClick={() => onLangChange(lang === 'en' ? 'cn' : 'en')}
						className="px-2"
					>
						{lang === 'en' ? '🇨🇳' : '🇬🇧'}
					</Button>
					<Button variant="outline" asChild>
						<a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener noreferrer">
							{lang === 'en' ? 'Launch Bot' : '启动 Bot'}
						</a>
					</Button>
					<Button asChild>
						<a href="https://github.com/wrx1234/sui-hackathon" target="_blank" rel="noopener noreferrer">
							GitHub
						</a>
					</Button>
				</div>
				<Button
					size="icon"
					variant="outline"
					onClick={() => setOpen(!open)}
					className="md:hidden"
					aria-expanded={open}
					aria-controls="mobile-menu"
					aria-label="Toggle menu"
				>
					<MenuToggleIcon open={open} className="size-5" duration={300} />
				</Button>
			</nav>
			<MobileMenu open={open} className="flex flex-col justify-between gap-2 overflow-y-auto">
				<NavigationMenu className="max-w-full">
					<div className="flex w-full flex-col gap-y-2">
						{navItems.map((item) => (
							<a
								key={item.href}
								href={item.href}
								className="block px-4 py-2 text-sm font-medium hover:bg-accent rounded-md"
								onClick={() => setOpen(false)}
							>
								{item.label}
							</a>
						))}
					</div>
				</NavigationMenu>
				<div className="flex flex-col gap-2">
					<Button 
						variant="ghost" 
						className="w-full" 
						onClick={() => onLangChange(lang === 'en' ? 'cn' : 'en')}
					>
						{lang === 'en' ? '🇨🇳 中文' : '🇬🇧 English'}
					</Button>
					<Button variant="outline" className="w-full bg-transparent" asChild>
						<a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener noreferrer">
							{lang === 'en' ? 'Launch Bot' : '启动 Bot'}
						</a>
					</Button>
					<Button className="w-full" asChild>
						<a href="https://github.com/wrx1234/sui-hackathon" target="_blank" rel="noopener noreferrer">
							GitHub
						</a>
					</Button>
				</div>
			</MobileMenu>
		</header>
	);
}

type MobileMenuProps = React.ComponentProps<'div'> & {
	open: boolean;
};

function MobileMenu({ open, children, className, ...props }: MobileMenuProps) {
	if (!open || typeof window === 'undefined') return null;

	return createPortal(
		<div
			id="mobile-menu"
			className={cn(
				'bg-background/95 supports-[backdrop-filter]:bg-background/50 backdrop-blur-lg',
				'fixed top-14 right-0 bottom-0 left-0 z-40 flex flex-col overflow-hidden border-y md:hidden',
			)}
		>
			<div
				data-slot={open ? 'open' : 'closed'}
				className={cn(
					'data-[slot=open]:animate-in data-[slot=open]:zoom-in-97 ease-out',
					'size-full p-4',
					className,
				)}
				{...props}
			>
				{children}
			</div>
		</div>,
		document.body,
	);
}

function useScroll(threshold: number) {
	const [scrolled, setScrolled] = React.useState(false);

	const onScroll = React.useCallback(() => {
		setScrolled(window.scrollY > threshold);
	}, [threshold]);

	React.useEffect(() => {
		window.addEventListener('scroll', onScroll);
		return () => window.removeEventListener('scroll', onScroll);
	}, [onScroll]);

	// also check on first load
	React.useEffect(() => {
		onScroll();
	}, [onScroll]);

	return scrolled;
}