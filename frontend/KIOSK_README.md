# ABFRL Kiosk-Style Chat Interface

## 🎨 Brand Identity Implementation

### ABFRL Color Palette (Exact Match)
```
Primary Colors:
- Deep Maroon Red: #8B1538 (dominant brand color)
- Accent Maroon: #A91D3A (gradient blend)
- Warm Gold: #D4AF37 (highlight color)
- Light Gold: #F5DEB3 (gradient blend)

Background Colors:
- White/Off-White: #FFFFFF, #FAFAFA
- Light Gray: #F5F5F5, #E5E5E5
- Charcoal: #2C2C2C (for contrast)

Gradient Combinations:
- Header: from-[#8B1538] to-[#A91D3A]
- Gold Accent: from-[#D4AF37] to-[#F5DEB3]
- User Message: from-[#8B1538] to-[#A91D3A]
```

## 🖥️ Kiosk UI Layout

### 1. Header Bar
- **Background**: Maroon to Red gradient (`#8B1538` → `#A91D3A`)
- **Logo**: White rounded square with "AB" gradient text
- **Title**: "Aditya Birla Fashion & Retail"
- **Subtitle**: "In-Store Digital Assistant"
- **Gold Accent Line**: Gradient line below header
- **Store Hours**: Displayed in top-right corner

### 2. Chat Area
**Bot Messages (Left-aligned)**:
- White background (`#FFFFFF`)
- Soft gray border (`border-gray-100`)
- Rounded corners (20px)
- Text: Dark gray (`text-gray-800`)
- Shadow: Medium (`shadow-md`)

**User Messages (Right-aligned)**:
- Maroon gradient background (`from-[#8B1538] to-[#A91D3A]`)
- White text
- Rounded corners (20px)
- Shadow: Medium (`shadow-md`)

**Typing Indicator**:
- Three animated dots
- Gradient colors (maroon to gold)
- Smooth bounce animation

### 3. Product Card (Preview)
- White to light gray gradient background
- Square image placeholder (128x128px)
- Brand name and product title
- Price in ₹ with maroon-gold gradient
- Gold "View Details" button
- Hover effects: Scale + shadow increase

### 4. Quick Action Buttons
Four gold buttons with icons:
- **Browse Products** (ShoppingBag icon)
- **Track Order** (Package icon)
- **Store Availability** (MapPin icon)
- **Sales Expert** (User icon)

Style:
- Background: Gold gradient (`from-[#D4AF37] to-[#F5DEB3]`)
- Text: Dark gray/black
- Hover: Scale 1.05 + shadow increase
- Rounded: 12px

### 5. Input Area
- Large white rounded container
- Gray input field with gold focus ring
- Microphone button (gray, hover effect)
- Gold "Send" button with icon
- Disabled state when input empty

## ✨ Key Features

### Visual Design
- ✅ Premium luxury retail look
- ✅ Smooth gradients (no harsh colors)
- ✅ Rounded cards and soft shadows
- ✅ Corporate/professional aesthetic
- ✅ High contrast for readability
- ✅ Touch-friendly large buttons

### Interactions
- ✅ Mock conversation pre-loaded
- ✅ Auto-scroll to latest message
- ✅ Typing indicator animation
- ✅ Quick action button clicks populate input
- ✅ Enter key to send
- ✅ Hover effects on all interactive elements

### Responsive Design
- Optimized for **landscape kiosk screens**
- Max-width: 1600px (centered)
- Works on desktop/laptop browsers
- Touch-friendly sizing

## 🚀 Usage

### Access the Kiosk
1. Start dev server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Navigate to:
   - Homepage: `http://localhost:5173/`
   - Kiosk Chat: `http://localhost:5173/kiosk`

### From Homepage
Click the **"ABFRL Kiosk Chat"** button (maroon-gold gradient).

## 📱 Demo Conversation

Pre-loaded messages:
1. **Bot**: "Welcome to Aditya Birla Fashion & Retail! I'm your in-store digital assistant. How may I help you today?"
2. **User**: "I'm looking for casual shoes"
3. **Bot**: "Excellent choice! We have a wonderful collection of casual shoes from premium brands. Let me show you our top picks available in-store today."

Mock responses rotate through:
- "I'd be happy to help you with that. Let me check our latest collection for you."
- "That's a great choice! We have several options that match your preference."
- "Our premium collection features top brands like Van Heusen, Allen Solly, and Louis Philippe."
- "Would you like to see items available in your size and preferred color?"
- "I can help you find the perfect match. What's your budget range?"
- "Excellent! Let me find the best options for you from our in-store inventory."

## 🎯 Design Goals Achieved

### ✅ Looks Like
- High-end fashion retail kiosk
- Mall digital assistant screen
- Luxury in-store touchscreen
- Premium brand experience

