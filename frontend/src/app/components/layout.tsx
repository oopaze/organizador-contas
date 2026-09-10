import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/app/components/ui/button';
import { LogOut, Wallet } from 'lucide-react';
import { visibleNavItems } from '@/app/components/nav-items';
import { useStandalone } from '@/lib/use-standalone';
import { BottomTabs } from '@/app/components/bottom-tabs';

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const standalone = useStandalone();
  const navItems = visibleNavItems(standalone);

  return (
    <div className="min-h-screen bg-gray-50 overflow-x-clip">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 pt-[env(safe-area-inset-top)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4 sm:grid sm:grid-cols-[1fr_auto_1fr]">
            {/* Logo and Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center shrink-0">
                <Wallet className="w-6 h-6 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-semibold text-gray-900">Poupix</h1>
                <p className="text-sm text-gray-500">Bem-vindo, {user?.profile?.first_name}!</p>
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="hidden items-center gap-1 sm:flex sm:order-2 sm:w-auto justify-center sm:justify-self-center">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink key={to} to={to}>
                  {({ isActive }) => (
                    <Button
                      variant={isActive ? 'secondary' : 'ghost'}
                      size="icon"
                      title={label}
                      aria-label={label}
                    >
                      <Icon className="w-5 h-5" />
                    </Button>
                  )}
                </NavLink>
              ))}
            </nav>

            {/* Logout Button */}
            <div className="flex order-2 sm:order-3 sm:justify-self-end">
              <Button variant="outline" size="icon" onClick={logout} className="sm:hidden" title="Sair">
                <LogOut className="w-4 h-4" />
              </Button>
              <Button variant="outline" onClick={logout} className="hidden sm:flex">
                <LogOut className="w-4 h-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-w-0 overflow-x-clip
                       pb-[calc(3.5rem+env(safe-area-inset-bottom)+2rem)] sm:pb-8">
        <Outlet />
      </main>

      <BottomTabs />
    </div>
  );
};
