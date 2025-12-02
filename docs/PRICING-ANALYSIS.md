# Pricing Analysis for Dental Voice Agent

> Comprehensive cost breakdown for all services used in the Pipecat dental assistant

**Date:** November 16, 2025  
**Services:** OpenAI GPT-4o-mini, ElevenLabs TTS, Soniox STT, Google Calendar API

---

## 📊 Current Stack Costs

### 1. **Speech-to-Text (STT): Soniox**

**Model:** `stt-rt-v3` (Real-time streaming)

| Metric | Cost | Notes |
|--------|------|-------|
| **Input audio tokens** | $2.00 / 1M tokens | Real-time streaming |
| **Output text tokens** | $4.00 / 1M tokens | Transcription output |
| **Per hour equivalent** | **~$0.12/hour** | Industry-leading accuracy |

**Usage calculation:**
- 1 hour of audio = ~30,000 input audio tokens
- 1 hour of speech = ~15,000 output text tokens
- **Cost per hour:** (30k × $2 + 15k × $4) / 1M = **$0.12**

### 2. **LLM Inference: OpenAI GPT-4o-mini**

**Model:** `gpt-4o-mini` (Fast, cost-effective)

| Metric | Cost | Notes |
|--------|------|-------|
| **Input tokens** | $0.150 / 1M tokens | Context + system prompt |
| **Cached input** | $0.075 / 1M tokens | 50% discount on repeated context |
| **Output tokens** | $0.600 / 1M tokens | LLM responses |

**Condensed prompt impact:**
- Original prompt: ~1,800 tokens → **$0.00027 per call**
- Condensed prompt: ~380 tokens → **$0.000057 per call**
- **Savings: 79% reduction in prompt costs** 🎉

**Average conversation estimates:**
| Scenario | Input Tokens | Output Tokens | Cost per Turn |
|----------|--------------|---------------|---------------|
| Simple query | 500 | 150 | $0.00016 |
| Appointment booking | 800 | 300 | $0.00030 |
| Complex interaction | 1,200 | 500 | $0.00048 |

**With function calling (calendar):**
- Add ~100-200 tokens for function definitions
- Add ~50-100 tokens per function call result

### 3. **Text-to-Speech (TTS): ElevenLabs**

**Current plan needed:** Pro ($99/month for 500k credits = 500 minutes)

| Plan | Monthly Cost | Minutes Included | Cost per Extra Minute |
|------|--------------|------------------|----------------------|
| Free | $0 | ~20 | N/A |
| Starter | $5 | ~60 | N/A |
| Creator | $11 ($22 regular) | ~200 | $0.15 |
| **Pro** | **$99** | **~1,000** | **$0.12** |
| Scale | $330 | ~4,000 | $0.09 |
| Business | $1,320 | ~22,000 | $0.06 |

**Your current settings:**
- Model: Turbo v2.5 (optimized for latency)
- Sample rate: 16kHz
- Speed: 1.1x
- Optimization level: 4 (low latency)

**Usage calculation:**
- Average response: 10-15 seconds
- Per conversation turn: ~12 seconds = 0.2 minutes
- 100 calls/day × 3 turns × 0.2 min = **60 minutes/day**
- **Monthly: ~1,800 minutes** → Pro plan + overages

---

## 💰 Complete Cost Breakdown by Call Volume

### Low Volume (100 calls/month)

| Service | Usage | Cost |
|---------|-------|------|
| **Soniox STT** | 3 hours (1.8 min/call) | $0.36 |
| **OpenAI GPT-4o-mini** | ~150k tokens total | $0.03 |
| **ElevenLabs TTS** | 180 minutes | $11.00 (Creator plan) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total** | | **~$11.39/month** |
| **Per call** | | **$0.114** |

### Medium Volume (500 calls/month)

| Service | Usage | Cost |
|---------|-------|------|
| **Soniox STT** | 15 hours | $1.80 |
| **OpenAI GPT-4o-mini** | ~750k tokens | $0.15 |
| **ElevenLabs TTS** | 900 minutes | $99.00 (Pro plan) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total** | | **~$100.95/month** |
| **Per call** | | **$0.202** |

### High Volume (2,000 calls/month)

