import React, { useState } from 'react';
import ProductList from './ProductList';
import ProductDetail from './ProductDetail';

function App() {
  const [selectedProduct, setSelectedProduct] = useState(null);

  return (
    <div>
      {!selectedProduct ? (
        <ProductList onSelect={setSelectedProduct} />
      ) : (
        <ProductDetail product={selectedProduct} onBack={() => setSelectedProduct(null)} />
      )}
    </div>
  );
}

export default App;
