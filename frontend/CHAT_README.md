# WhatsApp-Style Chat UI

## 📱 Overview
A fully functional WhatsApp-style chat interface for the AI Sales Agent system. This is a **frontend-only** implementation with mocked responses, ready for future backend integration.

## ✨ Features

### UI Components
- **WhatsApp-like Layout**
  - Green header with agent info and online status
  - Scrollable chat message area with patterned background
  - Bottom input bar with emoji, voice, and send buttons
  
### Message Features
- **User Messages**: Right-aligned with light green bubbles (`#d9fdd3`)
- **Agent Messages**: Left-aligned with white bubbles
- **Timestamps**: Display time for each message
- **Message Status**: 
  - ✓ Sent (gray single check)
  - ✓✓ Delivered (gray double check)
  - ✓✓ Read (blue double check)

### Interactions
- **Typing Indicator**: Animated dots showing "agent is typing"
- **Auto-scroll**: Messages automatically scroll to bottom
- **Mock Responses**: Agent replies after 1-1.5 seconds with random responses
- **Keyboard Support**: Press Enter to send message

### Design
- **WhatsApp Color Scheme**:
  - Header: `#008069` (WhatsApp green)
  - User bubbles: `#d9fdd3` (light green)
  - Agent bubbles: `#ffffff` (white)
  - Background: `#efeae2` (light beige)
  - Online indicator: `#25d366` (bright green)

- **Responsive**:
  - Mobile: Full width messages
  - Tablet: 75% max-width messages
  - Desktop: 65% max-width messages

## 🚀 Usage

### Access the Chat
1. Start the development server:
   ```bash
   npm run dev
   ```

2. Navigate to:
   - Homepage: `http://localhost:5173/`
   - Chat: `http://localhost:5173/chat`

### From Homepage
Click the **"Open AI Sales Chat"** button to enter the chat interface.

## 🔧 Technical Details

### Tech Stack
- **React 19** with hooks (useState, useRef, useEffect)
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Framer Motion** (available for future animations)

### File Structure
```
frontend/src/
├── components/
│   └── Chat.jsx          # Main chat component
├── App.jsx               # Router and navigation
└── ...
```

### Mock Responses
The chat simulates agent responses from a predefined list:
- "Sure! Let me check the best options for you."
- "I found some great products that match your preferences!"
- "Would you like me to show you our top recommendations?"
- "I can help you with that. What's your budget?"
- "Great choice! Let me find similar items for you."
- "I'm checking our inventory for you..."
- "Based on your preferences, I have some perfect options!"

## 🔌 Future Backend Integration

### Ready for FastAPI Connection
The component is structured to easily integrate with the backend:

```javascript
// TODO: Replace mock responses with actual API calls
const handleSendMessage = async () => {
  // Current: Mock response
  // Future: 
  /*
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      message: inputText,
      customer_id: 'user_123',
      session_id: sessionId
    })
  });
  const data = await response.json();
  setMessages(prev => [...prev, {
    id: Date.now(),
    text: data.response,
    sender: 'agent',
    timestamp: new Date().toLocaleTimeString(),
    status: 'read'
  }]);
  */
};
```

### Planned Integrations
1. **WebSocket**: Real-time message delivery
2. **Authentication**: Customer session management
3. **Sales Agent API**: Connect to FastAPI backend
4. **LangGraph**: Multi-agent workflow integration
5. **Product Recommendations**: Display product cards in chat
6. **Order Status**: Check inventory and order tracking
7. **Payment Flow**: Integrate payment processing

## 🎨 Customization

### Colors
Edit the color values in `Chat.jsx`:
```javascript
// Header
bg-[#008069]

// User messages
bg-[#d9fdd3]

// Agent messages
bg-white

// Background
bg-[#efeae2]
```

### Mock Responses
Add/edit responses in the `mockAgentResponses` array:
```javascript
const mockAgentResponses = [
  "Your custom response here",
  // ...
];
```

### Timing
Adjust response delays:
```javascript
setTimeout(() => setIsTyping(true), 1200);  // Show typing indicator
setTimeout(() => { /* send response */ }, 1500);  // Send reply
```

## 📱 Responsive Behavior

- **Mobile (< 768px)**: Full-width input, compact header
- **Tablet (768px - 1024px)**: 75% message width
- **Desktop (> 1024px)**: 65% message width, spacious layout

## 🐛 Known Limitations

- No backend connection (mock responses only)
- No message persistence (refreshing clears chat)
- No authentication/user sessions
- No file/image upload (UI elements present but not functional)
- No emoji picker implementation

## 📝 Future Enhancements

- [ ] WebSocket connection for real-time chat
- [ ] Message persistence (localStorage/backend)
- [ ] File upload support
- [ ] Emoji picker implementation
- [ ] Voice message recording
- [ ] Product card components in chat
- [ ] Typing indicator based on actual backend status
- [ ] Message search functionality
- [ ] Chat history/conversation list
- [ ] Customer profile integration

## 🤝 Contributing

When adding backend integration:
1. Keep the mock responses as fallback
2. Add loading states for API calls
3. Handle errors gracefully
4. Maintain the WhatsApp-style UX
5. Test responsive behavior

---

Built with ❤️ for EY CodeCrafters
