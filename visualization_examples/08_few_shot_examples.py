
import dspy
import sys
import os

# Add parent dir to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.response_saver import save_response

# Configure
lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class SentimentAnalysis(dspy.Signature):
    """Classify the sentiment of the given text."""
    text = dspy.InputField()
    sentiment = dspy.OutputField(desc="one of: positive, negative, neutral")

def main():
    # Define predictor
    classify = dspy.Predict(SentimentAnalysis)

    # Provide few-shot demonstrations to guide the model
    demos = [
        dspy.Example(
            text="I absolutely loved this movie, it was fantastic!",
            sentiment="positive"
        ).with_inputs("text"),
        dspy.Example(
            text="The food was terrible and the service was slow.",
            sentiment="negative"
        ).with_inputs("text"),
        dspy.Example(
            text="The meeting is scheduled for 3pm tomorrow.",
            sentiment="neutral"
        ).with_inputs("text"),
    ]

    # Attach demonstrations to the predictor
    classify.demos = demos

    # Run on a new example
    text = "This product works okay but nothing special about it."
    print(f"Text: {text}")

    response = classify(text=text)
    print(f"Sentiment: {response.sentiment}")

    # Save and Visualize
    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/08_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/08_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
