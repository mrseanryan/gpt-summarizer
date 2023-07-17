# gpt-summarizer

Summarize text using ChatGPT, with support for large text files, PDF files and translation.

## Dependencies

- Python3
- Chat GTP 3.5 Turbo

## Usage

1. Copy the text you want to summarize, into `data/input.txt`.

Tip: make sure the text does not contain commercially or personally sensitive information!

2. Run the `go.sh` script:

`./go.sh [target language]`

### Alternate Usage - other text file

To summarize a different file:

`python3 main_cli.py <path to input text file> [target language]`

### Alternate Usage - a PDF file

**gpt-summarizer** can also summarize PDF files:

`python3 main_cli.py <path to PDF file> [target language]`

## Example Output

The output is printed to STDOUT (terminal output):

```
=== === Short Summary === ===
Language models struggle to effectively use long contexts, with performance decreasing as the input context
grows longer. Relevant information at the beginning or end of the context is better utilized than information
in the middle. This analysis provides insights into how language models use their input context and suggests
new evaluation protocols for future long-context models.
=== === Long Summary === ===
This research focuses on understanding how language models utilize long contexts. While language models have
the ability to take long contexts as input, little is known about how well they actually use this information.
The study analyzes language model performance on two tasks: multi-document question answering and key-value
retrieval. The findings reveal that performance is highest when relevant information is located at the beginning
or end of the input context. However, when models need to access relevant information in the middle of long
contexts, performance significantly degrades. Additionally, as the input context grows longer, performance
decreases even for explicitly long-context models. The research provides valuable insights into the usage of
input context by language models and proposes new evaluation protocols for future long-context models. This
understanding is crucial for improving the effectiveness of language models in various user-facing language
technologies, such as conversational interfaces, search and summarization, and collaborative writing.
By addressing the challenges of effectively utilizing long contexts, language models can better handle
lengthy inputs and external information, leading to enhanced performance in real-world applications.
```

## Set up

1. Install openai Python client.

```
python3 -m pip install --upgrade pip
pip install --upgrade openai pymupdf
```

2. Get an Open AI key

3. Copy paste file `api-key.chatgpt.example.py` to `api-key.chatgpt.local.py`

4. Edit the local config file so that it contains your API key

## Chat-GPT Notes

### Principle 1 - Write Clear and Specific Instructions

- tactic 1: use delimiters, to denote what is the 'data input'
- tactic 2: ask for structured input (as opposed to journalist style or casual informal style)
- tactic 3: ask to check whether conditions are satisfied.
- tactic 4: few-shot prompting -> give successful examples of completing tasks, then ask the model to perform the task.

### Principle 2 - Give the model time to think.

- tactic 1: Instuct the model to spend more time! (outline specific steps to take)
- tactic 2: Instruct the model to work out its own solution before rushing to a conclusion

### Iterative prompt developement

- analyze errors, try to improve the prompt
- try include context (if too big, can use summaries?)

### Model Capabilities

- Summarizing
- Inferring
- Transforming (language, tone, format)
- Expanding

### Model Limitations

- does not know the boundary of its knowledge -> if asked on topic it has little knowledge of, it makes plausible but false statements -> hallucinations!

mitigations:

- asking the model to include a warning if it is not sure
- ask to use relevant information
- (ask to provide links to the source of the information)
