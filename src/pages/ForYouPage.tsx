import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchForYouStories, toggleSaveStory } from '../services/api';
import { StoryDetailModal } from '../components/StoryDetailModal';
import type { Story } from '../types';
import { Sparkles, Bookmark, ExternalLink, RefreshCw, Layers } from 'lucide-react';

export const ForYouPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const { data: stories = [], isLoading, refetch } = useQuery({
    queryKey: ['forYouStories'],
    queryFn: fetchForYouStories,
  });

  const saveMutation = useMutation({
    mutationFn: ({ storyId, isSaved }: { storyId: number; isSaved: boolean }) =>
      toggleSaveStory(storyId, isSaved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forYouStories'] });
      queryClient.invalidateQueries({ queryKey: ['savedStories'] });
    },
  });

  const categories = ['All', ...Array.from(new Set(stories.map((s) => s.category)))];
  const filteredStories = selectedCategory === 'All'
    ? stories
    : stories.filter((s) => s.category === selectedCategory);

  return (
    <div className="max-w-4xl mx-auto px-4 py-4 pb-24">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-radar-cyan" />
            <h1 className="text-xl font-bold text-white tracking-tight">For You</h1>
          </div>
          <p className="text-xs text-gray-400 font-mono mt-0.5">
            Ranked by learned topic affinity & personal interaction history
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="p-2 rounded-xl bg-radar-card hover:bg-radar-cardHover text-gray-300 hover:text-white border border-radar-border transition-colors text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Category filter pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-4 scrollbar-none">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono whitespace-nowrap transition-all ${
              selectedCategory === cat
                ? 'bg-radar-cyan text-black font-bold shadow-sm'
                : 'bg-radar-card hover:bg-radar-cardHover text-gray-400 border border-radar-border'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Stories Feed */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12">
          <RefreshCw className="w-6 h-6 text-radar-cyan animate-spin" />
        </div>
      ) : filteredStories.length > 0 ? (
        <div className="grid gap-3.5 sm:grid-cols-2">
          {filteredStories.map((story) => (
            <div
              key={story.id}
              onClick={() => {
                setSelectedStory(story);
                setIsModalOpen(true);
              }}
              className="glass-card rounded-xl border border-radar-border hover:border-radar-cyan/30 p-4 transition-all hover:-translate-y-0.5 cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-[10px] font-mono mb-2">
                  <span className="px-2 py-0.5 rounded bg-radar-cyan/10 text-radar-cyan border border-radar-cyan/20 uppercase font-semibold">
                    {story.category}
                  </span>
                  <span className="text-radar-lime font-bold">
                    SIGNAL {Math.round(story.final_score || story.importance_score)}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mb-1.5 leading-snug line-clamp-2">
                  {story.headline || story.title}
                </h3>
                <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed mb-3">
                  {story.summary || 'Summary processing.'}
                </p>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500 font-mono pt-2 border-t border-radar-border/60">
                <span className="truncate max-w-[140px] text-gray-300">{story.source_name}</span>
                <div className="flex items-center gap-2">
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
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center p-8 glass-card rounded-2xl border border-radar-border">
          <Layers className="w-8 h-8 text-gray-500 mx-auto mb-2" />
          <p className="text-sm text-gray-300 font-medium">No personalized recommendations yet</p>
          <p className="text-xs text-gray-500 mt-1">
            Interact with cards on the RADAR screen (swiping right or saving) to train your personal intelligence feed.
          </p>
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
