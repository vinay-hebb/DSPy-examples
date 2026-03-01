# String Mapping: 05_structured_output.py to 05_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 13:8 | 48 | 23:9 | 48 | Class Docstring | "Extract structured information from a biography." becomes task instructions |
| 15:5 | 9 | 4:5, 11:7, 25:7 | 9, 9, 9 | Field Name: biography | Used in field description, structure template, and user message |
| 17:5 | 9 | 6:5, 13:7, 28:78 | 9, 9, 9 | Field Name: full_name | Used in field description and structure template |
| 18:5 | 3 | 7:5, 15:7, 28:108 | 3, 3, 3 | Field Name: age | Used in field description and structure template |
| 18:34 | 32 | 7:17 | 32 | Field Description: age | "numeric estimate if not explicit" becomes age field description |
| 19:5 | 10 | 8:5, 17:7, 28:132 | 10, 10, 10 | Field Name: occupation | Used in field description and structure template |
| 20:5 | 9 | 9:5, 19:7, 28:163 | 9, 9, 9 | Field Name: known_for | Used in field description and structure template |
| 20:40 | 29 | 9:23 | 29 | Field Description: known_for | "short summary of achievements" becomes known_for field description |
| 26:5-27:74 | 0 | 26:1-27:74 | 0 | User Input: biography | Multi-line biography text inserted into user message |
