# Natural Function Calling Implementation

## Overview
Implemented immediate voice feedback during function calls to create a more natural, responsive conversational experience. The agent now speaks immediately when a function is triggered, rather than staying silent during API calls.

## What Was Changed

### 1. Added TTSSpeakFrame Import (`bot.py`)
```python
from pipecat.frames.frames import LLMRunFrame, TTSSpeakFrame
```

### 2. Implemented `on_function_calls_started` Event Handler
Added an event handler that triggers immediately when the LLM decides to call a function, providing contextual Greek voice feedback while the function executes in parallel.

```python
@llm.event_handler("on_function_calls_started")
async def on_function_calls_started(service, function_calls):
    """Provide immediate voice feedback when a function call is triggered."""
```

## How It Works

### Flow Diagram
```
User: "Πες μου τα ραντεβού για τη Δευτέρα."
  ↓
LLM decides to call check_doctor_availability()
  ↓
Event handler triggers → "Ας δω... ελέγχω τη διαθεσιμότητα..." (speaks immediately)
  ↓
Function executes in parallel (API call to Google Calendar)
  ↓
Function returns results
  ↓
LLM formulates response with results
  ↓
Response is spoken to user
```

### Key Benefits
1. **No Awkward Silence**: User hears immediate feedback instead of waiting in silence
2. **Natural Conversation**: Mimics human behavior ("let me check...")
3. **Parallel Execution**: Voice feedback plays while API call happens
4. **Contextual Messages**: Different messages for different function types

## Voice Feedback Messages

| Function | Greek Message | English Translation |
|----------|--------------|---------------------|
| `check_doctor_availability` | "Ας δω... ελέγχω τη διαθεσιμότητα..." | "Let me see... checking availability..." |
| `get_next_available_slots` | "Μια στιγμή, ψάχνω τα επόμενα διαθέσιμα ραντεβού..." | "One moment, searching for next available appointments..." |
| `create_appointment` | "Εντάξει, κλείνω το ραντεβού..." | "Okay, booking the appointment..." |
| `update_appointment` | "Εντάξει, αλλάζω το ραντεβού..." | "Okay, changing the appointment..." |
| `cancel_appointment` | "Εντάξει, ακυρώνω το ραντεβού..." | "Okay, canceling the appointment..." |
| Default (any other function) | "Μια στιγμή..." | "One moment..." |

## Example Conversation

**Before Implementation:**
```
User: "Πες μου τα ραντεβού για τη Δευτέρα."
[3-5 seconds of silence while API call happens]
Agent: "Για τη Δευτέρα, έχουμε διαθέσιμα ραντεβού στις..."
```

**After Implementation:**
```
User: "Πες μου τα ραντεβού για τη Δευτέρα."
Agent: "Ας δω... ελέγχω τη διαθεσιμότητα..." [immediately]
[API call happens in parallel]
Agent: "Για τη Δευτέρα, έχουμε διαθέσιμα ραντεβού στις..."
```

## Technical Details

### Event Handler Registration
The event handler is registered on the LLM service **after** creating the pipeline task so we can queue frames to it:
```python
llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
register_calendar_functions(llm)

# Create pipeline and task first
pipeline = Pipeline([...])
task = PipelineTask(pipeline, params=PipelineParams(...))

# Then register the event handler that uses the task
@llm.event_handler("on_function_calls_started")
async def on_function_calls_started(service, function_calls):
    # Handler implementation
```

### Frame Queue
The TTSSpeakFrame is queued to the pipeline task, which injects it at the pipeline start:
```python
await task.queue_frames([TTSSpeakFrame(message)])
```

This allows the frame to flow through the pipeline to the TTS service, which converts it to speech that plays immediately while the function executes asynchronously.

### Function Call Structure
The `function_calls` parameter contains information about all functions being called:
```python
function_calls = [
    {
        "function": {
            "name": "check_doctor_availability",
            "arguments": {...}
        },
        "id": "call_123abc"
    }
]
```

## Customization

### Adding New Functions
To add feedback for new functions:
1. Register the function with the LLM
2. Add an entry to `feedback_messages` dict:
```python
feedback_messages = {
    # Existing messages...
    "your_new_function": "Το μήνυμά σας εδώ...",
}
```

### Changing Messages
Edit the `feedback_messages` dictionary in the event handler to customize the Greek responses.

### Disabling Feedback
To disable for specific functions, add logic to skip certain function names:
```python
if function_name in ["function_to_skip"]:
    return  # Don't provide feedback
```

## Related Files
- `bot.py` - Main bot implementation with event handler
- `src/calendar/calendar_functions.py` - Calendar function definitions and handlers
- Example recipe: See Pipecat docs on Function Calling

## References
- [Pipecat Function Calling Documentation](https://docs.pipecat.ai/guides/learn/function-calling)
- Event handler pattern from OpenAI function calling example
