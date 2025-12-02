# Performance Metrics Guide

## Overview

Your bot now tracks **Time To First Byte (TTFB)** for each service in the pipeline automatically. This document explains how to read and optimize these metrics.

---

## What You'll See in Logs

With the updated logging, you'll see highlighted metrics like:

```
📊 AzureLLMService TTFB: 2192.34ms
💰 AzureLLMService#0 prompt tokens: 1634, completion tokens: 170
⏱️  Processing: 2609.66ms - AzureLLMService#0

📊 ElevenLabsTTSService TTFB: 893.94ms
💰 ElevenLabsTTSService#0 usage characters: 58
⏱️  Processing: 0.99ms - ElevenLabsTTSService#0
```

---

## Understanding Your Metrics Chart

### Azure LLM Service (Left Chart)

**What it measures:** Time from receiving user transcript until the **first token** is generated.

**Your data shows:**
- **Range:** 2,000ms - 6,000ms
- **Average:** ~3,000-4,000ms (3-4 seconds)
- **Peak:** 6,000ms at 2:39:33

**What this means:**
- This is your **biggest bottleneck** 🔴
- Users wait 3-6 seconds after speaking before hearing a response start
- The high variability (2-6s) suggests:
  - Network latency to Azure
  - Cold start delays
  - Long system prompts (your dental secretary prompt is ~1,600 tokens)
  - Model complexity (likely using GPT-4 or GPT-4o)

**Why it varies:**
- First request after idle: +1-2s (cold start)
- Cached prompts: -30-50% (you see "cache read input tokens" in logs)
- Network conditions
- Azure region load

---

### ElevenLabs TTS Service (Right Chart)

**What it measures:** Time from receiving LLM text until the **first audio chunk** is ready.

**Your data shows:**
- **Range:** 0ms - 2,500ms
- **Average:** ~800-1,200ms (0.8-1.2 seconds)
- **Peak:** 2,500ms at 2:39:44

**What this means:**
- Much more **consistent** than LLM ✅
- Typical 1 second is reasonable for high-quality voice
- The 2.5s spike likely from:
  - Longer text chunk
  - Network issue
  - Cold start after idle

---

## Total Latency Breakdown

From your logs, a typical conversation turn takes:

| Stage | Time | Percentage |
|-------|------|------------|
| **STT (Soniox)** | ~200-500ms | 5-10% |
| **LLM (Azure)** | **~3,000-4,500ms** | **60-70%** 🔴 |
| **TTS (ElevenLabs)** | ~800-1,200ms | 15-20% |
| **Network overhead** | ~200-500ms | 5-10% |
| **TOTAL** | **4,200-6,700ms** | **4-7 seconds** |

---

## Target Performance

For a natural conversation experience:

- ✅ **Excellent:** < 2,000ms total
- ⚠️ **Acceptable:** 2,000-3,500ms total
- 🔴 **Poor:** > 3,500ms total

**You're currently at 4-7 seconds, which feels sluggish.**

---

## Optimization Strategies

### 1. **Reduce LLM TTFB** (Priority #1 - 60% of latency)

#### A. Use a Faster Model
```env
# Current (slow but high quality)
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Try these alternatives:
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini     # 2-3x faster, 80% quality
AZURE_OPENAI_DEPLOYMENT=gpt-3.5-turbo   # 3-5x faster, 70% quality
```

**Expected improvement:** 3,000ms → 800-1,500ms

---

#### B. Shorten System Prompt

Your current dental secretary prompt is **~1,600 tokens**. This adds latency.

**Optimization:**
```yaml
# Instead of listing all 7 use cases in detail, use a condensed version:
instructions: |
  You are a Greek-speaking dental receptionist. Book, reschedule, cancel appointments.
  Ask: name, phone, reason (καθαρισμός/έλεγχος/πόνος), preferred time.
  Offer 2-3 slots. Confirm details. Escalate complex issues.
  Never give medical advice. Always speak Greek except brand names.
```

