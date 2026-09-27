import React from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import type { Story } from '../types';
import { Bookmark, ExternalLink, Sparkles, Check, X } from 'lucide-react';

interface StoryCardProps {
  story: Story;
  isFront: boolean;
  onSwipeRight: () => void;
  onSwipeLeft: () => void;
  onToggleSave: (storyId: number, currentlySaved: boolean) => void;
  onOpenDetail: (story: Story) => void;
}

export const StoryCard: React.FC<StoryCardProps> = ({
  story,
  isFront,
  onSwipeRight,
  onSwipeLeft,
  onToggleSave,
  onOpenDetail,
}) => {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-250, 250], [-18, 18]);
  const opacity = useTransform(x, [-250, -150, 0, 150, 250], [0.4, 0.9, 1, 0.9, 0.4]);
  
  // Feedback badge opacity transforms
  const likeOpacity = useTransform(x, [50, 150], [0, 1]);
  const skipOpacity = useTransform(x, [-150, -50], [1, 0]);

  const handleDragEnd = (_: any, info: any) => {
    if (info.offset.x > 100 || info.velocity.x > 500) {
      onSwipeRight();
    } else if (info.offset.x < -100 || info.velocity.x < -500) {
      onSwipeLeft();
    }
  };

  return (
    <motion.div
      style={isFront ? { x, rotate, opacity } : { scale: 0.95, y: 12, opacity: 0.7 }}
      drag={isFront ? 'x' : false}
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      whileDrag={{ cursor: 'grabbing' }}
      className={`absolute w-full max-w-md glass-card rounded-2xl border border-radar-border p-5 sm:p-6 select-none transition-shadow ${
        isFront ? 'cursor-grab shadow-2xl hover:border-radar-cyan/30' : 'pointer-events-none'
      }`}
    >
      {/* Swipe Feedback Badges */}
      {isFront && (
        <>
          <motion.div
            style={{ opacity: likeOpacity }}
            className="absolute top-4 right-4 z-20 flex items-center gap-1.5 px-3 py-1 rounded-full bg-radar-cyan/20 border border-radar-cyan text-radar-cyan text-xs font-mono font-bold tracking-widest uppercase shadow-lg"
          >
            <Check className="w-4 h-4" />
            <span>INTERESTED</span>
          </motion.div>

          <motion.div
            style={{ opacity: skipOpacity }}
            className="absolute top-4 left-4 z-20 flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/20 border border-red-500 text-red-400 text-xs font-mono font-bold tracking-widest uppercase shadow-lg"
          >
            <X className="w-4 h-4" />
            <span>SKIP</span>
          </motion.div>
        </>
      )}

      {/* Card Header: Category & Signal Badge */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <span className="px-2.5 py-0.5 text-[11px] font-mono font-bold uppercase tracking-wider rounded-md bg-radar-cyan/10 text-radar-cyan border border-radar-cyan/25">
          {story.category}
        </span>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-radar-card text-radar-lime border border-radar-border">
            SIGNAL {Math.round(story.final_score || story.importance_score)}
          </span>
          {story.is_breaking && (
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-radar-red/20 text-radar-red border border-radar-red/40 animate-pulse">
              HOT
            </span>
          )}
        </div>
      </div>

      {/* Headline & Tap Trigger for Details */}
      <div onClick={() => onOpenDetail(story)} className="cursor-pointer group">
        <h3 className="text-base sm:text-lg font-bold text-white mb-2 leading-snug group-hover:text-radar-cyan transition-colors">
          {story.headline || story.title}
        </h3>

        {/* Short Summary (1-3 sentences) */}
        <p className="text-xs sm:text-sm text-gray-300 line-clamp-3 mb-3 leading-relaxed">
          {story.summary || 'Summary processing by AI classifier pipeline.'}
        </p>

        {/* Why it matters callout */}
        <div className="rounded-xl bg-radar-surface/80 border border-radar-border/80 p-3 mb-4">
          <div className="flex items-center gap-1 text-[10px] font-mono font-bold uppercase tracking-wider text-radar-lime mb-1">
            <Sparkles className="w-3 h-3" />
            <span>Why It Matters</span>
          </div>
          <p className="text-xs text-gray-200 italic line-clamp-2">
            "{story.why_it_matters || 'Notable shift in AI capabilities and architectural tooling.'}"
          </p>
        </div>
      </div>

      {/* Metadata Footer */}
      <div className="flex items-center justify-between text-xs text-gray-400 font-mono mb-4 pt-2 border-t border-radar-border/60">
        <span className="truncate max-w-[160px] text-gray-300 font-medium">
          {story.source_name}
        </span>
        <span>
          {story.published_at ? new Date(story.published_at).toLocaleDateString() : 'Recent'}
        </span>
      </div>

      {/* Action Controls */}
      <div className="flex items-center justify-between gap-2 pt-1">
        <button
          onClick={() => onToggleSave(story.id, story.is_saved)}
          className={`flex items-center gap-1.5 py-2 px-3 rounded-xl border text-xs font-medium transition-all ${
            story.is_saved
              ? 'bg-radar-cyan/15 text-radar-cyan border-radar-cyan/40 shadow-sm'
              : 'bg-radar-card hover:bg-radar-cardHover text-gray-300 border-radar-border'
          }`}
          title="Save / Bookmark"
        >
          <Bookmark className={`w-3.5 h-3.5 ${story.is_saved ? 'fill-radar-cyan' : ''}`} />
          <span>{story.is_saved ? 'Saved' : 'Save'}</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onOpenDetail(story)}
            className="py-2 px-3 rounded-xl bg-radar-card hover:bg-radar-cardHover text-gray-300 hover:text-white border border-radar-border text-xs font-medium transition-colors"
          >
            Details
          </button>
          
          <a
            href={story.canonical_url || story.original_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1.5 py-2 px-3 rounded-xl bg-radar-cyan/10 hover:bg-radar-cyan/20 text-radar-cyan border border-radar-cyan/30 text-xs font-medium transition-colors"
            title="Open original publication"
          >
            <span>Source</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </motion.div>
  );
};
