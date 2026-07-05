import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Package, AlertTriangle, TrendingDown, DollarSign, Bell } from 'lucide-react';
import apiClient from '../api/apiClient';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, alertsRes] = await Promise.all([
          apiClient.get('/inventory/stats'),
          apiClient.get('/agents/alerts')
        ]);
        setStats(statsRes.data);
        setAlerts(alertsRes.data?.alerts || []);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
        // Set dummy stats so dashboard still renders
        setStats({ total_products: 0, low_stock: 0, out_of_stock: 0, total_value: 0 });
      }
    };
    fetchData();
  }, []);

  if (!stats) {
    return (
      <div className="loading-state animate-in">
        <div className="spinner"></div>
        <p>Synchronizing Nexus Intelligence...</p>
      </div>
    );
  }

  const chartData = [
    { name: 'Total', value: stats.total_products },
    { name: 'Low Stock', value: stats.low_stock },
    { name: 'Out of Stock', value: stats.out_of_stock },
  ];

  return (
    <div className="animate-in">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Intelligence Hub</h1>
            <p className="page-subtitle">Real-time inventory telemetry and AI-powered insights</p>
          </div>
          <div className="status-bar">
            <div className="status-dot"></div>
            All Systems Operational
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue"><Package size={26} /></div>
          <div>
            <div className="stat-label">Total Products</div>
            <div className="stat-value">{stats.total_products}</div>
            <div className="stat-trend">↑ 12% this month</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-yellow"><AlertTriangle size={26} /></div>
          <div>
            <div className="stat-label">Low Stock Items</div>
            <div className="stat-value">{stats.low_stock}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-red"><TrendingDown size={26} /></div>
          <div>
            <div className="stat-label">Out of Stock</div>
            <div className="stat-value">{stats.out_of_stock}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-green"><DollarSign size={26} /></div>
          <div>
            <div className="stat-label">Inventory Value</div>
            <div className="stat-value">${stats.total_value?.toLocaleString()}</div>
            <div className="stat-trend">↑ 5.4% this week</div>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Alerts */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <div className="card-icon"><Bell size={18} /></div>
              AI Alerts
            </div>
            <button style={{ color: 'var(--primary-light)', background: 'none', border: 'none', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}>View All</button>
          </div>
          <div className="card-body">
            {alerts.length > 0 ? (
              <div className="alerts-list">
                {alerts.map((alert, i) => (
                  <div key={i} className={`alert-item alert-item-${alert.severity}`}>
                    <div className={`alert-icon-wrap ${alert.severity === 'high' ? 'alert-icon-high' : 'alert-icon-med'}`}>
                      <AlertTriangle size={18} />
                    </div>
                    <div className="alert-content">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                        <div className="alert-product-name">{alert.product_name}</div>
                        <span className={`badge ${alert.severity === 'high' ? 'badge-red' : 'badge-yellow'}`}>
                          {alert.severity}
                        </span>
                      </div>
                      <div className="alert-message">{alert.message}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon"><Package size={28} /></div>
                <p>No risk vectors detected by Nexus AI</p>
              </div>
            )}
          </div>
        </div>

        {/* Chart */}
        <div className="card" style={{ minHeight: 460 }}>
          <div className="card-header">
            <div className="card-title">Stock Analytics</div>
          </div>
          <div className="card-body" style={{ height: 380 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} barSize={60}>
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.9} />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0.3} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" axisLine={false} tickLine={false} dy={10} tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                <YAxis stroke="#64748b" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip
                  cursor={{ fill: 'rgba(99,102,241,0.06)' }}
                  contentStyle={{ background: '#0d1526', border: '1px solid #1e2d4a', borderRadius: 12, boxShadow: '0 10px 40px rgba(0,0,0,0.4)' }}
                  itemStyle={{ color: '#e2e8f0', fontWeight: 700 }}
                  labelStyle={{ color: '#94a3b8', fontWeight: 600 }}
                />
                <Bar dataKey="value" fill="url(#barGrad)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
