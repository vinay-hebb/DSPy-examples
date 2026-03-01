
import dspy
import sys
import os

# Add parent dir to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.response_saver import save_response

# Configure
lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class MathSolver(dspy.Signature):
    """Solve simple math word problems."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="the final numerical answer")

def main():
    # Use ChainOfThought instead of Predict
    cot_predictor = dspy.ChainOfThought(MathSolver)

    # Run
    question = "If I have 3 apples and buy 2 more, then eat 1, how many do I have?"
    print(f"Question: {question}")
    
    response = cot_predictor(question=question)
    print(f"Rationale: {response.reasoning}")
    print(f"Answer: {response.answer}")

    # Save and Visualize
    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/02_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/02_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
