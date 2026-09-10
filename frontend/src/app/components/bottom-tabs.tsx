import React from 'react';
import { NavLink } from 'react-router-dom';
import { visibleNavItems } from '@/app/components/nav-items';
import { useStandalone } from '@/lib/use-standalone';

export const BottomTabs: React.FC = () => {
  const items = visibleNavItems(useStandalone());

  return (
    <nav
      className="fixed bottom-0 inset-x-0 z-40 flex border-t border-gray-200 bg-white
                 pb-[env(safe-area-inset-bottom)]"
      aria-label="Navegação principal"
    >
      {items.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className="flex flex-1 flex-col items-center justify-center gap-1 py-2 min-h-14"
        >
          {({ isActive }) => (
            <>
              <Icon className={`w-5 h-5 ${isActive ? 'text-emerald-600' : 'text-gray-500'}`} />
              <span className={`text-[11px] leading-none ${isActive ? 'text-emerald-600 font-medium' : 'text-gray-500'}`}>
                {label}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
};
