# Telephony Pricing Research Assignment

**Date:** November 16, 2025  
**Project:** Greek Dental Secretary Voice Agent  
**Goal:** Find the most cost-effective phone number service for production deployment

---

## 🎯 Your Task

Research and compare telephony providers that can give our voice agent a **Greek phone number** that patients can call. We need detailed pricing for incoming calls.

---

## 📋 Technical Requirements

### Must-Have Features

1. **Greek Phone Number (+30)**
   - Local Athens area code preferred (210 or 211)
   - OR toll-free Greek number (800)
   - Must look legitimate for a dental clinic

2. **SIP/WebRTC Compatibility**
   - Must work with **Pipecat framework** + **Daily.co transport**
   - SIP trunking support
   - WebRTC compatibility
   - Real-time audio streaming (no recording/playback)

3. **Incoming Call Support**
   - Patients call the number
   - Call routes to our voice AI agent
   - No human operator needed
   - Unlimited concurrent calls (or at least 5-10 simultaneous)

4. **Audio Quality**
   - 16kHz sample rate minimum
   - Low latency (<500ms)
   - Good audio quality for Greek language

5. **Geographic Availability**
   - Must support Greece (+30 numbers)
   - Incoming calls from Greek mobile/landline networks
   - International calling not required (Greece only)

---

## 🔍 Providers to Research

### Priority 1: Daily.co (Pipecat's Parent Company)

**What to find:**
- Daily PSTN pricing for Greece
- Greek phone number availability (+30)
- Setup fees, monthly fees, per-minute costs
- SIP integration with Pipecat Cloud
- Number provisioning time

**Where to look:**
- https://www.daily.co/pricing/
- https://docs.daily.co/reference/rest-api/telephony
- Contact Daily sales if pricing not public

**Questions to answer:**
- Can we get a Greek +30 number?
- Cost per incoming call minute?
- Monthly number rental fee?
- Setup/activation fees?
- Minimum commitment?

---

### Priority 2: Twilio

**What to find:**
- Twilio phone numbers for Greece
- Voice pricing (incoming calls)
- SIP trunking costs
- Integration with Pipecat/Daily

**Where to look:**
- https://www.twilio.com/en-us/voice/pricing/gr
- https://www.twilio.com/en-us/sip-trunking/pricing
- Twilio phone number pricing for Greece

**Questions to answer:**
- Greek phone number cost (monthly rental)?
- Incoming call cost per minute?
- SIP trunk fees?
- Can it forward to Daily.co/Pipecat?

---

### Priority 3: Vonage (formerly Nexmo)

**What to find:**
- Vonage Voice API pricing for Greece
- Greek virtual numbers
- SIP integration capabilities

**Where to look:**
- https://www.vonage.com/communications-apis/pricing/
- https://www.vonage.com/communications-apis/voice/
- Greek number availability

**Questions to answer:**
- Greek +30 number availability?
- Cost per incoming minute?
- Monthly number fee?
- WebRTC/SIP support?

---

### Priority 4: European/Greek Local Providers

