import React from 'react';
import { Link } from 'react-router-dom';
import { Product } from '@/types';
import { formatCurrency, formatRelativeTime, truncateText } from '@/utils/formatters';
import { TrashIcon, PauseIcon, PlayIcon, ChartBarIcon } from '@heroicons/react/24/outline';

interface ProductCardProps {
  product: Product;
  onDelete: (id: number) => void;
  onToggleActive: (id: number, isActive: boolean) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onDelete, onToggleActive }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex gap-4">
          {product.image_url && (
            <img
              src={product.image_url}
              alt={product.name || 'Product'}
              className="w-24 h-24 object-cover rounded"
            />
          )}
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 mb-1">
              {truncateText(product.name || 'Unknown Product', 50)}
            </h3>
            
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-2xl font-bold text-blue-600">
                {formatCurrency(product.current_price, product.currency)}
              </span>
              {product.alert_count && product.alert_count > 0 && (
                <span className="text-xs text-gray-500">
                  {product.alert_count} alert{product.alert_count > 1 ? 's' : ''}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
              <span>Checks every {product.check_interval_minutes} min</span>
              {product.last_checked_at && (
                <span>• Last checked {formatRelativeTime(product.last_checked_at)}</span>
              )}
            </div>

            <div className="flex items-center gap-2">
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
          </div>
        </div>

        <div className="flex gap-2 mt-4 pt-4 border-t">
          <Link
            to={`/product/${product.id}`}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
          >
            <ChartBarIcon className="w-4 h-4" />
            Details
          </Link>
          
          <button
            onClick={() => onToggleActive(product.id, !product.is_active)}
            className="flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            title={product.is_active ? 'Pause tracking' : 'Resume tracking'}
          >
            {product.is_active ? (
              <PauseIcon className="w-4 h-4 text-gray-600" />
            ) : (
              <PlayIcon className="w-4 h-4 text-gray-600" />
            )}
          </button>

          <button
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this product?')) {
                onDelete(product.id);
              }
            }}
            className="flex items-center justify-center px-3 py-2 border border-red-300 rounded-md hover:bg-red-50 transition-colors"
            title="Delete product"
          >
            <TrashIcon className="w-4 h-4 text-red-600" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
