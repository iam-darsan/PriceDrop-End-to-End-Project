import api from './api';
import { Product, ProductCreate, ProductUpdate, PriceAlert, AlertCreate, AlertUpdate, PriceHistory } from '@/types';

export const productService = {
  getProducts: async (): Promise<Product[]> => {
    const response = await api.get<Product[]>('/products');
    return response.data;
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get<Product>(`/products/${id}`);
    return response.data;
  },

  createProduct: async (data: ProductCreate): Promise<Product> => {
    const response = await api.post<Product>('/products', data);
    return response.data;
  },

  updateProduct: async (id: number, data: ProductUpdate): Promise<Product> => {
    const response = await api.patch<Product>(`/products/${id}`, data);
    return response.data;
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`);
  },

  getAlerts: async (productId: number): Promise<PriceAlert[]> => {
    const response = await api.get<PriceAlert[]>(`/products/${productId}/alerts`);
    return response.data;
  },

  createAlert: async (productId: number, data: AlertCreate): Promise<PriceAlert> => {
    const response = await api.post<PriceAlert>(`/products/${productId}/alerts`, data);
    return response.data;
  },

  updateAlert: async (alertId: number, data: AlertUpdate): Promise<PriceAlert> => {
    const response = await api.patch<PriceAlert>(`/alerts/${alertId}`, data);
    return response.data;
  },

  deleteAlert: async (alertId: number): Promise<void> => {
    await api.delete(`/alerts/${alertId}`);
  },

  getPriceHistory: async (productId: number, startDate?: string, endDate?: string): Promise<PriceHistory[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get<PriceHistory[]>(`/products/${productId}/history?${params.toString()}`);
    return response.data;
  },
};
