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
import { LucideIcon } from 'lucide-react';
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
	setLang: (lang: 'en' | 'cn') => void;
}

export function Header({ lang, setLang }: HeaderProps) {
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

	const scrollToSection = (id: string) => {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth' });
			setOpen(false);
		}
	};

	const t = {
		en: {
			features: 'Features',
			sniper: 'Sniper',
			architecture: 'Architecture',
			dashboard: 'Dashboard',
			launch: 'Launch Bot',
			github: 'GitHub',
		},
		cn: {
			features: '功能',
			sniper: '狙击',
			architecture: '架构',
			dashboard: '仪表盘',
			launch: '启动机器人',
			github: '开源代码',
		}
	};

	return (
		<header
			className={cn('sticky top-0 z-50 w-full border-b border-transparent', {
				'bg-background/95 supports-[backdrop-filter]:bg-background/50 border-border backdrop-blur-lg':
					scrolled,
			})}
		>
			<nav className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-4">
				<div className="flex items-center gap-5">
					<a href="#" className="hover:bg-accent rounded-md p-2">
						<div className="text-xl font-bold text-foreground">
							Sui DeFi Jarvis
						</div>
					</a>
					<NavigationMenu className="hidden md:flex">
						<NavigationMenuList>
							<NavigationMenuLink className="px-4" asChild>
								<button
									onClick={() => scrollToSection('features')}
									className="hover:bg-accent rounded-md p-2"
								>
									{t[lang].features}
								</button>
							</NavigationMenuLink>
							<NavigationMenuLink className="px-4" asChild>
								<button
									onClick={() => scrollToSection('sniper')}
									className="hover:bg-accent rounded-md p-2"
								>
									{t[lang].sniper}
								</button>
							</NavigationMenuLink>
							<NavigationMenuLink className="px-4" asChild>
								<button
									onClick={() => scrollToSection('architecture')}
									className="hover:bg-accent rounded-md p-2"
								>
									{t[lang].architecture}
								</button>
							</NavigationMenuLink>
							<NavigationMenuLink className="px-4" asChild>
								<button
									onClick={() => scrollToSection('dashboard')}
									className="hover:bg-accent rounded-md p-2"
								>
									{t[lang].dashboard}
								</button>
							</NavigationMenuLink>
						</NavigationMenuList>
					</NavigationMenu>
				</div>
				<div className="hidden items-center gap-2 md:flex">
					<Button
						variant="ghost"
						onClick={() => setLang(lang === 'en' ? 'cn' : 'en')}
						className="text-sm"
					>
						{lang === 'en' ? '🇨🇳' : '🇬🇧'}
					</Button>
					<Button variant="outline" asChild>
						<a href="https://github.com/wrx1234/sui-hackathon" target="_blank" rel="noopener noreferrer">
							{t[lang].github}
						</a>
					</Button>
					<Button asChild>
						<a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener noreferrer">
							{t[lang].launch}
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
				<div className="flex w-full flex-col gap-y-2">
					<button
						onClick={() => scrollToSection('features')}
						className="text-left p-2 hover:bg-accent rounded-md"
					>
						{t[lang].features}
					</button>
					<button
						onClick={() => scrollToSection('sniper')}
						className="text-left p-2 hover:bg-accent rounded-md"
					>
						{t[lang].sniper}
					</button>
					<button
						onClick={() => scrollToSection('architecture')}
						className="text-left p-2 hover:bg-accent rounded-md"
					>
						{t[lang].architecture}
					</button>
					<button
						onClick={() => scrollToSection('dashboard')}
						className="text-left p-2 hover:bg-accent rounded-md"
					>
						{t[lang].dashboard}
					</button>
				</div>
				<div className="flex flex-col gap-2">
					<Button
						variant="ghost"
						onClick={() => setLang(lang === 'en' ? 'cn' : 'en')}
						className="w-full"
					>
						{lang === 'en' ? '🇨🇳 中文' : '🇬🇧 English'}
					</Button>
					<Button variant="outline" className="w-full bg-transparent" asChild>
						<a href="https://github.com/wrx1234/sui-hackathon" target="_blank" rel="noopener noreferrer">
							{t[lang].github}
						</a>
					</Button>
					<Button className="w-full" asChild>
						<a href="https://t.me/SuiJarvisBot" target="_blank" rel="noopener noreferrer">
							{t[lang].launch}
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