import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '@/components/layout/Layout';
import PriceHistoryChart from '@/components/charts/PriceHistoryChart';
import AlertForm from '@/components/alerts/AlertForm';
import AlertList from '@/components/alerts/AlertList';
import { Product, PriceAlert, PriceHistory } from '@/types';
import { productService } from '@/services/products';
import { formatCurrency, formatRelativeTime } from '@/utils/formatters';
import { ArrowLeftIcon, LinkIcon, PauseIcon, PlayIcon } from '@heroicons/react/24/outline';

const ProductDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [history, setHistory] = useState<PriceHistory[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    if (!id) return;
    
    try {
      const [productData, alertsData, historyData] = await Promise.all([
        productService.getProduct(parseInt(id)),
        productService.getAlerts(parseInt(id)),
        productService.getPriceHistory(parseInt(id)),
      ]);
      
      setProduct(productData);
      setAlerts(alertsData);
      setHistory(historyData);
    } catch (error) {
      console.error('Failed to fetch product details:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleAddAlert = async (data: any) => {
    if (!id) return;
    await productService.createAlert(parseInt(id), data);
    await fetchData();
  };

  const handleDeleteAlert = async (alertId: number) => {
    await productService.deleteAlert(alertId);
    setAlerts(alerts.filter(a => a.id !== alertId));
  };

  const handleToggleAlert = async (alertId: number, isActive: boolean) => {
    await productService.updateAlert(alertId, { is_active: isActive });
    setAlerts(alerts.map(a => a.id === alertId ? { ...a, is_active: isActive } : a));
  };

  const handleToggleProduct = async () => {
    if (!product || !id) return;
    const updated = await productService.updateProduct(parseInt(id), { is_active: !product.is_active });
    setProduct(updated);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  if (!product) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">Product not found</p>
          <Link to="/dashboard" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-6">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
        >
          <ArrowLeftIcon className="w-5 h-5" />
          Back to Dashboard
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex gap-6">
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.name || 'Product'}
                  className="w-32 h-32 object-cover rounded"
                />
              )}
              
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  {product.name || 'Unknown Product'}
                </h1>
                
                <div className="flex items-baseline gap-3 mb-3">
                  <span className="text-3xl font-bold text-blue-600">
                    {formatCurrency(product.current_price, product.currency)}
                  </span>
                  {product.is_active ? (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Active
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      Paused
                    </span>
                  )}
                </div>

                <div className="text-sm text-gray-600 space-y-1 mb-4">
                  <p>Check interval: {product.check_interval_minutes} minutes</p>
                  {product.last_checked_at && (
                    <p>Last checked: {formatRelativeTime(product.last_checked_at)}</p>
                  )}
                </div>

                <div className="flex gap-3">
                  <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                  >
                    <LinkIcon className="w-4 h-4" />
                    View Product
                  </a>
                  
                  <button
                    onClick={handleToggleProduct}
                    className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm"
                  >
                    {product.is_active ? (
                      <>
                        <PauseIcon className="w-4 h-4" />
                        Pause Tracking
                      </>
                    ) : (
                      <>
                        <PlayIcon className="w-4 h-4" />
                        Resume Tracking
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Price History</h2>
            <PriceHistoryChart
              history={history}
              alerts={alerts}
              currency={product.currency || 'USD'}
            />
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Price Alerts</h2>
            <div className="space-y-4">
              <AlertForm onSubmit={handleAddAlert} />
              <AlertList
                alerts={alerts}
                currency={product.currency || 'USD'}
                onDelete={handleDeleteAlert}
                onToggle={handleToggleAlert}
              />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ProductDetails;
