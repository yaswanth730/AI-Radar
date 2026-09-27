export interface Story {
  id: number;
  title: string;
  headline?: string;
  summary?: string;
  why_it_matters?: string;
  canonical_url: string;
  original_url: string;
  category: string;
  sub_category?: string;
  published_at?: string;
  discovered_at: string;
  importance_score: number;
  novelty_score: number;
  technical_score: number;
  final_score: number;
  is_breaking: boolean;
  is_saved: boolean;
  source_id: number;
  source_name: string;
  source_type: string;
  topics: string[];
  companies: string[];
  technologies: string[];
}

export interface Stats {
  sources_total: number;
  sources_active: number;
  stories_discovered_total: number;
  duplicates_filtered_total: number;
  important_stories_total: number;
  saved_stories_total: number;
  last_scan_time?: string;
  last_scan_status?: string;
  last_scan_duration_seconds?: number;
}

export interface Source {
  id: number;
  name: string;
  type: 'RSS' | 'ATOM' | 'WEB' | 'GITHUB' | 'RESEARCH';
  url: string;
  priority: number;
  status: 'active' | 'inactive';
  last_successful_scan?: string;
  last_failure_at?: string;
  last_error_message?: string;
  stories_discovered_count: number;
}

export interface Preferences {
  scan_interval_minutes: number;
  ai_provider: string;
  categories: Record<string, number>;
  top_topics: { entity_name: string; score: number; interaction_count: number }[];
  top_companies: { entity_name: string; score: number; interaction_count: number }[];
  top_technologies: { entity_name: string; score: number; interaction_count: number }[];
}
