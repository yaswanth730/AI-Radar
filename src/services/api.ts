import type { Story, Stats, Source, Preferences } from '../types';

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.statusText}`);
  return res.json();
}

export async function fetchRadarStories(): Promise<Story[]> {
  const res = await fetch(`${API_BASE}/radar`);
  if (!res.ok) throw new Error(`Failed to fetch radar stories: ${res.statusText}`);
  return res.json();
}

export async function fetchForYouStories(): Promise<Story[]> {
  const res = await fetch(`${API_BASE}/for-you`);
  if (!res.ok) throw new Error(`Failed to fetch For You feed: ${res.statusText}`);
  return res.json();
}

export async function fetchTrendingStories(): Promise<Story[]> {
  const res = await fetch(`${API_BASE}/trending`);
  if (!res.ok) throw new Error(`Failed to fetch trending stories: ${res.statusText}`);
  return res.json();
}

export async function fetchSavedStories(): Promise<Story[]> {
  const res = await fetch(`${API_BASE}/saved`);
  if (!res.ok) throw new Error(`Failed to fetch saved stories: ${res.statusText}`);
  return res.json();
}

export async function fetchStoryDetail(id: number): Promise<Story> {
  const res = await fetch(`${API_BASE}/stories/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch story ${id}: ${res.statusText}`);
  return res.json();
}

export async function recordInteraction(storyId: number, interactionType: string): Promise<void> {
  await fetch(`${API_BASE}/stories/${storyId}/interactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ interaction_type: interactionType }),
  });
}

export async function toggleSaveStory(storyId: number, currentlySaved: boolean): Promise<boolean> {
  const method = currentlySaved ? 'DELETE' : 'POST';
  const res = await fetch(`${API_BASE}/stories/${storyId}/save`, { method });
  if (!res.ok) throw new Error(`Save toggle failed: ${res.statusText}`);
  const data = await res.json();
  return data.saved;
}

export async function fetchSources(): Promise<Source[]> {
  const res = await fetch(`${API_BASE}/sources`);
  if (!res.ok) throw new Error(`Failed to fetch sources: ${res.statusText}`);
  return res.json();
}

export async function fetchPreferences(): Promise<Preferences> {
  const res = await fetch(`${API_BASE}/preferences`);
  if (!res.ok) throw new Error(`Failed to fetch preferences: ${res.statusText}`);
  return res.json();
}

export async function triggerManualScan(): Promise<void> {
  const res = await fetch(`${API_BASE}/scans/run`, { method: 'POST' });
  if (!res.ok) {
    // If not implemented yet in foundation, log gracefully
    console.warn("Manual scan endpoint pending scheduler milestone");
  }
}
