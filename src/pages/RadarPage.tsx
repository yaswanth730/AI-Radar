import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchRadarStories, recordInteraction, toggleSaveStory, fetchStats } from '../services/api';
import { RadarCanvas } from '../components/RadarCanvas';
import { StoryCard } from '../components/StoryCard';
import { StoryDetailModal } from '../components/StoryDetailModal';
import type { Story } from '../types';
import { ThumbsUp, X, Sparkles, RefreshCw, BookmarkCheck } from 'lucide-react';

export const RadarPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: stories = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['radarStories'],
    queryFn: fetchRadarStories,
    staleTime: 60000,
  });

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
  });

  const interactionMutation = useMutation({
    mutationFn: ({ storyId, type }: { storyId: number; type: string }) =>
      recordInteraction(storyId, type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forYouStories'] });
    },
  });

  const saveMutation = useMutation({
    mutationFn: ({ storyId, isSaved }: { storyId: number; isSaved: boolean }) =>
      toggleSaveStory(storyId, isSaved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['radarStories'] });
      queryClient.invalidateQueries({ queryKey: ['savedStories'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const activeStories = stories.slice(currentIndex);
  const currentStory = activeStories[0];

  const handleSwipeRight = () => {
    if (!currentStory) return;
    interactionMutation.mutate({ storyId: currentStory.id, type: 'swipe_right' });
    setCurrentIndex((prev) => prev + 1);
  };

  const handleSwipeLeft = () => {
    if (!currentStory) return;
    interactionMutation.mutate({ storyId: currentStory.id, type: 'swipe_left' });
    setCurrentIndex((prev) => prev + 1);
  };

  const handleToggleSave = (storyId: number, currentlySaved: boolean) => {
    saveMutation.mutate({ storyId, isSaved: currentlySaved });
    if (selectedStory && selectedStory.id === storyId) {
      setSelectedStory({ ...selectedStory, is_saved: !currentlySaved });
    }
  };

  const handleOpenDetail = (story: Story) => {
    setSelectedStory(story);
    setIsModalOpen(true);
    interactionMutation.mutate({ storyId: story.id, type: 'detail_view' });
  };

  // Compute last scan text
  let lastScanText = '10m ago';
  if (stats?.last_scan_time) {
    const diffMins = Math.max(1, Math.round((Date.now() - new Date(stats.last_scan_time).getTime()) / 60000));
    lastScanText = `${diffMins}m ago`;
  }

  return (
    <div className="flex flex-col items-center justify-start min-h-[calc(100vh-140px)] px-4 py-2 pb-24">
      {/* Radar Animation & Telemetry Header */}
      <RadarCanvas
        sourcesCount={stats?.sources_active || 0}
        lastScanText={lastScanText}
        signalPoints={stats?.stories_discovered_total || 0}
      />

      {/* Discovery Stack Container */}
      <div className="relative w-full max-w-md h-[430px] flex items-center justify-center mt-1">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center text-center p-8 glass-card rounded-2xl border border-radar-border">
            <RefreshCw className="w-8 h-8 text-radar-cyan animate-spin mb-3" />
            <p className="text-sm font-mono text-gray-300">Synchronizing Radar Frequencies...</p>
            <p className="text-xs text-gray-500 mt-1">Collecting primary AI signals</p>
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center justify-center text-center p-8 glass-card rounded-2xl border border-radar-red/30">
            <p className="text-sm text-red-400 font-semibold mb-2">Radar Signal Interrupted</p>
            <p className="text-xs text-gray-400 mb-4">Could not retrieve discovery stories.</p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 rounded-xl bg-radar-card border border-radar-border text-xs text-white hover:bg-radar-cardHover"
            >
              Re-scan Frequencies
            </button>
          </div>
        ) : activeStories.length > 0 ? (
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Background card peek (if more stories exist) */}
            {activeStories[1] && (
              <StoryCard
                story={activeStories[1]}
                isFront={false}
                onSwipeRight={() => {}}
                onSwipeLeft={() => {}}
                onToggleSave={() => {}}
                onOpenDetail={() => {}}
              />
            )}
            {/* Front swipeable active card */}
            <StoryCard
              key={currentStory.id}
              story={currentStory}
              isFront={true}
              onSwipeRight={handleSwipeRight}
              onSwipeLeft={handleSwipeLeft}
              onToggleSave={handleToggleSave}
              onOpenDetail={handleOpenDetail}
            />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center p-8 glass-card rounded-2xl border border-radar-border max-w-sm">
            <Sparkles className="w-10 h-10 text-radar-cyan mb-3 opacity-80" />
            <h4 className="text-base font-bold text-white mb-1">Radar Horizon Clear</h4>
            <p className="text-xs text-gray-400 mb-5 leading-relaxed">
              You've reviewed all recent signals discovered in the current cycle. New primary developments are collected automatically every 10 minutes.
            </p>
            <button
              onClick={() => {
                setCurrentIndex(0);
                refetch();
              }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-radar-cyan/15 hover:bg-radar-cyan/25 text-radar-cyan border border-radar-cyan/30 text-xs font-semibold transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Review Earlier Stories</span>
            </button>
          </div>
        )}
      </div>

      {/* Mobile Explicit Swipe Buttons & Keyboard Prompts */}
      {currentStory && (
        <div className="flex items-center justify-center gap-6 mt-4">
          <button
            onClick={handleSwipeLeft}
            className="flex items-center justify-center w-12 h-12 rounded-full glass-panel border border-red-500/30 text-red-400 hover:bg-red-500/10 hover:border-red-500 transition-all shadow-lg active:scale-95"
            title="Skip (Left Swipe / A)"
          >
            <X className="w-5 h-5" />
          </button>

          <button
            onClick={() => handleToggleSave(currentStory.id, currentStory.is_saved)}
            className={`flex items-center justify-center w-10 h-10 rounded-full glass-panel border transition-all active:scale-95 ${
              currentStory.is_saved
                ? 'border-radar-cyan/50 text-radar-cyan bg-radar-cyan/15 shadow-[0_0_15px_rgba(0,255,163,0.3)]'
                : 'border-radar-border text-gray-400 hover:text-white'
            }`}
            title="Save / Bookmark (B)"
          >
            <BookmarkCheck className="w-4 h-4" />
          </button>

          <button
            onClick={handleSwipeRight}
            className="flex items-center justify-center w-12 h-12 rounded-full glass-panel border border-radar-cyan/30 text-radar-cyan hover:bg-radar-cyan/10 hover:border-radar-cyan transition-all shadow-lg active:scale-95"
            title="Interested (Right Swipe / D)"
          >
            <ThumbsUp className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Story Detail Slide-Over Modal */}
      <StoryDetailModal
        story={selectedStory}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onToggleSave={handleToggleSave}
      />
    </div>
  );
};
