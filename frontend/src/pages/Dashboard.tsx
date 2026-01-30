import React from 'react';
import Layout from '@/components/layout/Layout';
import ProductList from '@/components/products/ProductList';

const Dashboard: React.FC = () => {
  return (
    <Layout>
      <ProductList />
    </Layout>
  );
};

export default Dashboard;
