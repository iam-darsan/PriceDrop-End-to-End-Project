import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GoogleLoginButton from '@/components/auth/GoogleLoginButton';
import { useAuth } from '@/context/AuthContext';

const Login: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      navigate('/dashboard');
    }
  }, [token, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">PriceDrop</h1>
          <p className="text-gray-600">Track product prices and get notified when they drop</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">Welcome Back</h2>
          
          <div className="flex justify-center">
            <GoogleLoginButton />
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Features:</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="mr-2">✓</span>
                <span>Track prices from any e-commerce site</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">✓</span>
                <span>Set multiple price alerts per product</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">✓</span>
                <span>View price history charts</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">✓</span>
                <span>Email notifications when prices drop</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
