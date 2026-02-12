import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import salesAgentService from '@/services/salesAgentService';
import sessionStore from '@/lib/session';
import Navbar from '@/components/Navbar.jsx';
import { resolveImageUrl } from '@/lib/utils.js';

const OrderDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const customerId = sessionStore.getCustomerId();

  useEffect(() => {
    let mounted = true;
    const fetchOrder = async () => {
      setLoading(true);
      try {
        const res = await salesAgentService.getOrders(customerId);
        const list = res.orders || res || [];
        const found = list.find(o => (o.order_id || o.id) === id);
        if (mounted) setOrder(found || { order_id: id, items: [] });
      } catch (e) {
        console.error('Failed to fetch order', e);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchOrder();
    return () => { mounted = false; };
  }, [id, customerId]);

  const requestStyling = () => {
    if (!order || !order.items || order.items.length === 0) {
      alert('No items in order to style');
      return;
    }
    // Navigate to chat with stylist context
    const firstItem = order.items[0];
    navigate('/chat', {
      state: {
        stylistRequest: true,
        orderId: order.order_id || order.id,
        orderItems: order.items,
        product: {
          sku: firstItem.sku,
          name: firstItem.name || firstItem.sku,
          category: firstItem.category || 'Apparel',
          color: firstItem.color || null,
          brand: firstItem.brand || null
        }
      }
    });
  };

  const openPostPurchase = () => {
    // Navigate to chat with post-purchase context and options
    const orderItems = (order.items || []).map(it => ({
      sku: it.sku,
      name: it.name || it.sku,
      brand: it.brand || null,
      category: it.category || 'Apparel',
      quantity: it.qty || 1,
      unit_price: it.unit_price || 0,
      line_total: (it.unit_price || 0) * (it.qty || 1)
    }));
    
    navigate('/chat', {
      state: {
        postPurchaseRequest: true,
        orderId: order.order_id || order.id,
        userId: customerId || 'guest',
        amount: order.total_amount || orderItems.reduce((sum, it) => sum + it.line_total, 0),
        orderItems: orderItems,
        orderStatus: order.status || 'completed'
      }
    });
  };

  const formatPrice = (price) => {
    if (!price) return '';
    return `₹${Number(price).toLocaleString('en-IN')}`;
  };

  const statusColors = {
    processing: 'bg-yellow-100 text-yellow-800',
    shipped: 'bg-blue-100 text-blue-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    returned: 'bg-gray-100 text-gray-800',
  };

  const status = (order?.status || 'processing').toLowerCase();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 pt-28 pb-12">
        <button onClick={() => navigate('/orders')} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 mb-4">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to orders
        </button>
        
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            {/* Order Header */}
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Order {order?.order_id || id}</h2>
                {order?.created_at && (
                  <p className="text-sm text-gray-500 mt-1">
                    Placed on {new Date(order.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                  </p>
                )}
              </div>
              <span className={`px-3 py-1 text-sm font-medium rounded-full capitalize ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
                {order?.status || 'Processing'}
              </span>
            </div>

            {/* Order Items */}
            <div className="space-y-4 mb-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Items ({(order?.items || []).length})</h3>
              {(order?.items || []).map((it, idx) => (
                <div key={it.sku || idx} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
                  {/* Product Image */}
                  <div className="flex-shrink-0 w-20 h-20 bg-white rounded-lg overflow-hidden border border-gray-200">
                    {it.image ? (
                      <img 
                        src={resolveImageUrl(it.image)} 
                        alt={it.name || 'Product'} 
                        className="w-full h-full object-cover"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Product Details */}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900">{it.name || it.sku}</p>
                    {it.brand && <p className="text-sm text-gray-500">{it.brand}</p>}
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                      {it.category && <span>{it.category}</span>}
                      {it.color && <span>• {it.color}</span>}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">SKU: {it.sku}</p>
                  </div>

                  {/* Quantity & Price */}
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{formatPrice(it.line_total || it.unit_price)}</p>
                    <p className="text-sm text-gray-500">Qty: {it.qty || 1}</p>
                    {it.unit_price && <p className="text-xs text-gray-400">{formatPrice(it.unit_price)} each</p>}
                  </div>
                </div>
              ))}
            </div>

            {/* Order Total */}
            {order?.total_amount && (
              <div className="flex justify-between items-center py-4 border-t border-gray-200 mb-6">
                <span className="text-lg font-semibold text-gray-700">Total</span>
                <span className="text-xl font-bold text-gray-900">{formatPrice(order.total_amount)}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3">
              <button 
                onClick={openPostPurchase} 
                className="flex-1 sm:flex-none px-6 py-3 bg-yellow-500 text-white font-medium rounded-lg hover:bg-yellow-600 transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                Post-Purchase Support
              </button>
              <button 
                onClick={requestStyling} 
                className="flex-1 sm:flex-none px-6 py-3 bg-pink-500 text-white font-medium rounded-lg hover:bg-pink-600 transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Ask Stylist
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderDetailPage;
