import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import salesAgentService from '@/services/salesAgentService';
import sessionStore from '@/lib/session';
import Navbar from '@/components/Navbar.jsx';
import { resolveImageUrl } from '@/lib/utils.js';

const OrdersPage = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const customerId = sessionStore.getCustomerId();

  useEffect(() => {
    let mounted = true;
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await salesAgentService.getOrders(customerId);
        if (!mounted) return;
        setOrders(res.orders || res || []);
      } catch (e) {
        console.error('Failed to fetch orders', e);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetch();
    return () => { mounted = false; };
  }, [customerId]);

  const current = orders.filter(o => !['delivered', 'cancelled', 'returned'].includes((o.status || '').toLowerCase()));
  const delivered = orders.filter(o => (o.status || '').toLowerCase() === 'delivered');
  const cancelled = orders.filter(o => ['cancelled', 'returned'].includes((o.status || '').toLowerCase()));

  const getFirstItem = (order) => {
    const items = order.items || [];
    return items[0] || null;
  };

  const getItemCount = (order) => {
    const items = order.items || [];
    return items.length;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const OrderCard = ({ order }) => {
    const firstItem = getFirstItem(order);
    const itemCount = getItemCount(order);
    const status = (order.status || 'Processing').toLowerCase();
    
    const statusColors = {
      processing: 'bg-yellow-100 text-yellow-800',
      shipped: 'bg-blue-100 text-blue-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      returned: 'bg-gray-100 text-gray-800',
    };

    return (
      <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div className="flex gap-4">
          {/* Product Image */}
          <div className="flex-shrink-0 w-24 h-24 bg-gray-100 rounded-lg overflow-hidden">
            {firstItem?.image ? (
              <img 
                src={resolveImageUrl(firstItem.image)} 
                alt={firstItem.name || 'Product'} 
                className="w-full h-full object-cover"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
            )}
          </div>

          {/* Order Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <p className="font-semibold text-gray-900 truncate">
                  {firstItem?.name || firstItem?.sku || 'Order Item'}
                </p>
                {firstItem?.brand && (
                  <p className="text-xs text-gray-500">{firstItem.brand}</p>
                )}
                {itemCount > 1 && (
                  <p className="text-xs text-gray-500 mt-0.5">+{itemCount - 1} more item{itemCount > 2 ? 's' : ''}</p>
                )}
              </div>
              <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
                {order.status || 'Processing'}
              </span>
            </div>
            
            <div className="mt-2 flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500">Order {order.order_id || order.id}</p>
                {order.created_at && (
                  <p className="text-xs text-gray-400">{formatDate(order.created_at)}</p>
                )}
              </div>
              {order.total_amount && (
                <p className="font-semibold text-gray-900">₹{Number(order.total_amount).toLocaleString('en-IN')}</p>
              )}
            </div>

            <button 
              onClick={() => navigate(`/orders/${order.order_id || order.id}`)} 
              className="mt-3 w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Details
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 pt-28 pb-12">
        <h1 className="text-2xl font-bold mb-6">Your Orders</h1>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <p className="mt-4 text-gray-500">No orders yet</p>
            <button 
              onClick={() => navigate('/products')} 
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Start Shopping
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {current.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold mb-3 text-gray-800">Current Orders ({current.length})</h2>
                <div className="space-y-4">
                  {current.map((o) => (
                    <OrderCard key={o.order_id || o.id} order={o} />
                  ))}
                </div>
              </section>
            )}

            {delivered.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold mb-3 text-gray-800">Delivered ({delivered.length})</h2>
                <div className="space-y-4">
                  {delivered.map((o) => (
                    <OrderCard key={o.order_id || o.id} order={o} />
                  ))}
                </div>
              </section>
            )}

            {cancelled.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold mb-3 text-gray-800">Cancelled / Returned ({cancelled.length})</h2>
                <div className="space-y-4">
                  {cancelled.map((o) => (
                    <OrderCard key={o.order_id || o.id} order={o} />
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrdersPage;
