import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit2, Trash2, ArrowUp, ArrowDown, Filter, MoreHorizontal, Package } from 'lucide-react';
import apiClient from '../api/apiClient';

const Products: React.FC = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchProducts = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.get(`/products?search=${search}`);
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(fetchProducts, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleStockUpdate = async (id: string, delta: number) => {
    try {
      const changeType = delta > 0 ? 'restock' : 'sale';
      await apiClient.post(`/products/${id}/stock?delta=${delta}&change_type=${changeType}`);
      fetchProducts();
    } catch {
      alert('Failed to update stock');
    }
  };

  return (
    <div className="animate-in">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Asset Ledger</h1>
            <p className="page-subtitle">Manage and track all inventory assets in real-time</p>
          </div>
          <button className="btn-primary" style={{ width: 'auto', padding: '12px 24px' }}>
            <Plus size={18} />
            Add Product
          </button>
        </div>
      </div>

      <div className="table-container">
        <div className="table-toolbar">
          <div className="search-box">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search by name or SKU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button className="icon-btn">
            <Filter size={18} />
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Stock Level</th>
              <th style={{ textAlign: 'right' }}>Unit Price</th>
              <th style={{ textAlign: 'center' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={5}>
                  <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Syncing Asset Ledger...</p>
                  </div>
                </td>
              </tr>
            ) : products.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  <div className="empty-state">
                    <div className="empty-state-icon"><Package size={28} /></div>
                    <p>No products found. Add your first asset.</p>
                  </div>
                </td>
              </tr>
            ) : products.map((p) => (
              <tr key={p._id}>
                <td>
                  <div className="product-name">{p.name}</div>
                  <div className="product-location">📍 {p.location}</div>
                </td>
                <td>
                  <span className="sku-tag">{p.sku}</span>
                </td>
                <td>
                  <div className="qty-display">
                    <div>
                      <span className={p.quantity <= p.reorder_threshold ? 'qty-val-low' : 'qty-val-good'}>
                        {p.quantity}
                      </span>
                      <div style={{ fontSize: 9, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1 }}>units</div>
                    </div>
                    <div className="qty-controls">
                      <button className="qty-btn up" onClick={() => handleStockUpdate(p._id, 1)} title="Restock">
                        <ArrowUp size={12} />
                      </button>
                      <button className="qty-btn down" onClick={() => handleStockUpdate(p._id, -1)} title="Remove">
                        <ArrowDown size={12} />
                      </button>
                    </div>
                  </div>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <span className="price-display">
                    <span className="price-currency">$</span>
                    {p.unit_price?.toLocaleString()}
                  </span>
                </td>
                <td>
                  <div className="actions">
                    <button className="action-btn edit" title="Edit"><Edit2 size={15} /></button>
                    <button className="action-btn delete" title="Delete"><Trash2 size={15} /></button>
                    <button className="action-btn more" title="More"><MoreHorizontal size={15} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Products;