**Providers to check:**
- **Plivo** (https://www.plivo.com/pricing/)
- **Bandwidth** (https://www.bandwidth.com/pricing/)
- **Telnyx** (https://telnyx.com/pricing)
- **SignalWire** (https://signalwire.com/pricing)

**What to find:**
- Which ones support Greek numbers?
- Incoming call pricing
- SIP/WebRTC compatibility
- Monthly fees vs pay-as-you-go

---

## 📊 Data to Collect

For each provider, fill out this table:

| Provider | Greek Number Available? | Monthly Rental | Setup Fee | Incoming $/min | Min Commitment | SIP Support | Notes |
|----------|------------------------|----------------|-----------|----------------|----------------|-------------|-------|
| Daily.co | ? | ? | ? | ? | ? | ✅ (native) | |
| Twilio | ? | ? | ? | ? | ? | ? | |
| Vonage | ? | ? | ? | ? | ? | ? | |
| Plivo | ? | ? | ? | ? | ? | ? | |
| Others | ? | ? | ? | ? | ? | ? | |

---

## 💰 Cost Scenarios to Calculate

Use these call volume projections:

### Scenario 1: Low Volume (100 calls/month)
- Average call duration: **3 minutes**
- Total minutes: **300 min/month**

Calculate for each provider:
```
Monthly cost = (Number rental) + (300 min × per-minute rate)
```

### Scenario 2: Medium Volume (500 calls/month)
- Average call duration: **3 minutes**
- Total minutes: **1,500 min/month**

Calculate:
```
Monthly cost = (Number rental) + (1,500 min × per-minute rate)
```

### Scenario 3: High Volume (2,000 calls/month)
- Average call duration: **3 minutes**
- Total minutes: **6,000 min/month**

Calculate:
```
Monthly cost = (Number rental) + (6,000 min × per-minute rate)
```

### Scenario 4: Enterprise (10,000 calls/month)
- Average call duration: **3 minutes**
- Total minutes: **30,000 min/month**

Calculate:
```
Monthly cost = (Number rental) + (30,000 min × per-minute rate)
```

---

## 🔧 Technical Integration Questions

For each provider, answer:

1. **Can it connect to Pipecat Cloud?**
   - Native integration?
   - SIP forwarding required?
   - Webhook/API setup needed?

2. **Setup complexity:**
   - How many steps to connect phone → Pipecat?
   - Configuration time estimate?
   - Technical expertise required?

3. **Latency:**
   - Expected round-trip latency
   - Geographic routing (Greece → where?)
   - Any Greece-specific infrastructure?

4. **Reliability:**
   - SLA uptime guarantee?
   - Redundancy/failover?
   - Known issues with Greek network operators?

---

## 📝 Output Format

Create a report with these sections:

### 1. Executive Summary
- Top 3 recommended providers
- Best for low volume (<500 calls/month)
- Best for high volume (>2,000 calls/month)
- Cheapest option
- Highest quality option

### 2. Detailed Comparison Table
- All providers with complete pricing
- Cost calculations for all 4 scenarios
- Feature comparison

### 3. Provider Deep-Dives
- One section per viable provider
- Pricing breakdown
- Integration steps
- Pros/cons
- Setup time estimate

### 4. Final Recommendation
- Which provider to use and why
- Expected monthly cost at our target volume (500 calls/month)
- Setup instructions overview
- Risk assessment

---

## 🚨 Critical Points

### Red Flags to Watch For:

- ❌ **No Greek number support** → eliminate immediately
- ❌ **Recording-only** (not real-time streaming) → won't work
- ❌ **High latency** (>1 second) → poor user experience
- ❌ **Requires dedicated server** (not cloud-compatible) → too complex
- ❌ **Minimum commitment >$100/month** → too expensive for testing

### Green Flags to Note:

- ✅ **Native Daily.co integration** → easiest setup
- ✅ **Pay-as-you-go pricing** → no commitment
- ✅ **WebRTC support** → modern, low latency
- ✅ **European data centers** → better latency for Greece
- ✅ **Free trial available** → can test before committing

---

## 📞 Expected Pricing Ranges (Estimates)

Based on industry standards, expect:

- **Phone number rental:** €2-10/month (~$2-12/month)
- **Incoming calls:** $0.005-0.04/minute
- **Setup fees:** $0-50 (one-time)

**Target:** Keep total cost under **$80/month** at 500 calls (1,500 minutes)

---

## ⏰ Timeline

- **Research deadline:** 2-3 hours
- **Expected deliverable:** Markdown report with all data
- **Next step:** We'll choose provider and set up integration

---

## 📚 Additional Resources

- **Pipecat Telephony Docs:** https://docs.pipecat.ai/guides/telephony
- **Daily Telephony Docs:** https://docs.daily.co/reference/rest-api/telephony
- **Greek Telecom Info:** Research Greek mobile operators (Cosmote, Vodafone, Wind) for compatibility

---

## ❓ Questions to Clarify

If you encounter these situations:

1. **Provider requires account to see pricing:**
   - Sign up for free trial/account
   - OR contact sales and ask directly
   - Get written pricing quote

2. **Greek numbers not listed:**
   - Check "Europe" or "International" sections
   - Contact support: "Do you support +30 Greek numbers?"
   - Check country code coverage

3. **Pricing unclear:**
   - Ask for pricing examples at 500, 2000, 10k calls/month
   - Request total cost breakdown (all fees included)

4. **Technical compatibility unclear:**
   - Ask: "Can I forward calls to a SIP endpoint?"
   - Ask: "Do you support WebRTC?"
   - Ask: "Can I integrate with Daily.co?"

---

## 🎯 Success Criteria

Your research is complete when you can answer:

✅ Which provider gives us a Greek phone number?  
✅ What's the total monthly cost at 500 calls/month?  
✅ How do we connect it to Pipecat Cloud?  
✅ Can we start with a trial/low-commitment plan?  
✅ What's the expected call quality/latency?

---

**Good luck! Let me know if you need any clarification.** 🚀
