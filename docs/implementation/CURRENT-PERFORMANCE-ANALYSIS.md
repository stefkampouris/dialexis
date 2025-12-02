# Performance Analysis - Session 2025-11-15 02:51

## Metrics from Your Last Session

### Turn 1: Initial Greeting
```
LLM TTFB:  2,812ms  (2.8 seconds)
TTS TTFB:    516ms  (0.5 seconds)
Total:     3,328ms  (3.3 seconds)

Tokens: 1634 prompt, 223 completion
```

### Turn 2: User asked "Τι μπορείς να κάνεις;"
```
LLM TTFB:  6,352ms  (6.4 seconds) ⚠️ SLOW!
TTS TTFB:    603ms  (0.6 seconds)
Total:     6,955ms  (7.0 seconds) 🔴

Tokens: 1673 prompt, 628 completion
```

---

## Analysis

### 🔴 Critical Issue: LLM TTFB Spike

**Turn 2 took 6.4 seconds** for the LLM to respond - this is **unacceptably slow**.

**Why it happened:**
1. **Long completion** (628 tokens) - the agent gave a very detailed answer
2. **No prompt caching benefit** - only 1536 tokens were cached, rest was reprocessed
3. **Network or Azure load** - possible spike in Azure latency

**The prompt is making it worse:**
- Your system prompt is **~1,600 tokens**
- Every turn sends this full prompt again
- Cached reads help but don't eliminate the problem

---

## Recommendations (Priority Order)

### 1. 🔴 **URGENT: Shorten System Prompt**

Your current dental secretary prompt is very detailed. Create a "fast" version:

**Current:** ~1,600 tokens  
**Target:** ~400-600 tokens

**Create:** `prompts/dental-secretary-fast.yaml`

```yaml
instructions: |
  You are a Greek-speaking dental clinic receptionist AI.
  
  # Core Rules
  - Always speak Greek (except brand names like "Depon")
  - Keep responses short (1-3 sentences)
  - Never give medical advice
  
  # Tasks
  1. Book appointments: Get name, phone, reason (καθαρισμός/έλεγχος/πόνος), date preference
  2. Reschedule: Confirm existing appointment, offer new slots
  3. Cancel: Confirm cancellation, offer rebook
  4. FAQs: Hours, location, services, parking, payment methods
  5. Escalate: Complex issues, emergencies, complaints
  
  # Urgency Rules
  - Strong pain or swelling → same day
  - Moderate → next 2-3 days
  - Routine cleaning → normal schedule
  
  # Privacy
  - Only use provided patient data
  - Don't invent details
  - Don't share info between patients
  
  Structure: Greet → Understand need → Act → Confirm → Close politely.
```

**Expected improvement:** 6,400ms → 2,500ms (60% faster)

---

### 2. ⚡ **HIGH: Switch to gpt-4o-mini**

Update your `.env`:
```env
# Current (slow but high quality)
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Change to (2-3x faster, still good quality)
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

**Expected improvement:** Additional 40-50% speed boost

**Combined with short prompt:**
- Turn 1: 2,800ms → **~800ms** ⚡
- Turn 2: 6,400ms → **~1,500ms** ⚡

---

### 3. 🟡 **MEDIUM: Add Response Length Limit**

Add to your system prompt:
```yaml
## RESPONSE LENGTH
- Keep ALL responses under 100 words
- For complex answers, break into multiple turns
- Prioritize clarity over completeness
```

This will prevent 628-token completions like in Turn 2.

**Expected improvement:** More consistent performance, no more 6s+ spikes

---

### 4. 🟡 **MEDIUM: Use ElevenLabs Turbo**

Your TTS is already pretty good (500-600ms), but you can make it faster:

```env
ELEVENLABS_MODEL=eleven_turbo_v2_5
```

**Expected improvement:** 600ms → 350ms

---

## Expected Results After All Optimizations

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Turn 1 (greeting)** | 3.3s | 1.2s | **-64%** ⚡ |
| **Turn 2 (long answer)** | 7.0s | 2.0s | **-71%** ⚡ |
| **Average** | 5.2s | 1.6s | **-69%** ⚡ |

**User experience:**
- Before: "This feels slow and awkward" 🔴
- After: "This feels like talking to a human" ✅

---

## Quick Win: Test Right Now

Create `prompts/dental-secretary-fast.yaml` with the short prompt above, then in `bot.py`:

```python
# Line 109 - change this:
system_prompt = load_prompt()

# To this:
system_prompt = load_prompt("prompts/dental-secretary-fast.yaml")
```

Restart the bot and test again. You should immediately see:
- LLM TTFB drop from 2.8-6.4s → 1.0-2.0s
- Total response time drop from 3.3-7.0s → 1.5-2.5s

---

## Next Steps

1. ✅ Create the fast prompt (5 minutes)
2. ✅ Test and compare metrics (10 minutes)
3. ✅ If happy, switch to gpt-4o-mini for even more speed
4. ✅ Monitor with `analyze_metrics.py` script

Want me to create the fast prompt file for you? 🚀
