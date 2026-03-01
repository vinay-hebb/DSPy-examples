# String Mapping: 04_simple_rag.py to 04_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components. ChainOfThought automatically adds "reasoning" field.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 13:8 | 52 | 20:9 | 52 | Class Docstring | "Answer questions based ONLY on the provided context." becomes task instructions |
| 15:5 | 7 | 4:5, 10:7, 22:7 | 7, 7, 7 | Field Name: context | Used in field description, structure template, and user message |
| 16:5 | 8 | 5:5, 12:7, 26:7 | 8, 8, 8 | Field Name: question | Used in field description, structure template, and user message |
| 15:37 | 12 | 4:21 | 12 | Field Description: context | "facts to use" becomes context field description |
| 21:21 | 33 | 7:5, 14:7, 28:78, 30:12 | 9, 9, 9, 9 | Generated Field: reasoning | ChainOfThought auto-adds reasoning field (not in script) |
| 17:5 | 6 | 8:5, 16:7, 28:108, 32:7 | 6, 6, 6 | Field Name: answer | Used in field description and structure template |
| 25:10, 26:10, 27:10 | 35, 40, 28 | 37:6, 38:6, 39:6 | 35, 40, 28 | Retrieved Context | Individual context items formatted as numbered list in user message |
| 30:17 | 37 | 27:1 | 37 | User Question | "Who is the lead developer of Phoenix?" inserted into user message |
