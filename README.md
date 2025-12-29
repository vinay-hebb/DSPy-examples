# DSPy Examples

This repository contains examples demonstrating the use of DSPy for building agents that utilize various tools, including web search and a Python interpreter for math evaluations.

## Files

-   `multi_tool.py`: This script showcases a DSPy ReAct agent capable of using multiple tools. It includes a `search_web_agent` for web searches and an `evaluate_math` function for Python-based mathematical expression evaluation. It also demonstrates how to integrate custom logging for agent steps.
-   `web_search_agent.py`: This script focuses on a web search functionality using different methods, primarily `ddgs` (DuckDuckGo Search) with fallbacks to SearXNG or basic HTML scraping. It then uses the retrieved context in a DSPy `ChainOfThought` module to answer a question.

## Setup

### Prerequisites

-   Python 3.x
-   A compatible language model served by Ollama (default: `gemma3:1b`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/vinay-hebb/DSPy-examples.git
    cd DSPy-examples
    ```

2.  **Install Python dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    # Create and activate a virtual environment
    uv venv
    source .venv/bin/activate
    uv pip install dspy-ai requests duckduckgo-search
    ```
    *(Note: `duckduckgo-search` is used by `ddgs` in the scripts. If it's not available or causes issues, the scripts have fallback mechanisms.)*

## Usage

### Running `multi_tool.py`

This script demonstrates a ReAct agent answering a question that requires both web search and mathematical evaluation.

```bash
python multi_tool.py
```

### Running `web_search_agent.py`

This script demonstrates using web search to gather context and then employing a Chain of Thought model to answer a question.

```bash
python web_search_agent.py
```
