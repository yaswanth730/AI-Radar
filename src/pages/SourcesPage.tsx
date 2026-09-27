import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchSources, fetchStats, triggerManualScan } from '../services/api';
import { Rss, CheckCircle2, AlertTriangle, ExternalLink, RefreshCw, Zap } from 'lucide-react';

export const SourcesPage: React.FC = () => {
  const { data: sources = [], isLoading, refetch, isFetching } = useQuery({
    queryKey: ['sources'],
    queryFn: fetchSources,
  });

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
  });

  const handleScanNow = async () => {
    await triggerManualScan();
    refetch();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-4 pb-24">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2">
            <Rss className="w-5 h-5 text-radar-cyan" />
            <h1 className="text-xl font-bold text-white tracking-tight">Intelligence Sources</h1>
          </div>
          <p className="text-xs text-gray-400 font-mono mt-0.5">
            Monitored primary blogs, feeds, GitHub releases and research papers
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-radar-card hover:bg-radar-cardHover text-gray-300 hover:text-white border border-radar-border transition-colors text-xs font-mono"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-radar-cyan' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleScanNow}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-radar-cyan hover:bg-radar-cyan/90 text-black font-semibold text-xs transition-all shadow-md active:scale-95"
          >
            <Zap className="w-3.5 h-3.5 fill-black" />
            <span>Scan Now</span>
          </button>
        </div>
      </div>

      {/* Stats Summary Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-5 font-mono text-center">
        <div className="p-3 rounded-xl bg-radar-card border border-radar-border">
          <div className="text-[10px] text-gray-400">CONFIGURED</div>
          <div className="text-lg font-bold text-white">{sources.length}</div>
        </div>
        <div className="p-3 rounded-xl bg-radar-card border border-radar-border">
          <div className="text-[10px] text-gray-400">ACTIVE CHANNELS</div>
          <div className="text-lg font-bold text-radar-cyan">
            {sources.filter((s) => s.status === 'active').length}
          </div>
        </div>
        <div className="p-3 rounded-xl bg-radar-card border border-radar-border">
          <div className="text-[10px] text-gray-400">STORIES INDEXED</div>
          <div className="text-lg font-bold text-radar-lime">
            {stats?.stories_discovered_total || 0}
          </div>
        </div>
        <div className="p-3 rounded-xl bg-radar-card border border-radar-border">
          <div className="text-[10px] text-gray-400">FAILURES</div>
          <div className="text-lg font-bold text-radar-amber">
            {sources.filter((s) => s.last_failure_at).length}
          </div>
        </div>
      </div>

      {/* Sources List */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12">
          <RefreshCw className="w-6 h-6 text-radar-cyan animate-spin" />
        </div>
      ) : sources.length > 0 ? (
        <div className="space-y-3">
          {sources.map((src) => (
            <div
              key={src.id}
              className="glass-card rounded-xl border border-radar-border p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-sm text-white truncate">{src.name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-radar-card text-radar-cyan border border-radar-border uppercase">
                    {src.type}
                  </span>
                  <span className={`flex items-center gap-1 text-[10px] font-mono ${
                    src.status === 'active' ? 'text-radar-cyan' : 'text-gray-500'
                  }`}>
                    {src.status === 'active' ? (
                      <CheckCircle2 className="w-3 h-3" />
                    ) : (
                      <AlertTriangle className="w-3 h-3 text-radar-amber" />
                    )}
                    {src.status.toUpperCase()}
                  </span>
                </div>

                <div className="text-xs text-gray-400 font-mono truncate max-w-md">
                  {src.url}
                </div>
              </div>

              {/* Source Telemetry Details */}
              <div className="flex items-center gap-4 text-xs font-mono text-gray-400 self-end sm:self-center">
                <div className="text-right">
                  <div className="text-[10px] text-gray-500">COLLECTED</div>
                  <div className="font-bold text-gray-200">{src.stories_discovered_count}</div>
                </div>

                <div className="text-right hidden sm:block">
                  <div className="text-[10px] text-gray-500">LAST SCAN</div>
                  <div className="text-gray-300">
                    {src.last_successful_scan
                      ? new Date(src.last_successful_scan).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                      : 'Pending'}
                  </div>
                </div>

                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-xl bg-radar-card hover:bg-radar-cardHover text-gray-400 hover:text-white border border-radar-border transition-colors"
                  title="Open source feed URL"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center p-8 glass-card rounded-2xl border border-radar-border">
          <p className="text-sm text-gray-300">No sources configured yet. Default sources will be seeded during scan cycles.</p>
        </div>
      )}
    </div>
  );
};
