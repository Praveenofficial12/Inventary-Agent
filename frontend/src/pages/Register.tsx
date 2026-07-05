import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { UserPlus, Mail, Lock, User } from 'lucide-react';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({ email: '', password: '', full_name: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await apiClient.post('/auth/register', formData);
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Try again.');
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
            <UserPlus />
          </div>
          <h1 className="auth-title">Secure Access</h1>
          <p className="auth-subtitle">Join the Nexus AI Command Network</p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="alert-error">{error}</div>}

          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div className="input-wrap">
              <input
                type="text"
                required
                className="input-field"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              />
              <User className="input-icon" size={18} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="input-wrap">
              <input
                type="email"
                required
                className="input-field"
                placeholder="admin@nexus.ai"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                placeholder="Create a strong password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
              <Lock className="input-icon" size={18} />
            </div>
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading
              ? <span style={{ animation: 'spin 0.8s linear infinite', display: 'inline-block' }}>⟳</span>
              : <><UserPlus size={18} />Create Account</>
            }
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
