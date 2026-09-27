import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchSavedStories, toggleSaveStory } from '../services/api';
import { StoryDetailModal } from '../components/StoryDetailModal';
import type { Story } from '../types';
import { Bookmark, BookmarkX, ExternalLink, RefreshCw } from 'lucide-react';

export const SavedPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: savedStories = [], isLoading, refetch } = useQuery({
    queryKey: ['savedStories'],
    queryFn: fetchSavedStories,
  });

  const saveMutation = useMutation({
    mutationFn: ({ storyId, isSaved }: { storyId: number; isSaved: boolean }) =>
      toggleSaveStory(storyId, isSaved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedStories'] });
      queryClient.invalidateQueries({ queryKey: ['radarStories'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-4 pb-24">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-radar-cyan" />
            <h1 className="text-xl font-bold text-white tracking-tight">Saved Stories</h1>
          </div>
          <p className="text-xs text-gray-400 font-mono mt-0.5">
            Personal intelligence archive ({savedStories.length} bookmarked)
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
      ) : savedStories.length > 0 ? (
        <div className="grid gap-3.5 sm:grid-cols-2">
          {savedStories.map((story) => (
            <div
              key={story.id}
              onClick={() => {
                setSelectedStory(story);
                setIsModalOpen(true);
              }}
              className="glass-card rounded-xl border border-radar-border hover:border-radar-cyan/40 p-4 transition-all hover:-translate-y-0.5 cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-[10px] font-mono mb-2">
                  <span className="px-2 py-0.5 rounded bg-radar-cyan/10 text-radar-cyan border border-radar-cyan/25 uppercase font-semibold">
                    {story.category}
                  </span>
                  <span className="text-gray-400">
                    {story.published_at ? new Date(story.published_at).toLocaleDateString() : 'Recent'}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mb-1.5 leading-snug line-clamp-2">
                  {story.headline || story.title}
                </h3>
                <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed mb-3">
                  {story.summary}
                </p>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500 font-mono pt-2 border-t border-radar-border/60">
                <span className="truncate max-w-[140px] text-gray-300">{story.source_name}</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      saveMutation.mutate({ storyId: story.id, isSaved: true });
                    }}
                    title="Remove from saved"
                    className="p-1.5 rounded-lg bg-radar-card text-gray-400 hover:text-red-400 border border-radar-border transition-colors"
                  >
                    <BookmarkX className="w-3.5 h-3.5" />
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
        <div className="text-center p-12 glass-card rounded-2xl border border-radar-border">
          <Bookmark className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <h4 className="text-base font-bold text-white mb-1">No Saved Stories Yet</h4>
          <p className="text-xs text-gray-400 max-w-sm mx-auto leading-relaxed">
            Bookmark interesting discoveries on the RADAR screen or Feeds by tapping the save button.
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
