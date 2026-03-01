
import dspy
import sys
import os

# Add parent dir to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.response_saver import save_response

# Configure
lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

def main():
    # Define predictor
    qa_predictor = dspy.Predict(BasicQA)

    # Run
    question = "What is the capital of France?"
    print(f"Question: {question}")
    
    response = qa_predictor(question=question)
    print(f"Answer: {response.answer}")

    # Save and Visualize
    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/01_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/01_viz.html')

    save_response(lm, response_path)
    # visualize_interaction(script_path, response_path, html_path)  <-- Handled by separate script


if __name__ == "__main__":
    main()
