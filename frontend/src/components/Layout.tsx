import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare } from 'lucide-react';
import Sidebar from './Sidebar';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        {children}
      </main>
      <Link to="/chat" className="floating-ai-btn" title="Open AI assistant">
        <MessageSquare size={20} />
      </Link>
    </div>
  );
};

export default Layout;