Create 2 versions:
- `dental-secretary-full.yaml` (current, for complex scenarios)
- `dental-secretary-fast.yaml` (condensed, for 80% of calls)

**Expected improvement:** 500-800ms faster

---

#### C. Enable Aggressive Streaming

Make sure your Azure client uses streaming properly:

```python
llm = AzureLLMService(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview",
    # Add these for better streaming:
    stream=True,
    temperature=0.7,  # Lower = faster, more deterministic
)
```

**Expected improvement:** User hears response 300-500ms earlier

---

### 2. **Optimize TTS** (Priority #2 - 20% of latency)

#### A. Use ElevenLabs Turbo v2.5

```env
# Current model (unknown)
ELEVENLABS_MODEL=eleven_multilingual_v2

# Faster alternative:
ELEVENLABS_MODEL=eleven_turbo_v2_5
```

**Expected improvement:** 900ms → 400-600ms

---

#### B. Pre-generate Common Phrases

For frequent phrases, generate audio once and cache it:

```python
CACHED_AUDIO = {
    "greeting": "Καλημέρα, από την οδοντιατρική κλινική...",
    "confirm_name": "Μπορείτε να μου πείτε το όνομά σας;",
    "confirm_time": "Σας κλείνω ραντεβού. Σας βολεύει;",
}
```

**Expected improvement:** 900ms → 50ms for cached phrases

---

### 3. **Monitor & Alert**

Add thresholds to your metrics:

```python
# In bot.py, add after service initialization:
if "TTFB" in log_message:
    ttfb = float(log_message.split("TTFB: ")[1].split()[0]) * 1000
    if "AzureLLM" in log_message and ttfb > 5000:
        logger.warning(f"🚨 LLM TTFB exceeded 5s: {ttfb:.0f}ms")
    if "ElevenLabs" in log_message and ttfb > 2000:
        logger.warning(f"🚨 TTS TTFB exceeded 2s: {ttfb:.0f}ms")
```

---

## Expected Results After Optimization

| Optimization | Current | After | Improvement |
|-------------|---------|-------|-------------|
| **Switch to gpt-4o-mini** | 3,500ms | 1,200ms | -2,300ms |
| **Shorter prompt** | 3,500ms | 2,800ms | -700ms |
| **Turbo TTS** | 900ms | 500ms | -400ms |
| **Streaming** | (perception) | - | -300ms |
| **TOTAL** | **4,900ms** | **2,000ms** | **-2,900ms** |

From **5 seconds → 2 seconds** = **60% faster** ⚡

---

## How to A/B Test

1. Create two bot configurations:
   ```python
   # Fast version (for 90% of calls)
   DENTAL_FAST = {
       "model": "gpt-4o-mini",
       "prompt": "dental-secretary-fast.yaml",
       "tts_model": "eleven_turbo_v2_5",
   }
   
   # Quality version (for complex cases)
   DENTAL_QUALITY = {
       "model": "gpt-4o",
       "prompt": "dental-secretary-full.yaml",
       "tts_model": "eleven_multilingual_v2",
   }
   ```

2. Route based on complexity:
   ```python
   if user_query_is_simple():
       use_config(DENTAL_FAST)
   else:
       use_config(DENTAL_QUALITY)
   ```

---

## Next Steps

1. ✅ **Immediate:** Switch to `gpt-4o-mini` and test
2. ⏱️ **This week:** Create condensed prompt version
3. 🎯 **Next week:** Implement TTS caching for common phrases
4. 📊 **Ongoing:** Monitor daily TTFB averages

Track metrics in a spreadsheet to see improvements over time.

---

## Questions?

- **Why is my first call slow?** Cold start - models need to load
- **Why do metrics vary?** Network latency, Azure region load, prompt length
- **Can I eliminate latency?** No, but you can get to <2s which feels natural
- **Should I cache everything?** No, only static phrases - keep dynamic responses fresh

Good luck optimizing! 🚀
