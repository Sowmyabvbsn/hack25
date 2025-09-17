import React from 'react';
import { products } from './products';

function ProductList({ onSelect }) {
  return (
    <div className="product-list">
      {products.map(product => (
        <button key={product.id} onClick={() => onSelect(product)}>
          {product.name}
        </button>
      ))}
    </div>
  );
}

export default ProductList;
