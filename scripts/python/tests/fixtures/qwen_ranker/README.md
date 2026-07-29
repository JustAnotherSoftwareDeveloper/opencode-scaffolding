# Qwen ranker fixtures

These fixtures are intentionally local and model-free.  The packaged tokenizer and
Apache license are exercised through `importlib.resources`; the tests never call
Ollama or download model artifacts.
