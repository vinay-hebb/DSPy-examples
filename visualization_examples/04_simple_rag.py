
import dspy
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.response_saver import save_response

lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class ContextualQA(dspy.Signature):
    """Answer questions based ONLY on the provided context."""
    
    context = dspy.InputField(desc="facts to use")
    question = dspy.InputField()
    answer = dspy.OutputField()

def main():
    # We simulate RAG by passing a list of strings as context manually.
    rag_predictor = dspy.ChainOfThought(ContextualQA)

    # Simulated retrieval results
    retrieved_context = [
        "The project code name is 'Phoenix'.",
        "The launch date is set for October 15th.",
        "The lead developer is Sarah."
    ]
    
    question = "Who is the lead developer of Phoenix?"
    
    print(f"Context: {retrieved_context}")
    print(f"Question: {question}")
    
    response = rag_predictor(context=retrieved_context, question=question)
    
    print(f"Answer: {response.answer}")

    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/04_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/04_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
