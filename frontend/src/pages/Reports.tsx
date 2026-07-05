import React, { useState } from 'react';
import { FileDown, FileText, Loader2, Sparkles, BarChart2, TrendingUp, Package } from 'lucide-react';
import apiClient from '../api/apiClient';

const Reports: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/reports/generate');
      setReport(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate report. Check AI configuration.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const res = await apiClient.get('/reports/download/pdf', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'nexus_inventory_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      alert('PDF download failed.');
    }
  };

  return (
    <div className="animate-in">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Strategic Reports</h1>
            <p className="page-subtitle">AI-generated executive intelligence reports</p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            {report && (
              <button className="btn-secondary" onClick={handleDownloadPDF}>
                <FileDown size={18} />
                Download PDF
              </button>
            )}
            <button
              className="btn-primary"
              style={{ width: 'auto', padding: '12px 24px' }}
              onClick={handleGenerate}
              disabled={isLoading}
            >
              {isLoading
                ? <><Loader2 size={18} style={{ animation: 'spin 0.8s linear infinite' }} /> Generating...</>
                : <><Sparkles size={18} /> Generate Report</>
              }
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert-error" style={{ marginBottom: 24 }}>{error}</div>
      )}

      {!report && !isLoading && (
        <div className="reports-hero">
          <div className="reports-hero-icon"><FileText size={32} /></div>
          <h2>No Report Generated Yet</h2>
          <p>Click "Generate Report" to have Nexus AI analyze your entire inventory and produce a detailed executive summary.</p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 40, maxWidth: 600, margin: '40px auto 0' }}>
            {[
              { icon: <BarChart2 size={20} />, label: 'Stock Analysis', desc: 'Deep inventory breakdown' },
              { icon: <TrendingUp size={20} />, label: 'Risk Vectors', desc: 'Shortage predictions' },
              { icon: <Package size={20} />, label: 'Asset Valuation', desc: 'Full portfolio value' },
            ].map((f, i) => (
              <div key={i} style={{
                padding: '20px 16px',
                background: 'var(--bg)',
                border: '1px solid var(--border)',
                borderRadius: 12,
                textAlign: 'center',
                transition: 'all 0.25s',
                cursor: 'default',
              }}>
                <div style={{ color: 'var(--primary)', marginBottom: 10, display: 'flex', justifyContent: 'center' }}>{f.icon}</div>
                <div style={{ fontSize: 13, fontWeight: 700, color: 'white', marginBottom: 4 }}>{f.label}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="loading-state" style={{ minHeight: 360 }}>
          <div className="spinner"></div>
          <p>Nexus AI is analyzing your entire inventory...</p>
          <p style={{ fontSize: 12, opacity: 0.6 }}>This may take 15-30 seconds</p>
        </div>
      )}

      {report && (
        <div className="report-card">
          <div className="report-title">{report.title}</div>
          <div className="report-summary">{report.summary}</div>

          <div className="report-metrics">
            <div className="report-metric">
              <div className="report-metric-label">Total Inventory Value</div>
              <div className="report-metric-value green">
                ${report.key_metrics?.total_value?.toLocaleString() ?? 'N/A'}
              </div>
            </div>
            <div className="report-metric">
              <div className="report-metric-label">Low Stock Alerts</div>
              <div className="report-metric-value yellow">
                {report.key_metrics?.low_stock_count ?? 'N/A'}
              </div>
            </div>
            <div className="report-metric">
              <div className="report-metric-label">Top Category</div>
              <div className="report-metric-value primary">
                {report.key_metrics?.top_category ?? 'N/A'}
              </div>
            </div>
          </div>

          {Array.isArray(report.sections) && report.sections.map((section: any, i: number) => (
            <div key={i} className="report-section">
              <div className="report-section-heading">
                <div className="report-section-bar"></div>
                {section.heading}
              </div>
              <div className="report-section-content">{section.content}</div>
            </div>
          ))}
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Reports;
