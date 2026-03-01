
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
    """Process the input"""
    text = dspy.InputField(desc="the text to analyze")
    sentiment = dspy.OutputField(desc="sentiment label: positive, negative, or neutral")
    confidence = dspy.OutputField(desc="confidence level from 0 to 1")
    explanation = dspy.OutputField(desc="brief explanation of the sentiment")

# Define a DSPy Module (required for optimization)
class SentimentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentAnalysis)

    def forward(self, text):
        return self.predictor(text=text)

# Metric function: checks if sentiment prediction is reasonable
def sentiment_accuracy(example, prediction, trace=None):
    """
    Simple metric: check if predicted sentiment matches expected and confidence is non-zero.
    In real scenarios, this would be more sophisticated.
    """
    expected_sentiment = example.sentiment.lower().strip()
    predicted_sentiment = prediction.sentiment.lower().strip()

    # Check if sentiments match
    sentiments_match = expected_sentiment in predicted_sentiment or predicted_sentiment in expected_sentiment

    try:
        confidence = float(prediction.confidence)
        confidence_valid = 0.0 <= confidence <= 1.0
    except (ValueError, TypeError):
        confidence_valid = False

    return sentiments_match and confidence_valid

def main():
    # Training set: examples with known sentiments
    trainset = [
        dspy.Example(
            text="I absolutely love this product! It works perfectly and exceeded my expectations.",
            sentiment="positive",
            confidence="0.95",
            explanation="Strong positive language with enthusiastic tone"
        ).with_inputs("text"),
        dspy.Example(
            text="This movie was terrible. I wasted 2 hours of my life.",
            sentiment="negative",
            confidence="0.92",
            explanation="Clear negative sentiment expressed directly"
        ).with_inputs("text"),
        dspy.Example(
            text="The weather today is cloudy.",
            sentiment="neutral",
            confidence="0.88",
            explanation="Factual statement without emotional language"
        ).with_inputs("text"),
        dspy.Example(
            text="I'm so happy with my new car! Best decision ever!",
            sentiment="positive",
            confidence="0.93",
            explanation="Positive sentiment shown through happiness and positive comparison"
        ).with_inputs("text"),
        dspy.Example(
            text="I don't like the service here. Not recommended.",
            sentiment="negative",
            confidence="0.85",
            explanation="Negative sentiment about service quality"
        ).with_inputs("text"),
        dspy.Example(
            text="The report was submitted on Tuesday.",
            sentiment="neutral",
            confidence="0.90",
            explanation="Neutral factual statement about an event"
        ).with_inputs("text"),
    ]

    # Create uncompiled (unoptimized) module
    sentiment_module = SentimentModule()

    # Set up MIPRO optimizer with tracking enabled
    optimizer = dspy.MIPROv2(
        metric=sentiment_accuracy,
        init_temperature=1.4,
        track_stats=True,
    )

    # Compile (optimize) the module
    print("Optimizing with MIPROv2...")
    optimized_module = optimizer.compile(
        sentiment_module,
        trainset=trainset,
    )
    print("Optimization complete.")
    optimized_instruction = optimized_module.predictor.predict.signature.instructions
    print(f"\n{'='*70}")
    print(f"INSTRUCTION OVERRIDE DEMONSTRATION")
    print(f"{'='*70}")
    print(f"\n❌ INITIAL (Suboptimal) Instruction:")
    print(f"   'Process the input.'")
    print(f"\n✅ OPTIMIZED Instruction (after MIPROv2 compilation):")
    print(f"   '{optimized_instruction}'")
    num_demos = len(optimized_module.predictor.predict.demos)
    print(f"\nNumber of few-shot demos selected: {num_demos}")
    print(f"{'='*70}\n")

    # Test the optimized module on new texts
    test_texts = [
        "This is fantastic! I'm thrilled with the results.",
        "Absolutely horrible experience. Never coming back.",
        "It's raining outside today.",
    ]

    print("\n" + "="*60)
    print("Testing Optimized Sentiment Analysis")
    print("="*60)

    for test_text in test_texts:
        print(f"\nText: {test_text}")
        response = optimized_module(text=test_text)
        print(f"Sentiment: {response.sentiment}")
        print(f"Confidence: {response.confidence}")
        print(f"Explanation: {response.explanation}")
        print("-" * 40)

    # Print optimization summary
    print("\n" + "="*60)
    print("Optimization Summary")
    print("="*60)
    if hasattr(optimized_module, 'score'):
        print(f"Best Score: {optimized_module.score:.1f}%")
    if hasattr(optimized_module, 'total_calls'):
        print(f"Total LM Calls: {optimized_module.total_calls}")
    if hasattr(optimized_module, 'prompt_model_total_calls'):
        print(f"Prompt Generation LM Calls: {optimized_module.prompt_model_total_calls}")

    # Save and Visualize
    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/15_prompt+response.txt')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
