# String Mapping: 03_classification.py to 03_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 13:8 | 62 | 14:9 | 62 | Class Docstring | "Classify the user's intent into one of the allowed categories." becomes task instructions |
| 15:5 | 10 | 4:5, 9:2, 16:7, 28:7 | 10, 10, 10, 10 | Field Name: submission | Used in field description, structure template, and user message |
| 16:5 | 6 | 6:5, 10:7, 18:78, 36:12 | 6, 6, 6, 6 | Field Name: intent | Used in field description and structure template |
| 16:37 | 54 | 6:20 | 54 | Field Description | "one of: [Bug Report, Feature Request, Question, Other]" becomes intent field description |
| 21:13 | 63 | 17:1 | 63 | User Input | "I think the login button color is too bright, can we change it?" inserted into user message |
