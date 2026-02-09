import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '@/contexts/CartContext.jsx';
import { ShoppingCart, Trash2, Plus, Minus, ArrowLeft } from 'lucide-react';
import inventoryService from '@/services/inventoryService';

const CartPage = () => {
  const navigate = useNavigate();
  const {
    cartItems,
    removeFromCart,
    updateQuantity,
    getCartTotal,
    getCartCount,
    updateItemMetadata,
  } = useCart();
  const [reserveLoading, setReserveLoading] = useState({});
  const [reserveFeedback, setReserveFeedback] = useState({});
  const [storeOptions, setStoreOptions] = useState({});
  const [selectedStore, setSelectedStore] = useState({});

  const formatINR = (amount) => {
    return amount.toLocaleString('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
    });
  };

  const resetReservationMetadata = (sku) => {
    updateItemMetadata(sku, {
      reservationStatus: 'idle',
      reservationHoldId: null,
      reservationExpiresAt: null,
      reservationLocation: null,
      reservedQuantity: 0,
    });
  };

  const handleReleaseReservation = async (item) => {
    if (!item.reservationHoldId) {
      resetReservationMetadata(item.sku);
      return;
    }

    try {
      await inventoryService.releaseInventory(item.reservationHoldId);
      setReserveFeedback((prev) => ({
        ...prev,
        [item.sku]: 'Reservation released',
      }));
    } catch (error) {
      console.error('Failed to release reservation:', error);
      setReserveFeedback((prev) => ({
        ...prev,
        [item.sku]: 'Could not release reservation. Please try again.',
      }));
    } finally {
      resetReservationMetadata(item.sku);
    }
  };

  const handleReserveInStore = async (item) => {
    if (!item || item.qty <= 0) return;

    setReserveLoading((prev) => ({ ...prev, [item.sku]: true }));
    // Decide best location to reserve from: prefer user-selected store, else seeded STORE_MUMBAI, else find matching store
    let location = 'store:STORE_MUMBAI';
    try {
      const inventorySnapshot = await inventoryService.getInventory(item.sku);
      // Find a store with enough stock
      const stores = inventorySnapshot.store_stock || {};
      const userSelected = selectedStore[item.sku];
      if (userSelected) {
        location = userSelected === 'online' ? 'online' : `store:${userSelected}`;
      } else {
        const matchingStore = Object.keys(stores).find((s) => stores[s] >= item.qty);
        if (matchingStore) {
          location = `store:${matchingStore}`;
        } else if ((inventorySnapshot.online_stock || 0) >= item.qty) {
          location = 'online';
        }
      }

      // If no suitable store/online stock, we'll still attempt and let server respond with 409
      if (item.reservationHoldId) {
        await inventoryService.releaseInventory(item.reservationHoldId);
      }

      
      const response = await inventoryService.holdInventory({
        sku: item.sku,
        quantity: item.qty,
        location,
        ttl: 1800,
      });

      updateItemMetadata(item.sku, {
        reservationStatus: 'reserved',
        reservationHoldId: response.hold_id,
        reservationExpiresAt: response.expires_at,
        reservationLocation: location,
        reservedQuantity: item.qty,
      });

      setReserveFeedback((prev) => ({
        ...prev,
        [item.sku]: 'Your product is reserved in store.',
      }));
    } catch (error) {
      console.error('Reservation failed:', error);

      // If server responded with 409, fetch inventory levels and show helpful guidance
      if (error && error.status === 409) {
        try {
          const inventory = await inventoryService.getInventory(item.sku);
          const stores = inventory.store_stock || {};
          const storeEntries = Object.entries(stores)
            .filter(([, qty]) => qty > 0)
            .sort((a, b) => b[1] - a[1]);

          let suggestion;
          if (storeEntries.length > 0) {
            // show top 2 stores with availability
            const top = storeEntries.slice(0, 2).map(([s, q]) => `${s} (${q})`).join(', ');
            suggestion = `Not enough stock at the selected location. Available at: ${top}.`;
          } else if ((inventory.online_stock || 0) > 0) {
            suggestion = `No stock in stores for this SKU. ${inventory.online_stock} available online.`;
          } else {
            suggestion = 'Product is out of stock.';
          }

          setReserveFeedback((prev) => ({
            ...prev,
            [item.sku]: suggestion,
          }));
        } catch (e) {
          setReserveFeedback((prev) => ({
            ...prev,
            [item.sku]: 'Unable to reserve product. Please try again.',
          }));
        }
      } else {
        setReserveFeedback((prev) => ({
          ...prev,
          [item.sku]: error.message || 'Unable to reserve product. Please try again.',
        }));
      }

      resetReservationMetadata(item.sku);
    } finally {
      setReserveLoading((prev) => ({ ...prev, [item.sku]: false }));
    }
  };

  const handleQuantityChange = async (item, newQty) => {
    if (newQty <= 0) {
      await handleRemove(item);
      return;
    }

    if (item.reservationHoldId) {
      await handleReleaseReservation(item);
    }

    updateQuantity(item.sku, newQty);
  };

  // Fetch store options for cart items so users can pick a store to reserve from
  useEffect(() => {
    let mounted = true;
    const fetchOptions = async () => {
      const skus = cartItems.map((c) => c.sku);
      const nextOptions = {};
      const nextSelected = {};

      await Promise.all(
        skus.map(async (sku) => {
          try {
            const inv = await inventoryService.getInventory(sku);
            const stores = inv.store_stock ? Object.keys(inv.store_stock) : [];
            nextOptions[sku] = stores;
            // prefer seeded STORE_MUMBAI if present, else first store, else 'online'
            if (stores.includes('STORE_MUMBAI')) nextSelected[sku] = 'STORE_MUMBAI';
            else if (stores.length > 0) nextSelected[sku] = stores[0];
            else nextSelected[sku] = inv.online_stock > 0 ? 'online' : 'STORE_MUMBAI';
          } catch (e) {
            // ignore per-sku failures
          }
        })
      );

      if (!mounted) return;
      setStoreOptions((prev) => ({ ...prev, ...nextOptions }));
      setSelectedStore((prev) => ({ ...prev, ...nextSelected }));
    };

    if (cartItems.length > 0) fetchOptions();
    return () => {
      mounted = false;
    };
  }, [cartItems]);

  const handleRemove = async (item) => {
    if (item.reservationHoldId) {
      await handleReleaseReservation(item);
    }
    removeFromCart(item.sku);
  };

  const handleCheckout = () => {
    if (cartItems.length === 0) return;
    navigate('/checkout');
  };

  const isReservationFresh = (item) => {
    return (
      item.reservationStatus === 'reserved' &&
      item.reservationHoldId &&
      item.reservedQuantity === item.qty
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-yellow-50 to-red-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white shadow-md">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="hover:bg-white/10 p-2 rounded-full transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div className="flex items-center gap-3">
              <ShoppingCart className="w-8 h-8" />
              <div>
                <h1 className="text-2xl font-bold">Your Cart</h1>
                <p className="text-sm text-orange-100">
                  {getCartCount()} {getCartCount() === 1 ? 'item' : 'items'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cart Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {cartItems.length === 0 ? (
          <div className="text-center py-16">
            <ShoppingCart className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">Your cart is empty</h2>
            <p className="text-gray-500 mb-6">Add some products to get started!</p>
            <button
              onClick={() => navigate('/chat')}
              className="bg-gradient-to-r from-red-600 to-orange-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-red-700 hover:to-orange-700 transition-all"
            >
              Start Shopping
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Cart Items */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              {cartItems.map((item, idx) => (
                <div
                  key={item.sku}
                  className={`p-6 flex gap-4 ${idx !== 0 ? 'border-t border-gray-200' : ''}`}
                >
                  {/* Product Image */}
                  {item.image && (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-24 h-24 object-cover rounded-lg"
                      onError={(e) => (e.target.style.display = 'none')}
                    />
                  )}

                  {/* Product Details */}
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900">{item.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">SKU: {item.sku}</p>
                    <p className="text-lg font-bold text-green-600 mt-2">
                      {formatINR(item.unit_price)}
                    </p>

                    {/* Quantity Controls */}
                    <div className="flex items-center gap-4 mt-4">
                      <div className="flex items-center gap-2 border border-gray-300 rounded-lg">
                        <button
                          onClick={() => handleQuantityChange(item, item.qty - 1)}
                          className="p-2 hover:bg-gray-100 transition-colors rounded-l-lg"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="px-4 font-semibold">{item.qty}</span>
                        <button
                          onClick={() => handleQuantityChange(item, item.qty + 1)}
                          className="p-2 hover:bg-gray-100 transition-colors rounded-r-lg"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>

                      <button
                        onClick={() => handleRemove(item)}
                        className="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="mt-4 space-y-2">
                        {/* Store selector for reservation */}
                        <div className="flex items-center gap-2">
                          {storeOptions[item.sku] && storeOptions[item.sku].length > 0 ? (
                            <select
                              value={selectedStore[item.sku] || ''}
                              onChange={(e) =>
                                setSelectedStore((prev) => ({ ...prev, [item.sku]: e.target.value }))
                              }
                              className="border px-3 py-2 rounded-md text-sm"
                            >
                              {storeOptions[item.sku].map((s) => (
                                <option key={s} value={s}>
                                  {s}
                                </option>
                              ))}
                              <option value="online">Online</option>
                            </select>
                          ) : (
                            <span className="text-sm text-gray-500">Select store at reserve</span>
                          )}
                        </div>
                      <button
                        onClick={() => handleReserveInStore(item)}
                        disabled={reserveLoading[item.sku] || isReservationFresh(item)}
                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                          isReservationFresh(item)
                            ? 'bg-green-100 text-green-700 cursor-default'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        } ${reserveLoading[item.sku] ? 'opacity-70 cursor-wait' : ''}`}
                      >
                        {isReservationFresh(item)
                          ? 'Reserved in Store'
                          : reserveLoading[item.sku]
                          ? 'Reserving...'
                          : 'Reserve in Store'}
                      </button>

                      {reserveFeedback[item.sku] && (
                        <p className="text-sm text-gray-600">{reserveFeedback[item.sku]}</p>
                      )}

                      {item.reservationStatus === 'reserved' && !isReservationFresh(item) && (
                        <p className="text-sm text-orange-600">
                          Reservation covers {item.reservedQuantity} item(s). Update reservation to match current quantity.
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Item Total */}
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Total</p>
                    <p className="text-xl font-bold text-gray-900">
                      {formatINR(item.unit_price * item.qty)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Cart Summary */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-gray-700">
                  <span>Subtotal ({getCartCount()} items)</span>
                  <span className="font-semibold">{formatINR(getCartTotal())}</span>
                </div>
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-lg font-bold text-gray-900">
                    <span>Total</span>
                    <span className="text-green-600">{formatINR(getCartTotal())}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                className="w-full bg-gradient-to-r from-red-600 to-orange-600 text-white py-4 rounded-lg font-bold text-lg hover:from-red-700 hover:to-orange-700 transition-all shadow-lg hover:shadow-xl"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;