| Service | Usage | Cost |
|---------|-------|------|
| **Soniox STT** | 60 hours | $7.20 |
| **OpenAI GPT-4o-mini** | ~3M tokens | $0.60 |
| **ElevenLabs TTS** | 3,600 minutes | $330.00 (Scale plan) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total** | | **~$337.80/month** |
| **Per call** | | **$0.169** |

### Enterprise Volume (10,000 calls/month)

| Service | Usage | Cost |
|---------|-------|------|
| **Soniox STT** | 300 hours | $36.00 |
| **OpenAI GPT-4o-mini** | ~15M tokens | $3.00 |
| **ElevenLabs TTS** | 18,000 minutes | ~$1,080 (custom) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total** | | **~$1,119/month** |
| **Per call** | | **$0.112** |

---

## 📈 Cost Optimization Strategies

### 1. **Already Implemented ✅**
- **Condensed prompt:** 79% token reduction → Saves $0.0002/call
- **gpt-4o-mini:** Instead of gpt-4 → 90% cheaper
- **Turbo v2.5 TTS:** Low latency without sacrificing quality

### 2. **Alternative TTS: Google Gemini 2.0 Flash**

If you switch to Gemini TTS:

| Volume | ElevenLabs Cost | Gemini Flash Cost | Savings |
|--------|----------------|-------------------|---------|
| 180 min/mo | $11.00 | $2.70 | **$8.30 (75%)** |
| 900 min/mo | $99.00 | $13.50 | **$85.50 (86%)** |
| 3,600 min/mo | $330.00 | $54.00 | **$276.00 (84%)** |
| 18,000 min/mo | $1,080.00 | $270.00 | **$810.00 (75%)** |

**Gemini Flash TTS:**
- Cost: $0.015/minute ($10 per 1M output tokens, 25 tokens/sec)
- Quality: Very good, improving rapidly
- Latency: Competitive with ElevenLabs Turbo
- Voices: More limited than ElevenLabs
- Greek support: Excellent

**Trade-off:**
- **ElevenLabs:** Superior voice quality, emotion, naturalness
- **Gemini:** 6-10× cheaper, excellent quality, faster development

### 3. **Prompt Caching (OpenAI)**

Enable prompt caching for 50% discount on repeated context:
- System prompt stays the same → cache it
- **Savings:** ~$0.00003 per call (small but adds up)

### 4. **Batch Processing (Non-Real-time)**

For non-urgent tasks (summaries, analytics):
- Use OpenAI Batch API → 50% discount
- Not applicable for real-time voice calls

---

## 🎯 Recommended Configuration by Budget

### **Budget: <$50/month (Startup)**
```yaml
STT: Soniox (best accuracy)
LLM: GPT-4o-mini (best value)
TTS: Gemini Flash 2.0 (cheapest)
Result: ~300-500 calls/month
Per call: $0.05-0.08
```

### **Budget: $100-300/month (Growing)**
```yaml
STT: Soniox
LLM: GPT-4o-mini
TTS: ElevenLabs Pro ($99/mo)
Result: ~500-1,500 calls/month
Per call: $0.15-0.20
Quality: Premium Greek voices
```

### **Budget: $300-1,500/month (Scaling)**
```yaml
STT: Soniox
LLM: GPT-4o-mini with caching
TTS: ElevenLabs Scale/Business
Result: 2,000-10,000 calls/month
Per call: $0.11-0.17
Quality: Best-in-class
```

---

## 💡 Key Insights

### Cost Distribution (Medium Volume)
```
🎙️ TTS (ElevenLabs): 98.1% of total cost
🧠 LLM (GPT-4o-mini): 0.1% of total cost
👂 STT (Soniox): 1.8% of total cost
📅 Calendar API: 0.0% (free tier)
```

**Main cost driver:** TTS dominates at 98% of total costs!

### Optimization Priority
1. **TTS provider choice** → Biggest impact (75-85% savings with Gemini)
2. **Prompt engineering** → Already optimized ✅
3. **LLM selection** → Already optimal (gpt-4o-mini) ✅
4. **Caching** → Minor gains (~3-5% savings)

### Break-Even Analysis

