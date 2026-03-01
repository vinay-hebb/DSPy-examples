
import dspy
import sys
import os
from typing import List

# Add parent dir to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.response_saver import save_response

# Configure
lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class ExtractMovie(dspy.Signature):
    """Extract structured movie information from the given text."""
    text = dspy.InputField()
    title: str = dspy.OutputField(desc="the movie title")
    year: int = dspy.OutputField(desc="the release year as an integer")
    genre: str = dspy.OutputField(desc="the primary genre")
    director: str = dspy.OutputField(desc="the director name")
    cast: List[str] = dspy.OutputField(desc="list of main actors")

def main():
    # Define predictor
    extractor = dspy.Predict(ExtractMovie)

    # Run
    text = (
        "Released in 1994, The Shawshank Redemption is a drama film directed by Frank Darabont. "
        "It stars Tim Robbins and Morgan Freeman."
    )
    print(f"Text: {text}")

    response = extractor(text=text)

    # Access typed fields — year is validated as int, cast as List[str]
    print(f"\nExtracted Movie Info:")
    print(f"  Title: {response.title}")
    print(f"  Year: {response.year} (type: {type(response.year).__name__})")
    print(f"  Genre: {response.genre}")
    print(f"  Director: {response.director}")
    print(f"  Cast: {response.cast} (type: {type(response.cast).__name__})")

    # Save and Visualize
    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/09_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/09_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
