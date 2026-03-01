# String Mapping: 02_chain_of_thought.py to 02_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components. ChainOfThought automatically adds "reasoning" field.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 16:8 | 32 | 18:9 | 32 | Class Docstring | "Solve simple math word problems." becomes task instructions |
| 17:5 | 8 | 4:5, 10:7, 20:7 | 8, 8, 8 | Field Name: question | Used in field description, structure, and user message |
| 18:5 | 6 | 7:5, 15:4, 41:173 | 6, 6, 13 | Field Name: answer | Used in field description and JSON structure |
| 18:37 | 26 | 7:20 | 26 | Field Description | "the final numerical answer" becomes answer field description |
| 22:21 | 31 | 6:5, 14:4, 24:8 | 9, 9, 164 | Generated Field: reasoning | ChainOfThought auto-adds reasoning field (not in script) |
| 25:17 | 66 | 21:1 | 66 | User Input | "If I have 3 apples and buy 2 more, then eat 1, how many do I have?" inserted into user message |
