# DSPy Examples

This repository provides two main example bundles:

## Bundles

- `dspy_examples/` holds the agents that assemble DSPy modules with tools such as web search and Python evaluation.
- `visualization_examples/` contains the runnable DSPy demonstrations (QA, RAG, classification, optimization) and the helper scripts that visualize their prompt-to-response mappings as below.

<div align="center">
  <img src="./MIPRO%20Map.png" alt="prompt-to-response for MIPRO" title="" style="max-width: 900px; width: 100%;"/>
  <div style="margin-top:6px; font-size: 1em;">
    Baseline instruction is replaced with optimized instruction using MIPRO
  </div>
</div>

## File overview

- `dspy_examples/multi_tool.py`: A DSPy ReAct-style agent that mixes a search tool with a Python math evaluator and logs each agent step.
- `dspy_examples/web_search_agent.py`: Uses the `ddgs` search wrapper (with fallbacks to other web scrapers) and feeds the collected context into a Chain of Thought predictor to answer user questions.
- `visualization_examples/run_all.sh`: Runs every visualization example in order and then invokes `visualizer.py` for each mapping file to emit HTML viewers under `responses/`.
- `visualization_examples/visualizer.py`: Reads a Markdown mapping file and renders an interactive HTML visualization of how code snippets align with response text.
- `visualization_examples/watch_mappings.py`: Monitors mapping files for changes (used primarily in development workflows).
- The remaining DSPy sample scripts now live under `visualization_examples/` and correspond to the numbered tutorials (01…15).

## Setup

### Prerequisites

-   Python 3.x
-   A compatible model served by Ollama (default: `gemma3:1b`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/vinay-hebb/DSPy-examples.git
    cd DSPy-examples
    ```

2.  **Install Python dependencies** (prefer using a virtual environment):
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install dspy-ai requests duckduckgo-search
    ```
    > `duckduckgo-search` powers `ddgs`; if it causes issues, the scripts already include fallbacks.

## Usage

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

### Running the agent bundle

```bash
cd dspy_examples
python multi_tool.py
python web_search_agent.py
```

### Running the visualization bundle

```bash
cd visualization_examples
bash run_all.sh
```

Each run writes its prompt/response output under `responses/` and produces mapping visualizations (HTML files) alongside the Markdown traces. Open any `responses/*_mapping_viewer.html` in a browser to inspect the alignments between code and outputs.
