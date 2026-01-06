import React from 'react';
import { X } from 'lucide-react';

const ProductCard = ({ product, onAddToCart, canAddToCart = true }) => {
  const mainImage = product.images && product.images.length > 0 ? product.images[0] : 'https://via.placeholder.com/400x300?text=No+Image';

  return (
    <div className="luxury-card group" data-testid="product-card">
      <div className="relative overflow-hidden rounded-lg mb-4 aspect-[4/3]">
        <img
          src={mainImage}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
          }}
        />
        {product.users?.verificationStatus === 'verified' && (
          <div className="absolute top-2 right-2 bg-green-500/20 backdrop-blur-sm border border-green-500/30 px-2 py-1 rounded-full">
            <span className="text-green-400 text-xs font-semibold">Verified Seller</span>
          </div>
        )}
      </div>

      <h3 className="font-['Playfair_Display'] text-xl font-semibold text-white mb-2" data-testid="product-title">
        {product.title}
      </h3>

      <p className="text-gray-400 text-sm line-clamp-2 mb-4" data-testid="product-description">
        {product.description}
      </p>

      <div className="flex items-center justify-between">
        <div>
          <span className="text-2xl font-bold text-[#D4AF37]" data-testid="product-price">
            ${product.price.toFixed(2)}
          </span>
          {product.users?.name && (
            <p className="text-gray-500 text-xs mt-1">by {product.users.name}</p>
          )}
        </div>

        {canAddToCart && (
          <button
            onClick={() => onAddToCart(product)}
            className="btn-gold text-sm px-4 py-2"
            data-testid="add-to-cart-btn"
          >
            Add to Cart
          </button>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
