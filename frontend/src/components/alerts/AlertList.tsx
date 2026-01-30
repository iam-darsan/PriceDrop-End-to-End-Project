import React from 'react';
import { PriceAlert } from '@/types';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { TrashIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface AlertListProps {
  alerts: PriceAlert[];
  currency: string;
  onDelete: (id: number) => void;
  onToggle: (id: number, isActive: boolean) => void;
}

const AlertList: React.FC<AlertListProps> = ({ alerts, currency, onDelete, onToggle }) => {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500 bg-white rounded-lg border border-gray-200">
        No alerts set for this product
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="bg-white p-4 rounded-lg border border-gray-200 flex items-center justify-between"
        >
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(parseFloat(alert.target_price.toString()), currency)}
              </span>
              
              {alert.triggered_at ? (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Triggered
                </span>
              ) : alert.is_active ? (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Active
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Inactive
                </span>
              )}
            </div>
            
            <p className="text-xs text-gray-500 mt-1">
              Created: {formatDate(alert.created_at)}
              {alert.triggered_at && ` • Triggered: ${formatDate(alert.triggered_at)}`}
            </p>
          </div>

          <div className="flex gap-2">
            {!alert.triggered_at && (
              <button
                onClick={() => onToggle(alert.id, !alert.is_active)}
                className="p-2 hover:bg-gray-100 rounded transition-colors"
                title={alert.is_active ? 'Deactivate alert' : 'Activate alert'}
              >
                {alert.is_active ? (
                  <XCircleIcon className="w-5 h-5 text-gray-600" />
                ) : (
                  <CheckCircleIcon className="w-5 h-5 text-green-600" />
                )}
              </button>
            )}
            
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to delete this alert?')) {
                  onDelete(alert.id);
                }
              }}
              className="p-2 hover:bg-red-50 rounded transition-colors"
              title="Delete alert"
            >
              <TrashIcon className="w-5 h-5 text-red-600" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertList;
