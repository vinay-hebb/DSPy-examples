
import dspy
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.response_saver import save_response

lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class IntentClassifier(dspy.Signature):
    """Classify the user's intent into one of the allowed categories."""
    
    submission = dspy.InputField()
    intent = dspy.OutputField(desc="one of: [Bug Report, Feature Request, Question, Other]")

def main():
    classify = dspy.Predict(IntentClassifier)

    text = "I think the login button color is too bright, can we change it?"
    print(f"Submission: {text}")

    response = classify(submission=text)
    print(f"Intent: {response.intent}")

    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/03_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/03_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
