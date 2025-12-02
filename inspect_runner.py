import pipecat.runner.run
import inspect

try:
    source = inspect.getsource(pipecat.runner.run)
    with open("runner_source.txt", "w", encoding="utf-8") as f:
        f.write(source)
    print("Source written to runner_source.txt")
except Exception as e:
    print(f"Error: {e}")
