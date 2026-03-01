# String Mapping: 01_basic_qa.py to 01_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 15:8 | 44 | 14:9 | 44 | Class Docstring | "Answer questions with short factoid answers." becomes task instructions |
| 16:5 | 8 | 4:5, 8:7, 16:7 | 8, 8, 8 | Field Name: question | Used in field description list, structure template, and user message |
| 17:5 | 6 | 6:5, 10:7, 20:12 | 6, 6, 6 | Field Name: answer | Used in field description list and structure template |
| 17:37 | 27 | 6:20 | 27 | Field Description | "often between 1 and 5 words" becomes answer field description |
| 24:17 | 30 | 17:1 | 30 | User Input | "What is the capital of France?" inserted into user message section |
