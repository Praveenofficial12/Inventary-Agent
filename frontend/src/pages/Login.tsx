import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/apiClient';
import { LogIn, Loader2, Mail, Lock } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const res = await apiClient.post('/auth/login', { email, password });
      const { access_token, refresh_token, user: userData } = res.data;
      login(access_token, refresh_token, userData);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-orb auth-bg-orb-1"></div>
      <div className="auth-bg-orb auth-bg-orb-2"></div>

      <div className="auth-card animate-in">
        <div className="auth-header">
          <div className="auth-icon-wrap">
            <LogIn />
          </div>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to Nexus AI Inventory System</p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="alert-error">{error}</div>}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="input-wrap">
              <input
                type="email"
                required
                className="input-field"
                placeholder="admin@nexus.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Mail className="input-icon" size={18} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrap">
              <input
                type="password"
                required
                className="input-field"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Lock className="input-icon" size={18} />
            </div>
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? <Loader2 size={20} className="spin-icon" /> : <><LogIn size={18} />Sign In</>}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account? <Link to="/register">Create one</Link>
        </div>
      </div>

      <style>{`
        .spin-icon { animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Login;
