import api from './api';
import { User } from '@/types';

const API_BASE_URL = 'https://api.pricedrop24.shop';

export const authService = {
  getLoginUrl: () => {
    return `${API_BASE_URL}/auth/login`;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  setToken: (token: string) => {
    localStorage.setItem('token', token);
  },

  getToken: (): string | null => {
    return localStorage.getItem('token');
  },

  removeToken: () => {
    localStorage.removeItem('token');
  },
};
