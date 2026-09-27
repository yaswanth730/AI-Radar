import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchStoryDetail, toggleSaveStory } from '../services/api';
import { ArrowLeft, Bookmark, ExternalLink, Sparkles, Building, Code2, RefreshCw } from 'lucide-react';

export const StoryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const storyId = Number(id);

  const { data: story, isLoading, isError } = useQuery({
    queryKey: ['story', storyId],
    queryFn: () => fetchStoryDetail(storyId),
    enabled: !isNaN(storyId),
  });

  const saveMutation = useMutation({
    mutationFn: ({ id, isSaved }: { id: number; isSaved: boolean }) =>
      toggleSaveStory(id, isSaved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['story', storyId] });
      queryClient.invalidateQueries({ queryKey: ['savedStories'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <RefreshCw className="w-6 h-6 text-radar-cyan animate-spin" />
      </div>
    );
  }

  if (isError || !story) {
    return (
      <div className="max-w-xl mx-auto px-4 py-12 text-center">
        <h2 className="text-base font-bold text-white mb-2">Story Not Found</h2>
        <p className="text-xs text-gray-400 mb-4">The requested intelligence item could not be retrieved.</p>
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 rounded-xl bg-radar-card border border-radar-border text-xs text-white"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-4 pb-24">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white font-mono mb-4 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back</span>
      </button>

      <div className="glass-card rounded-2xl border border-radar-border p-6 sm:p-8">
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="px-2.5 py-1 text-xs font-mono font-bold uppercase tracking-wider rounded-md bg-radar-cyan/15 text-radar-cyan border border-radar-cyan/30">
            {story.category}
          </span>
          <span className="text-xs font-mono font-bold text-radar-lime">
            SIGNAL {Math.round(story.final_score || story.importance_score)}
          </span>
        </div>

        <h1 className="text-xl sm:text-2xl font-extrabold text-white mb-3 leading-snug">
          {story.headline || story.title}
        </h1>

        <div className="flex items-center gap-2 text-xs font-mono text-gray-400 mb-5 pb-3 border-b border-radar-border">
          <span className="text-gray-300 font-medium">{story.source_name}</span>
          <span>•</span>
          <span>{story.published_at ? new Date(story.published_at).toLocaleDateString() : 'Recent'}</span>
        </div>

        {/* AI RADAR Grounded Summary */}
        <div className="rounded-xl bg-radar-surface/90 border border-radar-border p-4 mb-5">
          <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-radar-cyan uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" />
            <span>AI RADAR Grounded Summary</span>
          </div>
          <p className="text-sm text-gray-200 leading-relaxed mb-3">
            {story.summary}
          </p>

          <div className="pt-2.5 border-t border-radar-border/60">
            <div className="text-[11px] font-mono font-bold text-radar-lime uppercase tracking-wider mb-1">
              Why It Matters
            </div>
            <p className="text-xs text-gray-300 italic leading-relaxed">
              "{story.why_it_matters}"
            </p>
          </div>
        </div>

        {/* Entity Tags */}
        <div className="space-y-2 mb-6 text-xs">
          {story.companies.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Building className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-gray-400">Companies:</span>
              {story.companies.map((c) => (
                <span key={c} className="px-2 py-0.5 rounded bg-radar-card text-gray-300 border border-radar-border">
                  {c}
                </span>
              ))}
            </div>
          )}

          {story.technologies.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Code2 className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-gray-400">Tech:</span>
              {story.technologies.map((t) => (
                <span key={t} className="px-2 py-0.5 rounded bg-radar-card text-gray-300 border border-radar-border">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3 pt-3 border-t border-radar-border">
          <button
            onClick={() => saveMutation.mutate({ id: story.id, isSaved: story.is_saved })}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border font-medium text-xs sm:text-sm transition-all ${
              story.is_saved
                ? 'bg-radar-cyan/15 text-radar-cyan border-radar-cyan/40'
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
            <span>Read Original Source</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};
