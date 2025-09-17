import React from 'react';

function ProductDetail({ product, onBack }) {
  if (!product) return null;
  return (
    <div className="product-detail">
      <h2>{product.name}</h2>
      <p>{product.description}</p>
      <img src={product.image} alt={product.name} />
      <a href={product.link} target="_blank" rel="noopener noreferrer">
        Buy Now
      </a>
      <button onClick={onBack}>Back</button>
    </div>
  );
}

export default ProductDetail;
