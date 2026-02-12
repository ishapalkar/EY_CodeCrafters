# Omni-Channel Refactoring Plan - Implementation Progress

## 🎯 Priority Matrix

### PRIORITY 1: Fix Immediate Issues (Critical)
- [ ] Add detailed logging to kiosk session creation
- [ ] Fix session structure for proper metadata
- [ ] Remove short TTL logic from session expiry
- [ ] Ensure customer_id is properly set in all flows

### PRIORITY 2: Supabase Integration (High)
- [ ] Add Supabase connection to session_manager.py
- [ ] Migrate sessions store from in-memory to Supabase
- [ ] Implement sliding 7-day expiry 
- [ ] Add omni-channel session continuity (@app routes)

### PRIORITY 3: Authentication Endpoints (High)
- [ ] Create /auth/login endpoint (phone+password)
- [ ] Create /auth/signup endpoint (full customer profile)
- [ ] Create /auth/logout endpoint
- [ ] Implement WhatsApp phone-only override in /session/login

### PRIORITY 4: Sales Agent Memory (Medium)
- [ ] Fetch session.metadata.chat_context in sales_graph.py
- [ ] Add conversation_summary to session metadata
- [ ] Fetch purchase_history and loyalty_tier for context
- [ ] Add persuasive follow-up logic

### PRIORITY 5: QR Authentication (Low - Postponed)
- [ ] QR login support can wait until main flow is stable

## 🗂️ Implementation Order

1. **Phase 1:** Add logging + fix session structure (PRIORITY 1)
   - Target: Identify kiosk error root cause
   - Time: 30 mins
   
2. **Phase 2:** Supabase integration (PRIORITY 2)
   - Target: Persistent sessions + proper expiry
   - Time: 1.5 hours
   
3. **Phase 3:** Auth endpoints (PRIORITY 3)
   - Target: Separate login/signup flows
   - Time: 1 hour
   
4. **Phase 4:** Sales agent memory (PRIORITY 4)
   - Target: Contextual + persuasive responses
   - Time: 45 mins
   
5. **Phase 5:** Testing + Port verification
   - Target: All tests pass, no port conflicts
   - Time: 30 mins

## 📋 Constraints (Hard Requirements)
✅ DO NOT break existing functionality
✅ DO NOT change ports
✅ DO NOT use port 5000
✅ Extend session_manager.py (don't replace)
✅ Sessions ONLY in Supabase (no CSV)
✅ Keep CSV fallback for products/customers
✅ No new frameworks
✅ All changes backward compatible

## 🚀 Starting Phase 1 Now