**Current Stack (ElevenLabs):**
- Fixed cost: $99/month (Pro)
- Marginal cost: $0.12/extra minute
- Best for: Premium quality needs

**Alternative Stack (Gemini TTS):**
- Fixed cost: $0/month
- Marginal cost: $0.015/minute (pure pay-as-you-go)
- Best for: Cost optimization, high volume

**Break-even:** ElevenLabs becomes cost-effective at >1,000 min/month IF voice quality is critical

---

## 🔮 Monthly Cost Projections

### Conservative Estimate (10 calls/day)
```
Monthly calls: 300
TTS: ElevenLabs Pro ($99) or Gemini ($4.50)
STT: $1.08
LLM: $0.06
Total: $100.14 (ElevenLabs) or $5.64 (Gemini)
```

### Moderate Estimate (50 calls/day)
```
Monthly calls: 1,500
TTS: ElevenLabs Pro + overages ($150) or Gemini ($22.50)
STT: $5.40
LLM: $0.30
Total: $155.70 (ElevenLabs) or $28.20 (Gemini)
```

### Aggressive Growth (200 calls/day)
```
Monthly calls: 6,000
TTS: ElevenLabs Scale ($330) or Gemini ($90)
STT: $21.60
LLM: $1.20
Total: $352.80 (ElevenLabs) or $112.80 (Gemini)
```

---

## 📋 Action Items

### Immediate (Week 1)
- [x] Implement condensed prompt (79% token reduction)
- [x] Use gpt-4o-mini for cost efficiency
- [ ] Enable OpenAI prompt caching
- [ ] Set up cost monitoring dashboard

### Short-term (Month 1)
- [ ] Test Gemini 2.0 Flash TTS quality in Greek
- [ ] A/B test: ElevenLabs vs Gemini with sample users
- [ ] Implement usage analytics (calls/day, avg duration)
- [ ] Set up billing alerts at $50, $100, $200 thresholds

### Long-term (Quarter 1)
- [ ] Negotiate volume discounts with ElevenLabs (>10k min/mo)
- [ ] Evaluate Soniox competitors (Deepgram, AssemblyAI)
- [ ] Consider self-hosted TTS for ultimate cost control
- [ ] Implement dynamic provider switching based on load

---

## 🎤 Voice Quality Comparison

| Provider | Quality (1-10) | Greek Support | Latency | Cost/min |
|----------|---------------|---------------|---------|----------|
| **ElevenLabs Turbo** | 9/10 | Excellent | 200-400ms | $0.12 |
| **Gemini 2.0 Flash** | 8/10 | Excellent | 150-300ms | $0.015 |
| **OpenAI TTS** | 7/10 | Good | 300-500ms | $0.015 |
| **Azure TTS** | 6/10 | Good | 200-400ms | $0.016 |

**Recommendation:** 
- Start with Gemini for cost efficiency
- Upgrade to ElevenLabs Pro if users complain about voice quality
- ElevenLabs is worth the 8× premium for premium positioning

---

## 📊 ROI Calculator

**Assumptions:**
- Revenue per call: $10 (appointment booking)
- Close rate: 30% (3 in 10 calls book)
- Cost per call: $0.20 (ElevenLabs) or $0.06 (Gemini)

| Monthly Calls | Revenue | Cost (E11) | Profit (E11) | Cost (Gemini) | Profit (Gemini) |
|--------------|---------|------------|--------------|---------------|-----------------|
| 100 | $300 | $11 | $289 | $6 | $294 |
| 500 | $1,500 | $101 | $1,399 | $30 | $1,470 |
| 2,000 | $6,000 | $338 | $5,662 | $120 | $5,880 |
| 10,000 | $30,000 | $1,119 | $28,881 | $600 | $29,400 |

**Key insight:** Even at high volume, AI costs are <4% of revenue → Focus on call quality over cost optimization!

---

## 🔗 Useful Links

- [OpenAI Pricing](https://openai.com/api/pricing/)
- [ElevenLabs Pricing](https://elevenlabs.io/pricing)
- [Soniox Pricing](https://soniox.com/pricing)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Google Calendar API](https://developers.google.com/calendar/api/quickstart/python) (Free tier: 1M requests/day)

---

**Last updated:** November 16, 2025  
**Maintainer:** @steve
