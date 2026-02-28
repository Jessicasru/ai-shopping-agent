import { Routes, Route } from 'react-router-dom';
import Nav from './components/Nav';
import Landing from './pages/Landing';
import Upload from './pages/Upload';
import Profile from './pages/Profile';
import Matches from './pages/Matches';

export default function App() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="pt-[4.5rem]">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/matches" element={<Matches />} />
        </Routes>
      </main>
    </div>
  );
}
