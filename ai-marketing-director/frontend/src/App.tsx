import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ContentLibrary from './pages/ContentLibrary';
import ContentEditor from './pages/ContentEditor';
import ContentCalendar from './pages/ContentCalendar';
import Approvals from './pages/Approvals';
import OAuthSettings from './pages/OAuthSettings';
import Campaigns from './pages/Campaigns';
import './styles/global.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/content" element={<ContentLibrary />} />
          <Route path="/content/new" element={<ContentEditor />} />
          <Route path="/content/:id/edit" element={<ContentEditor />} />
          <Route path="/calendar" element={<ContentCalendar />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/settings/oauth" element={<OAuthSettings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
