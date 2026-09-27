import React from 'react';
import type { Story } from '../types';
import { X, ExternalLink, Bookmark, Sparkles, Building, Code2, Tag } from 'lucide-react';

interface StoryDetailModalProps {
  story: Story | null;
  isOpen: boolean;
  onClose: () => void;
  onToggleSave: (storyId: number, currentlySaved: boolean) => void;
}

export const StoryDetailModal: React.FC<StoryDetailModalProps> = ({
  story,
  isOpen,
  onClose,
  onToggleSave,
}) => {
  if (!isOpen || !story) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div 
        className="relative w-full max-w-lg glass-card rounded-2xl border border-radar-borderGlow/40 p-5 sm:p-6 my-auto text-left shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Badges & Close Button */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 text-[11px] font-mono font-bold uppercase tracking-wider rounded-md bg-radar-cyan/15 text-radar-cyan border border-radar-cyan/30">
              {story.category}
            </span>
            {story.is_breaking && (
              <span className="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider rounded-md bg-radar-red/20 text-radar-red border border-radar-red/40 animate-pulse">
                BREAKING
              </span>
            )}
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-radar-card text-gray-400 hover:text-white hover:bg-radar-cardHover transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Headline */}
        <h2 className="text-lg sm:text-xl font-bold text-white mb-2 leading-tight">
          {story.headline || story.title}
        </h2>

        {/* Source metadata */}
        <div className="flex items-center gap-2 text-xs font-mono text-gray-400 mb-4 pb-3 border-b border-radar-border">
          <span className="text-gray-300 font-medium">{story.source_name}</span>
          <span>•</span>
          <span>{story.published_at ? new Date(story.published_at).toLocaleDateString() : 'Recent'}</span>
          <span>•</span>
          <span className="text-radar-lime font-semibold">Signal {story.final_score || story.importance_score}</span>
        </div>

        {/* AI RADAR SUMMARY BANNER (Crucial distinction from original source) */}
        <div className="rounded-xl bg-radar-surface/90 border border-radar-border p-3.5 mb-4">
          <div className="flex items-center gap-1.5 text-[11px] font-mono font-bold text-radar-cyan uppercase tracking-wider mb-1.5">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI RADAR Grounded Summary</span>
          </div>
          <p className="text-sm text-gray-200 leading-relaxed mb-3">
            {story.summary || 'Summary analysis pending autonomous classification.'}
          </p>

          <div className="pt-2 border-t border-radar-border/60">
            <div className="text-[10px] font-mono font-bold text-radar-lime uppercase tracking-wider mb-1">
              Why It Matters
            </div>
            <p className="text-xs text-gray-300 italic leading-relaxed">
              "{story.why_it_matters || 'Represents a noteworthy advancement in the AI ecosystem.'}"
            </p>
          </div>
        </div>

        {/* Signal Scores Breakdown */}
        <div className="grid grid-cols-3 gap-2 mb-4 font-mono text-center">
          <div className="p-2 rounded-lg bg-radar-card border border-radar-border">
            <div className="text-[10px] text-gray-400">IMPORTANCE</div>
            <div className="text-sm font-bold text-radar-cyan">{Math.round(story.importance_score)}/100</div>
          </div>
          <div className="p-2 rounded-lg bg-radar-card border border-radar-border">
            <div className="text-[10px] text-gray-400">NOVELTY</div>
            <div className="text-sm font-bold text-radar-lime">{Math.round(story.novelty_score)}/100</div>
          </div>
          <div className="p-2 rounded-lg bg-radar-card border border-radar-border">
            <div className="text-[10px] text-gray-400">TECHNICAL</div>
            <div className="text-sm font-bold text-radar-blue">{Math.round(story.technical_score)}/100</div>
          </div>
        </div>

        {/* Entity Tags */}
        <div className="space-y-2 mb-5 text-xs">
          {story.companies.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Building className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-gray-400 text-[11px]">Companies:</span>
              {story.companies.map((c) => (
                <span key={c} className="px-2 py-0.5 rounded bg-radar-card text-gray-300 text-[11px] border border-radar-border">
                  {c}
                </span>
              ))}
            </div>
          )}

          {story.technologies.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Code2 className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-gray-400 text-[11px]">Tech:</span>
              {story.technologies.map((t) => (
                <span key={t} className="px-2 py-0.5 rounded bg-radar-card text-gray-300 text-[11px] border border-radar-border">
                  {t}
                </span>
              ))}
            </div>
          )}

          {story.topics.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Tag className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-gray-400 text-[11px]">Topics:</span>
              {story.topics.map((t) => (
                <span key={t} className="px-2 py-0.5 rounded bg-radar-card text-gray-300 text-[11px] border border-radar-border">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 pt-3 border-t border-radar-border">
          <button
            onClick={() => onToggleSave(story.id, story.is_saved)}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border font-medium text-xs sm:text-sm transition-all ${
              story.is_saved
                ? 'bg-radar-cyan/15 text-radar-cyan border-radar-cyan/40 shadow-sm'
                : 'bg-radar-card hover:bg-radar-cardHover text-gray-300 border-radar-border'
            }`}
          >
            <Bookmark className={`w-4 h-4 ${story.is_saved ? 'fill-radar-cyan' : ''}`} />
            <span>{story.is_saved ? 'Saved' : 'Save Story'}</span>
          </button>

          <a
            href={story.canonical_url || story.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-radar-cyan hover:bg-radar-cyan/90 text-black font-semibold text-xs sm:text-sm shadow-md transition-all"
          >
            <span>Read Original</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};
