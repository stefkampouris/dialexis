# Hosting & Deployment Analysis for Dental Voice Agent

> Complete guide to hosting options, infrastructure costs, and deployment strategies

**Date:** November 16, 2025  
**Framework:** Pipecat with Daily transport  
**Deployment Options:** Pipecat Cloud, Modal, Self-hosted

---

## 🏢 Recommended Hosting: Pipecat Cloud

**Why Pipecat Cloud?**
- ✅ Purpose-built for Pipecat framework
- ✅ Managed infrastructure (zero DevOps)
- ✅ Auto-scaling and load balancing
- ✅ Built-in Daily WebRTC transport (included free!)
- ✅ Real-time monitoring and observability
- ✅ 80+ service integrations (OpenAI, ElevenLabs, Soniox, etc.)
- ✅ Blazing fast cold starts (<1 second)
- ✅ Unlimited concurrency

---

## 💰 Pipecat Cloud Pricing

### Agent Hosting (Container Compute)

| Profile | Specs | Active Mode | Reserved Mode | Use Case |
|---------|-------|-------------|---------------|----------|
| **agent-1x** | 0.5 vCPU, 1GB RAM | **$0.01/min** | $0.0005/min | Voice agents (RECOMMENDED) |
| agent-2x | 1 vCPU, 2GB RAM | $0.02/min | $0.0010/min | Voice + video agents |
| agent-3x | 1.5 vCPU, 3GB RAM | $0.03/min | $0.0015/min | Complex processing |

**Active vs Reserved:**
- **Active:** Pay-per-use, auto-scales, perfect for variable load
- **Reserved:** Pre-committed capacity at 95% discount, for predictable high volume

### Transport (Network)

| Transport | Cost | Notes |
|-----------|------|-------|
| **Daily WebRTC Voice** | **FREE** | Included with Pipecat Cloud! ✨ |
| Daily WebRTC Voice+Video | $0.004/min | For multimodal agents |
| Websocket | Provider cost | Bring your own (Twilio, etc.) |

### Telephony (Optional)

| Service | Cost/min | Use Case |
|---------|----------|----------|
| Daily SIP Dial-in/out | $0.005 | SIP trunk integration |
| Daily PSTN Dial-in/out | $0.018 | Direct phone number |
| Twilio | Provider cost | Use existing Twilio account |

### Krisp VIVA (Background Noise Removal)

| Tier | Cost |
|------|------|
| First 10k minutes/month | **FREE** |
| Additional minutes | $0.0015/min |

### Recording (Optional)

| Service | Cost/min |
|---------|----------|
| Cloud storage + processing | $0.01349 |

---

## 📊 Complete Monthly Costs (Pipecat Cloud)

### Scenario 1: Low Volume (100 calls/month, 3 min avg)

| Component | Usage | Cost |
|-----------|-------|------|
| **Agent Hosting (agent-1x)** | 300 minutes | **$3.00** |
| **Daily WebRTC Voice** | 300 minutes | **$0.00** (free!) |
| **OpenAI GPT-4o-mini** | 150k tokens | $0.03 |
| **Soniox STT** | 3 hours | $0.36 |
| **ElevenLabs TTS** | 180 minutes | $11.00 (Creator plan) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total Infrastructure** | | **$14.39/month** |
| **Per call** | | **$0.14** |

### Scenario 2: Medium Volume (500 calls/month, 3 min avg)

| Component | Usage | Cost |
|-----------|-------|------|
| **Agent Hosting (agent-1x)** | 1,500 minutes | **$15.00** |
| **Daily WebRTC Voice** | 1,500 minutes | **$0.00** (free!) |
| **OpenAI GPT-4o-mini** | 750k tokens | $0.15 |
| **Soniox STT** | 15 hours | $1.80 |
| **ElevenLabs TTS** | 900 minutes | $99.00 (Pro plan) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total Infrastructure** | | **$115.95/month** |
| **Per call** | | **$0.23** |

### Scenario 3: High Volume (2,000 calls/month, 3 min avg)

| Component | Usage | Cost |
|-----------|-------|------|
| **Agent Hosting (agent-1x)** | 6,000 minutes | **$60.00** |
| **Daily WebRTC Voice** | 6,000 minutes | **$0.00** (free!) |
| **OpenAI GPT-4o-mini** | 3M tokens | $0.60 |
| **Soniox STT** | 60 hours | $7.20 |
| **ElevenLabs TTS** | 3,600 minutes | $330.00 (Scale plan) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total Infrastructure** | | **$397.80/month** |
| **Per call** | | **$0.20** |

### Scenario 4: Enterprise (10,000 calls/month, 3 min avg)

| Component | Usage | Cost |
|-----------|-------|------|
| **Agent Hosting (agent-1x)** | 30,000 minutes | **$300.00** |
| **Daily WebRTC Voice** | 30,000 minutes | **$0.00** (free!) |
| **OpenAI GPT-4o-mini** | 15M tokens | $3.00 |
| **Soniox STT** | 300 hours | $36.00 |
| **ElevenLabs TTS** | 18,000 minutes | ~$1,080 (custom) |
| **Google Calendar API** | Free tier | $0.00 |
| **Total Infrastructure** | | **$1,419/month** |
| **Per call** | | **$0.14** |