### ❌ Does NOT Look Like
- WhatsApp chat
- Customer support widget
- Gaming interface
- Casual mobile app

## 🔧 Technical Details

### Tech Stack
- React 19 with hooks
- Tailwind CSS (custom gradients)
- Lucide React icons
- Framer Motion ready

### File Structure
```
frontend/src/
├── components/
│   ├── Chat.jsx          # WhatsApp-style chat
│   └── KioskChat.jsx     # ABFRL kiosk (NEW)
├── App.jsx               # Router with /kiosk route
└── index.css             # Custom scrollbar styles
```

### Key Components
```javascript
// Message state
const [messages, setMessages] = useState([...]);

// Typing indicator
const [isTyping, setIsTyping] = useState(false);

// Auto-scroll
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [messages, isTyping]);

// Mock responses (1.5-2 second delay)
setTimeout(() => {
  setIsTyping(false);
  // Add bot message
}, 2000);
```

## 🔌 Future Backend Integration

### Planned Connections
```javascript
// TODO: Replace mock with actual API
const handleSendMessage = async () => {
  /*
  const response = await fetch('http://localhost:8000/kiosk/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: inputText,
      store_id: 'STORE_001',
      session_id: sessionId
    })
  });
  const data = await response.json();
  // Update messages with response
  */
};
```

### Integration Points
1. **Sales Agent API**: Connect to FastAPI backend
2. **Product Search**: Real-time inventory lookup
3. **Store Availability**: Check local stock
4. **Order Tracking**: Customer order status
5. **Expert Connect**: Queue for human agent
6. **Analytics**: Track kiosk usage patterns
7. **Session Management**: Customer identification

## 🎨 Customization Guide

### Colors
Edit gradient values in `KioskChat.jsx`:
```javascript
// Header gradient
className="bg-gradient-to-r from-[#8B1538] to-[#A91D3A]"

// User message gradient
className="bg-gradient-to-br from-[#8B1538] to-[#A91D3A]"

// Gold button gradient
className="bg-gradient-to-br from-[#D4AF37] to-[#F5DEB3]"
```

### Branding
Update logo and text:
```javascript
<div className="w-16 h-16 bg-white rounded-lg">
  <span className="text-3xl font-bold">AB</span>
</div>
<h1>Aditya Birla Fashion & Retail</h1>
<p>In-Store Digital Assistant</p>
```

### Quick Actions
Add/modify buttons:
```javascript
const quickActions = {
  newAction: "Your action message",
  // ...
};

<button onClick={() => handleQuickAction('newAction')}>
  <Icon className="w-5 h-5" />
  <span>Action Label</span>
</button>
```

### Timing
Adjust response delays:
```javascript
setTimeout(() => setIsTyping(true), 800);   // Show typing
setTimeout(() => { /* send reply */ }, 2000); // Send response
```

## 📐 Layout Specifications

### Spacing
- Container max-width: 1600px
- Padding: 32px (px-8)
- Message gap: 16px (space-y-4)
- Button gap: 12px (gap-3)

### Typography
- Header title: 2xl (24px), bold
- Message text: base (16px)
- Timestamp: xs (12px)
- Button text: base (16px), semibold

### Shadows
- Card shadow: shadow-md (medium)
- Hover shadow: shadow-xl (extra large)
- Header shadow: shadow-lg (large)

### Border Radius
- Chat bubbles: 20px (rounded-2xl)
- Buttons: 12px (rounded-xl)
- Input field: 12px (rounded-xl)
- Cards: 16px (rounded-2xl)

## 🐛 Known Limitations

- No real backend connection (mock only)
- No persistent session storage
- Microphone button non-functional (visual only)
- No actual product data
- No authentication/customer ID
- No multi-language support

## 📝 Future Enhancements

- [ ] WebSocket for real-time responses
- [ ] Product carousel in chat
- [ ] Voice input implementation
- [ ] QR code scanner for product lookup
- [ ] Store map integration
- [ ] Virtual try-on integration
- [ ] Payment gateway in chat
- [ ] Loyalty points display
- [ ] Personalized recommendations
- [ ] Multi-brand selection (ABFRL portfolio)
- [ ] Size finder assistant
- [ ] Style advisor mode

## 🏪 ABFRL Brand Portfolio

Can be extended to support:
- **Van Heusen**
- **Louis Philippe**
- **Allen Solly**
- **Peter England**
- **American Eagle**
- **Forever 21**
- **Pantaloons**

## 🤝 Contributing

When adding features:
1. Maintain ABFRL color scheme
2. Keep premium luxury aesthetic
3. Test on large touchscreens
4. Ensure accessibility (contrast, sizing)
5. Add loading states for async operations
6. Handle errors gracefully
7. Document all new features

---

Built for **EY CodeCrafters** x **Aditya Birla Fashion & Retail**
Premium In-Store Digital Experience 🏬✨
