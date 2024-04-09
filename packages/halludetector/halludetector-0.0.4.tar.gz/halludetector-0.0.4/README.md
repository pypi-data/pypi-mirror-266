# Hallucination detector

This project implements generic approaches for hallucination detection.

The ```Detector``` base class implements the building blocks to detect hallucinations and score them.

```ask_llm``` - method to request a response from an LLM via a prompt

```extract_triplets``` - method to extract subject, predicate, object from a text.

```extract_sentences``` - method to split a text into sentences using spacy

```generate_question``` - method to generate a question from a text

```retrieve``` - method to retrieve information from google via the serper api

```check``` - method to check if the claims contain hallucinations

```similarity_bertscore``` - method to check the similarity between texts via bertscore

```similarity_ngram``` - method to check the similarity between texts via ngram model

You can implement any custom detector and combine all the available methods from above.

## Installation

#### Use a conda environment and install the followings.
```
pip install -e .
pip install -r requirements.txt

python3 -m spacy download en_core_web_sm

```
#### Export envs for openai and google wrapper
```
export OPENAI_API_KEY=
export SERPER_API_KEY=
```


## Usage

#### as server
```
python3 server.py
```

Go to http://127.0.0.1:5000 and use the app.


#### as library
```
from openai import OpenAI
from halludetector import calculate_score

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# prompt - the prompt as text
# the question you want to ask as text
# 5 times to ask the llm if the completion contains hallucinations

score, completion, explanations = calculate_score(client, prompt, question, 5)

print(score)
```

#### from cli

```
python3 scorer.py --file data/questions.json --config config.json
```


## Configuration for ChainPoll

The file `/data/prompt.txt` contains a prompt template that is used.

Feel free to update it.

Allowed variables:

`{completion}` for the answer to the question.


`{question}` the initial question.


The file `config.json` contains the needed configuration for the library.
