import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { TopHeader } from './components/TopHeader';
import { Navbar } from './components/Navbar';
import { RadarPage } from './pages/RadarPage';
import { ForYouPage } from './pages/ForYouPage';
import { TrendingPage } from './pages/TrendingPage';
import { SavedPage } from './pages/SavedPage';
import { SourcesPage } from './pages/SourcesPage';
import { SettingsPage } from './pages/SettingsPage';
import { StoryDetailPage } from './pages/StoryDetailPage';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-radar-bg text-gray-100 flex flex-col font-sans selection:bg-radar-cyan selection:text-black">
      <TopHeader />
      <Navbar />
      <main className="flex-1 w-full max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<RadarPage />} />
          <Route path="/for-you" element={<ForYouPage />} />
          <Route path="/trending" element={<TrendingPage />} />
          <Route path="/saved" element={<SavedPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/story/:id" element={<StoryDetailPage />} />
          <Route path="*" element={<RadarPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
