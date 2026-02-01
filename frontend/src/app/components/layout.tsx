import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/app/components/ui/button';
import { LogOut, Wallet, Home, Users, MessageSquare } from 'lucide-react';

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-3 items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                <Wallet className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Poupix</h1>
                <p className="text-sm text-gray-500">Bem-vindo, {user?.profile?.first_name}!</p>
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="flex items-center justify-center gap-1">
              <NavLink to="/">
                {({ isActive }) => (
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="icon"
                    title="Dashboard"
                  >
                    <Home className="w-5 h-5" />
                  </Button>
                )}
              </NavLink>
              <NavLink to="/actors">
                {({ isActive }) => (
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="icon"
                    title="Atores"
                  >
                    <Users className="w-5 h-5" />
                  </Button>
                )}
              </NavLink>
              <NavLink to="/chat">
                {({ isActive }) => (
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="icon"
                    title="Assistente IA"
                  >
                    <MessageSquare className="w-5 h-5" />
                  </Button>
                )}
              </NavLink>
            </nav>

            <div className="flex justify-end">
              <Button variant="outline" onClick={logout}>
                <LogOut className="w-4 h-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
};
