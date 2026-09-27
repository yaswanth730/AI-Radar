import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchStats } from '../services/api';
import { Radio, RefreshCw } from 'lucide-react';

export const TopHeader: React.FC = () => {
  const { data: stats, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 15000,
  });

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-radar-border px-4 py-3 sm:px-6">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Live Beacon */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-radar-card border border-radar-borderGlow text-radar-cyan">
            <Radio className="w-4 h-4 animate-pulse" />
            <span className="absolute -top-0.5 -right-0.5 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-radar-cyan opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-radar-cyan"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-wider text-sm sm:text-base text-gradient-lime">
                AI RADAR
              </span>
              <span className="px-1.5 py-0.5 text-[10px] uppercase font-mono font-bold tracking-widest rounded bg-radar-cyan/10 text-radar-cyan border border-radar-cyan/30">
                ACTIVE
              </span>
            </div>
            <p className="text-[11px] text-gray-400 font-mono hidden xs:block">
              Continuous Primary Source Intelligence
            </p>
          </div>
        </div>

        {/* Live Telemetry Display */}
        <div className="flex items-center gap-3 sm:gap-6 text-xs font-mono">
          <div className="hidden sm:flex flex-col items-end">
            <span className="text-gray-400 text-[10px]">MONITORED SOURCES</span>
            <span className="text-gray-200 font-semibold">
              {isLoading ? '--' : `${stats?.sources_active || 0} / ${stats?.sources_total || 0}`}
            </span>
          </div>

          <div className="hidden md:flex flex-col items-end">
            <span className="text-gray-400 text-[10px]">SIGNAL POINTS</span>
            <span className="text-radar-cyan font-semibold">
              {isLoading ? '--' : stats?.stories_discovered_total || 0}
            </span>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-radar-card hover:bg-radar-cardHover text-gray-300 hover:text-white border border-radar-border transition-colors text-xs"
            title="Refresh radar telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-radar-cyan' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>
    </header>
  );
};
