import dspy
import os
from typing import Literal
import requests
from urllib.parse import quote

# --- Configuration ---
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "gemma3:1b")
lm = dspy.LM(f'ollama/{OLLAMA_MODEL_NAME}', api_base=OLLAMA_API_BASE)
dspy.configure(lm=lm)
import time

from dspy.utils.logging_utils import enable_logging, disable_logging
import dspy.utils.logging_utils as logging_utils

def evaluate_math(expression: str) -> float:
    start_time = time.time()
    result = dspy.PythonInterpreter({}).execute(expression)
    elapsed = time.time() - start_time
    # Use dspy's internal logging so prints propagate through agent callbacks/logging.
    print_fn = getattr(logging_utils, "eprint", print)
    print_fn(f"[evaluate_math] Elapsed time: {elapsed:.3f} seconds")
    return result

def search_web_agent(query: str) -> str:
    """Search the web using ddgs library or fallback methods."""
    import time
    start_time = time.time()
    results = []
    
    # Try using ddgs library (best option)
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            # Get text results
            search_results = list(ddgs.text(query, max_results=3))
            for result in search_results:
                if 'body' in result:
                    results.append(result['body'])
                elif 'text' in result:
                    results.append(result['text'])
                elif 'snippet' in result:
                    results.append(result['snippet'])
    except ImportError:
        # If duckduckgo-search is not installed, try alternative methods
        try:
            # Alternative: Use SearXNG public instance (if available)
            searx_url = "https://searx.be/search"
            params = {
                'q': query,
                'format': 'json',
                'engines': 'google,bing,duckduckgo'
            }
            response = requests.get(searx_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for result in data.get('results', [])[:3]:
                    if 'content' in result:
                        results.append(result['content'])
                    elif 'snippet' in result:
                        results.append(result['snippet'])
        except Exception:
            print(f"Warning: Web search failed in agent")
    
    elapsed = time.time() - start_time
    print_fn = getattr(logging_utils, "eprint", print)
    print_fn(f"[search_web_agent] Elapsed time: {elapsed:.3f} seconds")
    if not results:
        return []
    
    return results

from dspy.utils.callback import BaseCallback
class AgentLoggingCallback(BaseCallback):
    def on_module_end(self, call_id, outputs, exception):
        # Determine if the step was reasoning (Thought) or acting (tool use)
        step = "Reasoning" if any(k.startswith("Thought") for k in outputs) else "Acting"
        print(f"== {step} Step ==")
        for k, v in outputs.items():
            print(f"  {k}: {v}")
        print("\n")

dspy.settings.configure(lm=lm, callbacks=[AgentLoggingCallback()])
enable_logging()
react = dspy.ReAct("question -> answer: float", tools=[search_web_agent, evaluate_math])

try:
    pred = react(question="What is 9362158 divided by the year of birth of David Gregory of Kinnairdy castle?")
    print(pred.answer)
except Exception as e:
    print(f"Error in agent example: {e}")
