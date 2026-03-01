
import dspy
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.response_saver import save_response

lm = dspy.LM('ollama/gemma3:1b', api_base='http://localhost:11434')
dspy.configure(lm=lm)

class BioExtractor(dspy.Signature):
    """Extract structured information from a biography."""
    
    biography = dspy.InputField()
    
    full_name = dspy.OutputField()
    age = dspy.OutputField(desc="numeric estimate if not explicit")
    occupation = dspy.OutputField()
    known_for = dspy.OutputField(desc="short summary of achievements")

def main():
    extractor = dspy.Predict(BioExtractor)

    text = """
    Born in 1879, Albert Einstein was a theoretical physicist who developed the theory of relativity. 
    He is considered one of the most influential scientists of all time.
    """
    print(f"Bio: {text.strip()}")

    response = extractor(biography=text)
    
    print("\nExtracted Info:")
    print(f"Name: {response.full_name}")
    print(f"Age: {response.age} (at death/implied)")
    print(f"Job: {response.occupation}")
    print(f"Fame: {response.known_for}")

    script_path = os.path.abspath(__file__)
    response_path = os.path.join(os.path.dirname(__file__), 'responses/05_prompt+response.txt')
    html_path = os.path.join(os.path.dirname(__file__), 'responses/05_viz.html')

    save_response(lm, response_path)


if __name__ == "__main__":
    main()
