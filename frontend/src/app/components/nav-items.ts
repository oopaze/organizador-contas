import { Home, Users, MessageSquare, Brain, Plug, HandCoins } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  /** Telas de AI/MCP: somem do app instalado, seguem acessíveis pelo navegador. */
  hideWhenInstalled?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Início', icon: Home },
  { to: '/loans', label: 'Empréstimos', icon: HandCoins },
  { to: '/actors', label: 'Atores', icon: Users },
  { to: '/chat', label: 'Assistente IA', icon: MessageSquare, hideWhenInstalled: true },
  { to: '/integrations', label: 'Integrações', icon: Plug, hideWhenInstalled: true },
  { to: '/ai-insights', label: 'AI Insights', icon: Brain, hideWhenInstalled: true },
];

export function visibleNavItems(standalone: boolean): NavItem[] {
  return standalone ? NAV_ITEMS.filter((i) => !i.hideWhenInstalled) : [...NAV_ITEMS];
}