---

## 💡 Reserved Instances Strategy (High Volume)

For **predictable high volume**, use reserved instances:

### Example: 2,000 calls/month (6,000 minutes)

**Active Mode:**
- Agent hosting: 6,000 min × $0.01 = **$60/month**

**Reserved Mode (10 instances, 24/7):**
- 10 instances × 43,800 min/month × $0.0005 = **$219/month**
- Handles up to 43,800 minutes/month
- **Saves $180/month** if using >21,900 min/month
- **Break-even:** ~2,200 min/month (~730 calls)

**When to use Reserved:**
- Predictable traffic patterns
- >700 calls/month consistently
- Need guaranteed availability
- Enterprise SLA requirements

---

## 🔄 Alternative Hosting: Modal

**Pros:**
- Serverless architecture (only pay for actual compute)
- Excellent for GPU workloads (if self-hosting LLM)
- Good for development/testing
- $30/month free credits

**Cons:**
- More DevOps work required
- Need to manage WebRTC transport separately
- Cold starts (5-10 minutes for LLMs)
- Less optimized for voice agents

### Modal Pricing

| Resource | Cost |
|----------|------|
| CPU core (2 vCPU) | $0.0000131/sec = $0.047/hour |
| Memory (1 GiB) | $0.00000222/sec = $0.008/hour |
| **Total for voice agent** | ~$0.055/hour = **$0.0009/min** |

**Comparison:**
- Modal CPU: $0.0009/min
- Pipecat Cloud agent-1x: $0.01/min (11× more but fully managed)

**When Modal makes sense:**
- Self-hosting your own LLM (need GPUs)
- Very low volume (<100 calls/month)
- Heavy customization requirements
- Already have Modal infrastructure

---

## 🏠 Self-Hosted Options

### Option 1: AWS/GCP/Azure (Not Recommended)

**Typical costs for voice agent:**
- Container hosting: $30-100/month (ECS/Cloud Run/AKS)
- Load balancer: $20-50/month
- WebRTC infrastructure: $200-500/month (custom TURN servers)
- Monitoring/logging: $20-50/month
- DevOps overhead: Significant time investment

**Total:** $270-700/month + engineering time

**When to consider:**
- Already have enterprise cloud contracts
- Strict data residency requirements
- >50,000 calls/month
- Dedicated infrastructure team

### Option 2: Railway / Render / Fly.io

**Pros:**
- Easy deployment (similar to Heroku)
- Good for web apps + API

**Cons:**
- NOT optimized for real-time voice
- WebRTC complexity
- Higher latency
- Limited voice-specific features

**Pricing:** ~$10-50/month (basic tier)

**Verdict:** ❌ Not suitable for production voice AI

---

## 📈 Cost Breakdown by Component

### What drives costs?

**At 500 calls/month:**
```
Agent Hosting (Pipecat):  13% ($15)
TTS (ElevenLabs):         85% ($99)
STT (Soniox):             1.6% ($1.80)
LLM (GPT-4o-mini):        0.1% ($0.15)
Transport (Daily):        0% (FREE!)
```

**Key insight:** TTS is still the dominant cost, but infrastructure adds 13-18%

---

## 🎯 Recommended Architecture

### Production Setup (Medium Volume)

```yaml
Hosting: Pipecat Cloud
  Profile: agent-1x (voice only)
  Mode: Active (auto-scaling)
  
Transport: Daily WebRTC Voice
  Cost: FREE (included)
  
Services:
  LLM: OpenAI GPT-4o-mini
  STT: Soniox (real-time)
  TTS: ElevenLabs Pro ($99/mo)
  Calendar: Google Calendar API
  
Additional:
  Krisp VIVA: Enabled (10k free min)
  Monitoring: Built-in (included)
  Scaling: Automatic
```

**Total:** ~$116/month for 500 calls

### Cost-Optimized Setup (Low Volume)

```yaml
Hosting: Pipecat Cloud
  Profile: agent-1x
  Mode: Active
  
Transport: Daily WebRTC Voice (FREE)
  
Services:
  LLM: OpenAI GPT-4o-mini
  STT: Soniox
  TTS: Gemini 2.0 Flash (instead of ElevenLabs)
  
Additional:
  Krisp VIVA: Enabled
  Monitoring: Built-in
```

**Total:** ~$9/month for 100 calls (66% savings)

### Enterprise Setup (High Volume)

```yaml
Hosting: Pipecat Cloud
  Profile: agent-1x
  Mode: Reserved (10-20 instances)
  
Transport: Daily WebRTC Voice (FREE)
Telephony: Daily PSTN ($0.018/min)
  
Services:
  LLM: GPT-4o-mini with caching
  STT: Soniox (volume discounts negotiated)
  TTS: ElevenLabs Business ($1,320/mo)
  
Additional:
  Krisp VIVA: Unlimited
  Recording: Enabled ($0.01349/min)
  Support: Enterprise 24/7
```

