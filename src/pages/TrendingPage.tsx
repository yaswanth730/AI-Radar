import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchTrendingStories, toggleSaveStory } from '../services/api';
import { StoryDetailModal } from '../components/StoryDetailModal';
import type { Story } from '../types';
import { TrendingUp, Bookmark, ExternalLink, RefreshCw, Flame } from 'lucide-react';

export const TrendingPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: stories = [], isLoading, refetch } = useQuery({
    queryKey: ['trendingStories'],
    queryFn: fetchTrendingStories,
  });

  const saveMutation = useMutation({
    mutationFn: ({ storyId, isSaved }: { storyId: number; isSaved: boolean }) =>
      toggleSaveStory(storyId, isSaved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trendingStories'] });
      queryClient.invalidateQueries({ queryKey: ['savedStories'] });
    },
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-4 pb-24">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-radar-lime" />
            <h1 className="text-xl font-bold text-white tracking-tight">Trending Developments</h1>
          </div>
          <p className="text-xs text-gray-400 font-mono mt-0.5">
            Ranked by cross-source importance and technical signal momentum
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="p-2 rounded-xl bg-radar-card hover:bg-radar-cardHover text-gray-300 hover:text-white border border-radar-border transition-colors text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-12">
          <RefreshCw className="w-6 h-6 text-radar-cyan animate-spin" />
        </div>
      ) : stories.length > 0 ? (
        <div className="space-y-3">
          {stories.map((story, idx) => (
            <div
              key={story.id}
              onClick={() => {
                setSelectedStory(story);
                setIsModalOpen(true);
              }}
              className="glass-card rounded-xl border border-radar-border hover:border-radar-lime/40 p-4 transition-all hover:bg-radar-cardHover/50 cursor-pointer flex items-start gap-3.5"
            >
              {/* Rank Index Badge */}
              <div className="flex flex-col items-center justify-center min-w-[32px] pt-1">
                <span className={`text-sm font-mono font-extrabold ${idx < 3 ? 'text-radar-lime' : 'text-gray-500'}`}>
                  #{idx + 1}
                </span>
                {idx < 3 && <Flame className="w-3.5 h-3.5 text-radar-lime mt-0.5" />}
              </div>

              {/* Story Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 text-[10px] font-mono mb-1">
                  <span className="px-2 py-0.5 rounded bg-radar-cyan/10 text-radar-cyan border border-radar-cyan/25 uppercase font-semibold">
                    {story.category}
                  </span>
                  <span className="text-gray-400">•</span>
                  <span className="text-gray-300 truncate">{story.source_name}</span>
                  <span className="ml-auto text-radar-lime font-bold">
                    SIGNAL {Math.round(story.final_score || story.importance_score)}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mb-1 leading-snug">
                  {story.headline || story.title}
                </h3>
                <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">
                  {story.summary}
                </p>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-col items-center gap-1.5 pt-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    saveMutation.mutate({ storyId: story.id, isSaved: story.is_saved });
                  }}
                  className={`p-1.5 rounded-lg border text-xs transition-colors ${
                    story.is_saved
                      ? 'bg-radar-cyan/15 text-radar-cyan border-radar-cyan/30'
                      : 'bg-radar-card text-gray-400 hover:text-white border-radar-border'
                  }`}
                >
                  <Bookmark className={`w-3.5 h-3.5 ${story.is_saved ? 'fill-radar-cyan' : ''}`} />
                </button>
                <a
                  href={story.canonical_url || story.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 rounded-lg bg-radar-card text-gray-400 hover:text-white border border-radar-border"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center p-8 glass-card rounded-2xl border border-radar-border">
          <p className="text-sm text-gray-300">No trending AI signals currently registered.</p>
        </div>
      )}

      <StoryDetailModal
        story={selectedStory}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onToggleSave={(id, saved) => saveMutation.mutate({ storyId: id, isSaved: saved })}
      />
    </div>
  );
};
