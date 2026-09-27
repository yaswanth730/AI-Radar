import React from 'react';
import { NavLink } from 'react-router-dom';
import { Radio, Sparkles, TrendingUp, Bookmark, Rss, Settings } from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { to: '/', label: 'Radar', icon: Radio },
  { to: '/for-you', label: 'For You', icon: Sparkles },
  { to: '/trending', label: 'Trending', icon: TrendingUp },
  { to: '/saved', label: 'Saved', icon: Bookmark },
  { to: '/sources', label: 'Sources', icon: Rss },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export const Navbar: React.FC = () => {
  return (
    <>
      {/* Mobile Bottom Navigation (Fixed) */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 glass-panel border-t border-radar-border px-2 py-1.5 md:hidden">
        <div className="flex items-center justify-around max-w-md mx-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center py-1 px-2.5 rounded-lg text-[10px] font-medium transition-all ${
                  isActive
                    ? 'text-radar-cyan bg-radar-cyan/10 font-bold'
                    : 'text-gray-400 hover:text-gray-200'
                }`
              }
            >
              <Icon className="w-4 h-4 mb-0.5" />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Desktop / Tablet Sub-Header Bar */}
      <div className="hidden md:block w-full bg-radar-surface/90 border-b border-radar-border px-6 py-2 sticky top-[57px] z-30 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex items-center gap-1.5">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-radar-card text-radar-cyan border border-radar-borderGlow shadow-sm font-semibold'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-radar-card/50'
                }`
              }
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </div>
    </>
  );
};
