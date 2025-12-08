import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Package, MapPin, User, ShoppingBag } from 'lucide-react';

const KioskChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Welcome to Aditya Birla Fashion & Retail! I'm your in-store digital assistant. How may I help you today?",
      sender: 'bot',
      timestamp: '10:30 AM'
    },
    {
      id: 2,
      text: "I'm looking for casual shoes",
      sender: 'user',
      timestamp: '10:31 AM'
    },
    {
      id: 3,
      text: "Excellent choice! We have a wonderful collection of casual shoes from premium brands. Let me show you our top picks available in-store today.",
      sender: 'bot',
      timestamp: '10:31 AM'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Mock bot responses
  const mockBotResponses = [
    "I'd be happy to help you with that. Let me check our latest collection for you.",
    "That's a great choice! We have several options that match your preference.",
    "Our premium collection features top brands like Van Heusen, Allen Solly, and Louis Philippe.",
    "Would you like to see items available in your size and preferred color?",
    "I can help you find the perfect match. What's your budget range?",
    "Excellent! Let me find the best options for you from our in-store inventory."
  ];

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputText,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    // Show typing indicator
    setTimeout(() => {
      setIsTyping(true);
    }, 800);

    // Mock bot response after 1.5-2 seconds
    setTimeout(() => {
      setIsTyping(false);
      const randomResponse = mockBotResponses[Math.floor(Math.random() * mockBotResponses.length)];
      const botMessage = {
        id: Date.now() + 1,
        text: randomResponse,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: true 
        })
      };
      setMessages(prev => [...prev, botMessage]);
    }, 2000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action) => {
    const quickMessages = {
      browse: "Show me your latest products",
      track: "I want to track my order",
      availability: "Check product availability in store",
      expert: "I'd like to speak with a sales expert"
    };

    const message = quickMessages[action];
    setInputText(message);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header Bar - ABFRL Branding */}
      <div className="bg-gradient-to-r from-[#8B1538] to-[#A91D3A] text-white px-8 py-6 shadow-lg">
        <div className="flex items-center justify-between max-w-[1600px] mx-auto">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center shadow-md">
                <span className="text-3xl font-bold bg-gradient-to-br from-[#8B1538] to-[#D4AF37] bg-clip-text text-transparent">
                  AB
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-wide">Aditya Birla Fashion & Retail</h1>
                <p className="text-sm text-gray-200 font-light">In-Store Digital Assistant</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-white/10 rounded-full backdrop-blur-sm">
              <span className="text-sm font-medium">Store Open: 10 AM - 9 PM</span>
            </div>
          </div>
        </div>
        <div className="h-1 bg-gradient-to-r from-[#D4AF37] via-[#F5DEB3] to-[#D4AF37] mt-4 rounded-full opacity-80"></div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col max-w-[1600px] mx-auto w-full px-8 py-6">
        
        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto mb-6 px-4 space-y-4 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[60%] rounded-2xl px-6 py-4 shadow-md ${
                  message.sender === 'user'
                    ? 'bg-gradient-to-br from-[#8B1538] to-[#A91D3A] text-white'
                    : 'bg-white text-gray-800 border border-gray-100'
                }`}
              >
                <p className="text-base leading-relaxed mb-2">{message.text}</p>
                <div className={`text-xs ${
                  message.sender === 'user' ? 'text-gray-200' : 'text-gray-400'
                }`}>
                  {message.timestamp}
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl px-6 py-4 shadow-md border border-gray-100">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 bg-gradient-to-br from-[#8B1538] to-[#D4AF37] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-gradient-to-br from-[#8B1538] to-[#D4AF37] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-gradient-to-br from-[#8B1538] to-[#D4AF37] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Product Card Preview (Demo) */}
        <div className="mb-6 px-4">
          <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-lg border border-gray-200 p-6 max-w-md">
            <p className="text-sm font-semibold text-gray-600 mb-4">FEATURED PRODUCT</p>
            <div className="flex gap-4">
              <div className="w-32 h-32 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center">
                <ShoppingBag className="w-12 h-12 text-gray-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-800 mb-1">Premium Casual Shoes</h3>
                <p className="text-sm text-gray-600 mb-2">Van Heusen Collection</p>
                <p className="text-2xl font-bold bg-gradient-to-r from-[#8B1538] to-[#D4AF37] bg-clip-text text-transparent mb-3">
                  ₹4,999
                </p>
                <button className="w-full bg-gradient-to-r from-[#8B1538] via-[#D2691E] to-[#D4AF37] hover:from-[#7A1230] hover:via-[#C25A15] hover:to-[#C4A037] text-white font-semibold py-2 px-4 rounded-lg hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Action Buttons */}
        <div className="mb-4 px-4">
          <p className="text-sm font-semibold text-gray-600 mb-3">QUICK ACTIONS</p>
          <div className="grid grid-cols-4 gap-3">
            <button
              onClick={() => handleQuickAction('browse')}
              className="bg-gradient-to-br from-[#8B1538] via-[#D2691E] to-[#D4AF37] hover:from-[#7A1230] hover:via-[#C25A15] hover:to-[#C4A037] text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
            >
              <ShoppingBag className="w-5 h-5" />
              <span>Browse Products</span>
            </button>
            <button
              onClick={() => handleQuickAction('track')}
              className="bg-gradient-to-br from-[#8B1538] via-[#D2691E] to-[#D4AF37] hover:from-[#7A1230] hover:via-[#C25A15] hover:to-[#C4A037] text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
            >
              <Package className="w-5 h-5" />
              <span>Track Order</span>
            </button>
            <button
              onClick={() => handleQuickAction('availability')}
              className="bg-gradient-to-br from-[#8B1538] via-[#D2691E] to-[#D4AF37] hover:from-[#7A1230] hover:via-[#C25A15] hover:to-[#C4A037] text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
            >
              <MapPin className="w-5 h-5" />
              <span>Store Availability</span>
            </button>
            <button
              onClick={() => handleQuickAction('expert')}
              className="bg-gradient-to-br from-[#8B1538] via-[#D2691E] to-[#D4AF37] hover:from-[#7A1230] hover:via-[#C25A15] hover:to-[#C4A037] text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
            >
              <User className="w-5 h-5" />
              <span>Sales Expert</span>
            </button>
          </div>
        </div>

        {/* Input Area */}
        <div className="px-4">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4">
            <div className="flex items-center gap-4">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
                className="flex-1 bg-gray-50 rounded-xl px-6 py-4 outline-none text-base border border-gray-200 focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all"
              />
              <button
                className="bg-gray-100 hover:bg-gray-200 text-gray-600 p-4 rounded-xl transition-all duration-300"
                title="Voice input (Coming soon)"
              >
                <Mic className="w-6 h-6" />
              </button>
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim()}
                className={`bg-gradient-to-r from-[#8B1538] via-[#D2691E] to-[#D4AF37] text-white font-bold py-4 px-8 rounded-xl shadow-md transition-all duration-300 flex items-center gap-2 ${
                  inputText.trim()
                    ? 'hover:shadow-xl transform hover:scale-105 cursor-pointer hover:from-[#7A1230] hover:via-[#C25A15] hover:to-[#C4A037]'
                    : 'opacity-50 cursor-not-allowed'
                }`}
              >
                <Send className="w-5 h-5" />
                <span className="font-semibold">Send</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Need assistance? Our store staff is always here to help you • Powered by AI Sales Agent
          </p>
        </div>
      </div>
    </div>
  );
};

export default KioskChat;