**Total:** ~$1,600-2,000/month for 10k calls

---

## 🚀 Deployment Steps (Pipecat Cloud)

### 1. Setup (5 minutes)

```bash
# Install Pipecat Cloud CLI
pip install pipecat-cloud

# Login
pcc login

# Initialize project
pcc init dental-agent
```

### 2. Configure (pcc-deploy.toml)

```toml
agent_name = "dental-secretary"
image = "your-registry/dental-agent:latest"
agent_profile = "agent-1x"
secret_set = "dental-secrets"

[scaling]
min_agents = 1
max_agents = 10
```

### 3. Deploy

```bash
# Build and push Docker image
docker build -t your-registry/dental-agent:latest .
docker push your-registry/dental-agent:latest

# Deploy to Pipecat Cloud
pcc deploy

# Get endpoint URL
pcc status
```

### 4. Monitor

```bash
# View logs
pcc logs --follow

# Check metrics
pcc metrics

# View active sessions
pcc sessions
```

---

## 📊 Cost Comparison Matrix

| Hosting | Setup Time | Monthly Cost (500 calls) | DevOps Burden | Voice Optimized | Scale Limit |
|---------|-----------|-------------------------|---------------|-----------------|-------------|
| **Pipecat Cloud** | 5 min | **$116** | None | ⭐⭐⭐⭐⭐ | Unlimited |
| Modal | 30 min | $110-130 | Medium | ⭐⭐⭐ | Very high |
| AWS/GCP/Azure | 2-5 days | $350-600 | High | ⭐⭐ | Unlimited |
| Railway/Render | 15 min | $50-150 | Low | ⭐ | Limited |

---

## 💰 Total Cost of Ownership (TCO)

### Pipecat Cloud (Recommended)

**Year 1:**
```
Infrastructure: $1,391 (500 calls/mo avg)
Development time saved: $5,000+ (no DevOps)
Scaling incidents avoided: $2,000+
Total TCO: $1,391
Engineer hours saved: ~40 hours
```

### Self-Hosted AWS

**Year 1:**
```
Infrastructure: $4,200 (EC2, LB, storage)
Initial setup: $8,000 (2 weeks engineering)
Maintenance: $6,000 (5 hours/month)
Scaling incidents: $3,000 (downtime, debugging)
Total TCO: $21,200
Engineer hours: 160 hours
```

**Pipecat Cloud ROI:** Save ~$20,000/year + 160 engineer hours

---

## 🎯 Final Recommendations

### For Your Dental Agent (Starting Out)

**Month 1-3: Cost-Optimized**
```
✅ Pipecat Cloud (agent-1x, active)
✅ Daily WebRTC Voice (FREE)
✅ Gemini 2.0 Flash TTS
✅ Soniox STT
✅ GPT-4o-mini
💰 Total: ~$9-20/month
```

**Month 4-6: Quality Upgrade**
```
✅ Pipecat Cloud (agent-1x, active)
✅ Daily WebRTC Voice (FREE)
✅ ElevenLabs Pro TTS ($99/mo)
✅ Soniox STT
✅ GPT-4o-mini
💰 Total: ~$116/month
```

**Month 6+: Scale Mode**
```
✅ Pipecat Cloud (agent-1x, reserved)
✅ Daily WebRTC Voice (FREE)
✅ ElevenLabs Scale TTS
✅ Soniox STT (volume discount)
✅ GPT-4o-mini (caching enabled)
✅ Krisp VIVA (included)
💰 Total: ~$300-400/month (2k calls)
```

---

## 🔗 Resources

- [Pipecat Cloud Console](https://pipecat.daily.co/)
- [Pipecat Cloud Docs](https://docs.pipecat.ai/deployment/pipecat-cloud)
- [Pipecat Cloud Pricing Calculator](https://www.daily.co/pricing/pipecat-cloud/#calculator)
- [Modal Deployment Guide](https://docs.pipecat.ai/deployment/platforms/modal)
- [Daily Pricing](https://www.daily.co/pricing/)

---

## 📋 Next Steps

### Week 1: Setup & Deploy
- [ ] Create Pipecat Cloud account
- [ ] Set up secrets (API keys)
- [ ] Deploy first version
- [ ] Test with 10-20 calls

### Week 2-4: Optimize
- [ ] Monitor performance metrics
- [ ] A/B test TTS providers (Gemini vs ElevenLabs)
- [ ] Optimize prompt (already 79% reduced ✅)
- [ ] Set up cost alerts

### Month 2-3: Scale
- [ ] Analyze call patterns
- [ ] Consider reserved instances if >700 calls/month
- [ ] Negotiate volume discounts with providers
- [ ] Add telephony (Daily PSTN) if needed

---

**Last updated:** November 16, 2025  
**Maintainer:** @steve  
**Status:** Ready for production deployment 🚀
