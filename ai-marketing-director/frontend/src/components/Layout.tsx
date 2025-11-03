import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Calendar,
  CheckSquare,
  Settings,
  TrendingUp,
  Rocket,
} from 'lucide-react';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Content', href: '/content', icon: FileText },
    { name: 'Calendar', href: '/calendar', icon: Calendar },
    { name: 'Approvals', href: '/approvals', icon: CheckSquare },
    { name: 'Campaigns', href: '/campaigns', icon: TrendingUp },
    { name: 'OAuth Settings', href: '/settings/oauth', icon: Settings },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <Rocket className="logo-icon" size={32} />
          <div className="logo-text">
            <div className="logo-title">AI Elevate</div>
            <div className="logo-subtitle">Marketing Director</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`nav-item ${isActive(item.href) ? 'active' : ''}`}
              >
                <Icon size={20} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">AE</div>
            <div>
              <div className="user-name">AI Elevate</div>
              <div className="user-role">Marketing Team</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="content-wrapper">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
