import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Package, Users, MessageSquare,
  FileText, LogOut, ChevronRight, Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar: React.FC = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const links = [
    { to: '/', icon: <LayoutDashboard size={20} />, label: 'Intelligence Hub', end: true },
    { to: '/products', icon: <Package size={20} />, label: 'Asset Ledger', end: false },
    { to: '/suppliers', icon: <Users size={20} />, label: 'Entity Hub', end: false },
    { to: '/chat', icon: <MessageSquare size={20} />, label: 'Nexus AI Chat', end: false },
    { to: '/reports', icon: <FileText size={20} />, label: 'Strategic Reports', end: false },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <Zap size={22} fill="white" />
        </div>
        <div className="logo-text">
          <h1>Nexus AI</h1>
          <span>Inventory System</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">Navigation</div>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">{link.icon}</span>
            <span>{link.label}</span>
            <ChevronRight size={14} className="nav-chevron" />
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-user">
        <div className="user-avatar">
          {(user?.full_name?.charAt(0) || 'A').toUpperCase()}
        </div>
        <div className="user-info">
          <div className="user-name">{user?.full_name || 'Administrator'}</div>
          <div className="user-role">{user?.role || 'Admin Access'}</div>
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={18} />
          <span>Terminate Session</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
