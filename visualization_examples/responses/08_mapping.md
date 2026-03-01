# String Mapping: 08_few_shot_examples.py to 08_prompt+response.txt

## Mapping Format

Maps code snippets and values from the Python script to their corresponding outputs in the prompt+response file.

, 25:1-38:1 , 0 , 17:1-35:1 , 0 , Few shot , Few shot strings ,

## Mappings

Mappings show how Python script strings are transformed by DSPy into prompt components. Few-shot demonstrations are injected as chat history before the user query.

| Doc A Position | Doc A Length | Doc B Position | Doc B Length | Label | Description |
| --- | --- | --- | --- | --- | --- |
| 15:8 | 41 | 14:9 | 41 | Class Docstring | "Classify the sentiment of the given text." becomes task instructions |
| 16:5 | 4 | 4:5, 16:7, 23:7 | 4, 4, 4 | Field Name: text | Used in field description list, structure template, and demo inputs |
| 17:5 | 9 | 6:5, 10:7, 26:7, 39:78 | 9, 9, 9, 9 | Field Name: sentiment | Used in field description and output structure |
| 17:40 | 35 | 6:23 | 35 | Field Description | "one of: positive, negative, neutral" becomes sentiment field description |
| 26:19 | 48 | 17:1 | 48 | Demo 1 Input | "I absolutely loved this movie, it was fantastic!" inserted as first example input |
| 27:24 | 8 | 20:1 | 8 | Demo 1 Output | "positive" as first example output |
| 30:19 | 47 | 24:1 | 47 | Demo 2 Input | "The food was terrible and the service was slow." inserted as second example input |
| 31:24 | 8 | 27:1 | 8 | Demo 2 Output | "negative" as second example output |
| 34:19 | 42 | 31:1 | 42 | Demo 3 Input | "The meeting is scheduled for 3pm tomorrow." inserted as third example input |
| 35:24 | 7 | 34:1 | 7 | Demo 3 Output | "neutral" as third example output |
| 43:13 | 53 | 38:1 | 53 | User Input | "This product works okay but nothing special about it." inserted as final user message |
