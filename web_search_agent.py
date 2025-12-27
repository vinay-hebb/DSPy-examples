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

def search_web(query: str) -> list[str]:
    """Search the web using ddgs library or fallback methods."""
    results = []
    
    # Try using ddgs library (best option)
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            # Get text results
            search_results = list(ddgs.text(query, max_results=5))
            if search_results:
                for result in search_results:
                    # Try different possible keys in the result dictionary
                    # The ddgs library typically returns 'body' for text results
                    text_content = (result.get('body') or result.get('text') or 
                                  result.get('snippet') or result.get('description') or
                                  str(result))  # Fallback to string representation
                    if text_content and text_content.strip():
                        results.append(text_content.strip())
    except ImportError:
        # Package not installed, will try fallbacks
        pass
    except Exception as e:
        # If ddgs fails for any reason, try fallbacks
        print(f"Warning: ddgs search failed: {e}")
    
    # If ddgs didn't return results, try fallback methods
    if not results:
        try:
            # Alternative 1: Use SearXNG public instance (if available)
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
            # Alternative 2: Try Brave Search API (requires API key, but we'll try without)
            try:
                # Using a simple web scraping approach with requests
                url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Simple text extraction (basic fallback)
                    import re
                    # Extract text between result snippets (basic pattern matching)
                    text = response.text
                    # Look for result snippets in the HTML
                    snippets = re.findall(r'result__snippet[^>]*>([^<]+)', text)
                    results.extend(snippets[:3])
            except Exception as e2:
                print(f"Warning: HTML scraping fallback failed: {e2}")
    
    if not results:
        print(f"Warning: No search results found for query: {query}")
        # Return empty list instead of a placeholder to avoid misleading the LLM
        return []
    
    return results

rag = dspy.ChainOfThought('context, question -> response')

question = "What's the name of the castle that David Gregory inherited?"
try:
    context = search_web(question)
    if context:
        ragResponse = rag(context=context, question=question)
        print(ragResponse)
    else:
        print("Skipping RAG example: Web search unavailable")
except Exception as e:
    print(f"Error in RAG example: {e}")
