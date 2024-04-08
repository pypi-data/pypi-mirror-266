# Validation tool to compare a generated context by sLLM to reference context

생성된 문장(Function call 또는 Reservation Board (a.k.a Formatted output))과 기준이 되는 문장을 비교하여 두 문자열이 동일한지 여부를 확인합니다.

## Input data format

```json
{
    "context": "<s>[INST] <<SYS>>\nYou are a helpful and respectful movie ticketing assistant.\nYou"re actively involved in a three-way conversation with "user", "function" (the function helper other than you), ...",
    "answer": "{\"function_call\": {\"name\": \"extract_date_time\", \"arguments\": \"{\\\"query\\\":\\\"현재 시간을 알려주세요~\\\"}\"}, \"role\": \"assistant\", \"content\": null} ",
    "generated": "{\"function_call\": {\"name\": \"extract_date_time\", \"arguments\": \"{\\\"query\\\":\\\"현재 시간을 알려주세요\\\"}\"}, \"role\": \"assistant\", \"content\": null} "
}
```

## Load data from CSV file

```csv
index, context, answer, generated
0,<s>[INST] <<SYS>>\nYou are a...,{"function_call": {...,{"function_call": {...
```

## Installation

```bash
pip install equivalent_llm
```

## OpenAI API key

It use ChatGPT 4-turbo API. You need to set your API key to use this tool. You can set the API key in two ways: in command line or in python.

In command line:

```bash
export OPENAI_API_KEY="your-api-key"
```

In python:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

## Usage

For the validation set, you can use the following code:

```python
import equivalent_llm

# Validation from CSV file
validated = equivalent_llm.validate("data.csv")

json_list = validated["input_data"]
validation_results = validated["validations"]

# Validation from JSON list
equivalent_llm.validate(json_list)

# If you want to validate only subset of data, which can set as list of indexes
equivalent_llm.validate(json_list, indexes=[1,3,5])
# If you want to validate only one
equivalent_llm.validate(json_list, indexes=4)
# If you want to validate some range
equivalent_llm.validate(json_list, indexes=range(0, 15, 3))
```

If you want to validate with prompts, you can use the following code:

```python
import logging
debug_logger = logging.getLogger('debug_logger')
debug_logger.setLevel(logging.DEBUG)
index = 6
equivalent_llm.EquvalentLLM(json_list[index]['context'], json_list[index]['answer'], json_list[index]['generated'], logger=debug_logger)
```

## Output

### Function call (Task 1)

```json
{
  "target": "extract_date_time",
  "tests": {
    "equivalence": [{"argument": "query", "passed": true, "score": 98, "evidence": "The target sentence is equivalent to the reference sentence, with the only difference being the omission of a tilde (~) which is often used to soften the tone in informal contexts. This does not change the meaning of the sentence."}],
    "consistency": [{"argument": "query", "passed": true, "score": 100, "evidence": "..."}],
    "grammar": [{"argument": "query", "passed": true, "score": 100, "evidence": "..."}],
    "elegance": [],
    "function_name": {"passed": true},
    "required": {"passed": true},
    "paired_arguments": {"passed": true}},
  "passed": true,
  "count": {
  "total": {"passed": 3, "total": 3},
    "equivalence": {"passed": 1, "total": 1},
    "consistency": {"passed": 1, "total": 1},
    "grammar": {"passed": 1, "total": 1},
    "elegance": {"passed": 0, "total": 0},
    "etc": {"passed": 3, "total": 3}
  },
  "reference": {...},
  "generated": {...},
  "given_information": [...],
  "index": 0}
```

## Reservation board (a.k.a Formatted output) (Task 2)

```json
{
    "target": "reservation_board",
    "tests": {
        "equivalence": [{"element": "answer", "passed": true, "evidence": "..."}, {"element": "template", "passed": true, "evidence": "..."}],
    "consistency": [{"element": "answer", "passed": true, "score": 100, "evidence": "..."}],
    "grammar": [{"element": "answer", "passed": true, "score": 100, "evidence": "..."}],
    "elegance": [{"element": "answer", "passed": true, "score": 100, "evidence": "...", "alternative": "현재 시간은 14시 36분입니다."}]
  },
  "passed": true,
  "count": {
    "total": {"passed": 5, "total": 5},
    "equivalence": {"passed": 2, "total": 2},
    "consistency": {"passed": 1, "total": 1},
    "grammar": {"passed": 1, "total": 1},
    "elegance": {"passed": 1, "total": 1}
  },
  "reference": {...},
  "generated": {...},
  "given_information": [...],
  "index": 1}
```

## Build a package

1. Install [PDM](https://pdm-project.org/en/latest/) package
2. Build and install a package

```bash
# pdm build (or pdm build --release)
pdm install
```
