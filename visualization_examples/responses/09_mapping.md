# String Mapping: 09_typed_predictors.py to 09_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components. Typed OutputFields (with type annotations and descriptions) generate JSON schema constraints in the prompt.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 16:8 | 56 | 24:9 | 56 | Class Docstring | "Extract structured movie information from the given text." becomes task instructions |
| 17:5 | 4 | 4:5, 13:7 | 4, 4 | Field Name: text | Used in input field description and input section header |
| 18:5 | 5 | 6:5, 17:3, 42:62 | 5, 18, 7 | Field Name: title | Used in output field list |
| 18:41 | 15 | 6:19 | 15 | Field Description: title | "the movie title" becomes title field description |
| 19:5 | 4 | 7:5, 18:4, 42:76 | 4, 14, 6 | Field Name: year | Used in output field list |
| 19:40 | 30 | 7:18 | 30 | Field Description: year | "the release year as an integer" becomes year field description |
| 20:5 | 5 | 8:5, 19:4, 42:131 | 5, 17, 7 | Field Name: genre | Used in output field list |
| 20:41 | 17 | 8:19 | 17 | Field Description: genre | "the primary genre" becomes genre field description |
| 21:5 | 8 | 9:5, 20:4, 42:145 | 8, 23, 10 | Field Name: director | Used in output field list |
| 21:44 | 17 | 9:22 | 17 | Field Description: director | "the director name" becomes director field description |
| 22:5 | 4 | 10:5, 21:4, 42:162 | 4, 14, 6 | Field Name: cast | Used in output field list |
| 22:46 | 19 | 10:24 | 19 | Field Description: cast | "list of main actors" becomes cast field description |
| 30:9-31:49 | 0 | 27:1 | 127 | User Input | Multi-line movie description inserted into input section |
