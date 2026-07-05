import React, { useState, useEffect } from 'react';
import { Plus, Globe, Mail, Phone, Star, MapPin, ChevronRight } from 'lucide-react';
import apiClient from '../api/apiClient';

const Suppliers: React.FC = () => {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSuppliers = async () => {
      try {
        const res = await apiClient.get('/suppliers');
        setSuppliers(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSuppliers();
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Entity Hub</h1>
            <p className="page-subtitle">Global supply chain partners and vendor intelligence</p>
          </div>
          <button className="btn-primary" style={{ width: 'auto', padding: '12px 24px' }}>
            <Plus size={18} />
            Onboard Entity
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Retrieving Entity Profiles...</p>
        </div>
      ) : suppliers.length === 0 ? (
        <div className="empty-state" style={{ padding: 80 }}>
          <div className="empty-state-icon">
            <Globe size={28} />
          </div>
          <p>No supply chain entities found. Onboard your first partner.</p>
        </div>
      ) : (
        <div className="entity-grid">
          {suppliers.map((s) => (
            <div key={s._id} className="entity-card">
              <div className="entity-avatar">
                <Globe size={28} />
              </div>
              <div className="entity-name">{s.name}</div>
              <div className="entity-tag">Verified Supply Partner</div>

              <div className="entity-detail">
                <div className="entity-detail-icon"><Mail size={15} /></div>
                <div>
                  <div className="entity-detail-label">Contact Email</div>
                  <div className="entity-detail-value">{s.contact_email || 'N/A'}</div>
                </div>
              </div>

              <div className="entity-detail">
                <div className="entity-detail-icon"><Phone size={15} /></div>
                <div>
                  <div className="entity-detail-label">Phone</div>
                  <div className="entity-detail-value">{s.contact_phone || 'N/A'}</div>
                </div>
              </div>

              <div className="entity-detail">
                <div className="entity-detail-icon"><MapPin size={15} /></div>
                <div>
                  <div className="entity-detail-label">Address</div>
                  <div className="entity-detail-value">{s.address || 'Global Hub'}</div>
                </div>
              </div>

              <div className="entity-detail">
                <div className="entity-detail-icon"><Star size={15} /></div>
                <div>
                  <div className="entity-detail-label">Rating</div>
                  <div className="entity-detail-value">{s.rating ?? 'N/A'} / 5.0</div>
                </div>
              </div>

              <div className="entity-footer">
                <span className="entity-id">ID: {String(s._id).substring(0, 8)}...</span>
                <button style={{
                  display: 'flex', alignItems: 'center', gap: 4,
                  padding: '6px 12px',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--primary-light)',
                  fontSize: 11,
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontFamily: 'var(--font)',
                  transition: 'all 0.25s',
                }}>
                  View Profile <ChevronRight size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Suppliers;
