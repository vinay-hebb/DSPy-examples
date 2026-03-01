
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
    answer = dspy.OutputField(desc="a short factoid answer, often 1 to 5 words")

# Define a DSPy Module (required for optimization)
class QAModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(BasicQA)

    def forward(self, question):
        return self.predictor(question=question)

# Metric function: checks if the expected answer appears in the prediction
def answer_match(example, prediction, trace=None):
    expected = example.answer.lower().strip()
    predicted = prediction.answer.lower().strip()
    return expected in predicted or predicted in expected

def main():
    # Training set: examples with known answers
    trainset = [
        dspy.Example(question="What is the capital of France?", answer="Paris").with_inputs("question"),
        dspy.Example(question="What is the capital of Germany?", answer="Berlin").with_inputs("question"),
        dspy.Example(question="What is the capital of Italy?", answer="Rome").with_inputs("question"),
        dspy.Example(question="What is the capital of Spain?", answer="Madrid").with_inputs("question"),
        dspy.Example(question="What is the capital of Japan?", answer="Tokyo").with_inputs("question"),
        dspy.Example(question="What is the capital of Brazil?", answer="Brasilia").with_inputs("question"),
    ]

    # Create uncompiled (unoptimized) module
    qa_module = QAModule()

    # Set up the optimizer
    optimizer = dspy.BootstrapFewShot(
        metric=answer_match,
        max_bootstrapped_demos=2,
        max_labeled_demos=4,
        max_rounds=1,
    )

    # Compile (optimize) the module
    print("Optimizing with BootstrapFewShot...")
    optimized_qa = optimizer.compile(qa_module, trainset=trainset)
    print("Optimization complete.")

    # Test the optimized module on a new question
    question = "What is the capital of Australia?"
    print(f"\nQuestion: {question}")

    response = optimized_qa(question=question)
    print(f"Answer: {response.answer}")

    # Save and Visualize
    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/14_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/14_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
