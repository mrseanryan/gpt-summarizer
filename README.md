# gpt-summarizer

Summarize text using ChatGPT or a local LLM, with support for multiple large text files, PDF files and translation.

- outputs in YAML format, with title, short and long summaries, paragraph summaries and metadata.

## Features

| Area                 | Feature                                                                                                                                                                                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File types           | - Summarize text, markdown, HTML, PDF files                                                                                                                                                                                                                 |
| Summarization levels | - Summarize at different lavels: short, long, and per-paragraph                                                                                                                                                                                             |
| Translation          | - Translate to a target language                                                                                                                                                                                                                            |
| Data sources         | - Batch summarize whole directories of files <br/> - Download a file via URL and summarize it                                                                                                                                                               |
| Private LLM          | - Optionally use a locally hosted LLM, for maximum privacy and prevent any loss of IP (Intellectual Property)                                                                                                                                               |
| Cost savings         | - Avoid re-summarizing a previously processed file<br/> - Calculate cost estimates (when using Open AI)                                                                                                                                                     |
| Output files         | - Output files in YAML format (as opposed to JSON): cheaper for LLM to generate, easy for humans to read <br/> - Output files with a “.yaml.txt” file extension, for easy previewing and search in storage tools like Dropbox or SharePoint or Google Drive |

## Dependencies

- Python3

If running a local LLM:

- ctransformers

If using Open AI Chat GPT:

- Chat GTP 3.5 Turbo [requires an Open AI API key]

## Usage

To see the available options:

```
./go.sh
```

or

```
poetry run python -m gpt_summarizer.main_cli
```

Output:

```
Usage: main_cli.py <path to input file or input directory or URL> [options]

The options are:
[-l --language - The target output language. The default is set in config.py]
[-o --output - The output directory. By default is None, so output is to stdout (no files are output).]
[-h --help]
```

1. Copy the text you want to summarize, into a file like `data/input.txt`.

Tip: unless using a local LLM, make sure the text does not contain commercially or personally sensitive information!

2. Run the `go.sh` script:

`./go.sh data/input.txt [options]`

### Alternate Usage - other text file

To summarize different file(s):

`
poetry run python -m gpt_summarizer.main_cli <path to input text file or directory> [options]`

### Alternate Usage - a PDF file

**gpt-summarizer** can also summarize PDF files:

`poetry run python -m gpt_summarizer.main_cli <path to PDF file or directory> [options]`

## Example Output

The output is printed to STDOUT (terminal output):

```bash
=== === ===     [1] Summarizing './data/input.txt'      === === ===
Summarizing file at './data/input.txt' into English...
=== === ===     [2] Short Summary = Chunk 1 of 1        === === ===
The study examines how language models perform with long contexts, finding that they struggle when relevant information is in the middle of the input. Performance decreases as context length increases, even for models designed for long contexts, offering insights for future model evaluation.
=== === ===     [3] FULL Short Summary  === === ===
The study examines how language models perform with long contexts, finding that they struggle when relevant information is in the middle of the input. Performance decreases as context length increases, even for models designed for long contexts, offering insights for future model evaluation.

=== === ===     [4] FULL Long Summary   === === ===
The research delves into the performance of language models when processing long contexts, revealing that models face challenges when relevant information is located in the middle of the input. As the context length grows, performance diminishes, impacting tasks like multi-document question answering and key-value retrieval. This study sheds light on how language models utilize input contexts and proposes new evaluation methods for forthcoming long-context models.

=== === ===     [5] FULL paragraphs Summary     === === ===
Recent language models can handle long contexts but struggle with utilizing longer context effectively.
Performance is highest when relevant information is at the beginning or end of the input context.
Models face significant degradation when required to access relevant information in the middle of long contexts.
Performance decreases as the input context length increases, even for models explicitly designed for long contexts.
The study offers insights into how language models utilize input context and suggests new evaluation protocols for future long-context models.
 -- THIS FILE time: 0:00:05s
 -- THIS FILE estimated cost: $0.0006715
=== === ===     [6] Completed   === === ===
1 files processed in 0:00:05s
 -- Total estimated cost: $0.0006715
```

The output is a YAML file, with a structure like this (abbreviated) example:

```yaml
title: 'Lost in the Middle: How Language Models Use Long Contexts'
short_summary: 'Recent language models'' performance in utilizing long contexts is
  analyzed, revealing challenges when accessing information in the middle. The study
  provides insights for future long-context models.
  ...
  '
long_summary: 'The study delves into how language models handle long contexts, showing
  that performance peaks when relevant information is at the beginning or end, but
  drops significantly in the middle. It explores the impact of context length on model
  performance and the challenges faced by models in accessing information. The research
  offers new evaluation protocols for upcoming long-context models.
  ...

  '
paragraphs:
- Recent language models face challenges in utilizing long contexts effectively.
- Performance peaks when relevant information is at the beginning or end of the input
  context.
  ...
run_info:
  total_time_seconds: 43.19290280342102
  total_estimated_cost_currency: $
  total_estimated_cost: 0.014135000000000002
tool_info:
  tool_name: gpt-summarizer
  tool_version: 1.2.0
  llm: gpt-3.5-turbo
summary_date: '2025-01-24 17:37:32'
source_path: ./temp\downloaded--How-Language-Models-use-Long-Contexts.2025_01_24__173648.pdf
target_language: English
```

See also an example of [summarizing this README](./example_output/downloaded--README.2024_05_24__150934.yaml.txt).

Large files are broken into chunks for processing, with a single concatenated final output.

Costs are estimated using the figures in `config.py`.

If an output directory is specified as an option, then each input file has an equivalent output file, in YAML format.

## Set up

**gpt-summary** can be used in 2 ways:

1 - via remote LLM on Open-AI (Chat GPT)
2 - OR via local LLM (see the model types supported by [ctransformers](https://github.com/marella/ctransformers)).

First, edit config.py according to whether you can use GPU acceleration:

- If you have an NVidia graphics card and have also installed CUDA, then set IS_GPU_ENABLED to be True.
- Otherwise, set it to be False

### Option 1 - Open AI (Chat GPT)

1. Install openai Python client.

```
poetry install
```

OR

```
pip install cornsnake~=0.0.60 html2text==2024.2.26 json5==0.9.25 ollama==0.2.0 openai==1.23.6 pydantic~=2.7.3 PyMuPDF==1.24.1 pyyaml==6.0.1 ruff==0.3.5
```

2. Get an Open AI key

3. Set environment variable with your Open AI key:

```
export OPENAI_API_KEY="xxx"
```

Add that to your shell initializing script (`~/.zprofile` or similar)

Load in current terminal:

```
source ~/.zprofile
```

4. Set config.py to use open-ai

Set the value of `LOCAL_CTRANSFORMERS_MODEL_FILE_PATH` to be "".
Set the value of `OLLAMA_MODEL_NAME` to be "".

### Option 2 - Local LLM via ollama [recommended approach for local LLM]

1. Install ollama

- see [ollama site](https://ollama.com/download)

2. Pull a compatible model - for example llama3 or phi3 [depending on your hardware]

```
ollama pull llama3
```

3. Run ollama

```
ollama serve
```

4. Configure gpt-summarizer to use ollama

Edit config.py - set `OLLAMA_MODEL_NAME` to the name of the model from step 2
Set the value of `LOCAL_CTRANSFORMERS_MODEL_FILE_PATH` to be "".

5. Install python libraries

```
poetry install
```

OR

```
pip install cornsnake~=0.0.60 html2text==2024.2.26 json5==0.9.25 ollama==0.2.0 PyMuPDF==1.24.1 pyyaml==6.0.1 ruff==0.3.5
```

#### Tip: if you find there are many retries when parsing the LLM output, then try switching between JSON and YAML.

YAML is generally cheaper and faster, but some LLMs may be more reliable if asked to output JSON.

For a local LLM, you can decide which format to use via `config.py`:

- edit the value of `is_local__json_not_yaml`


### Option 3 - Local LLM via ctransformers

1. Install the ctransformers Python library

```
pip3 install --upgrade ctransformers pymupdf
```

2. Download a compatible model. To know what model types are supported, see the [ctransformers](https://github.com/marella/ctransformers) project.

Quality models are available at hugging face - see [TheBloke](https://huggingface.co/TheBloke).

Example: https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML/resolve/main/llama-2-13b-chat.ggmlv3.q4_0.bin

OR via bash:

```
./download-llama-2-13B-model.sh
```

3. Edit config.py

Set `LOCAL_CTRANSFORMERS_MODEL_FILE_PATH` to the path to the model file.
Set `OLLAMA_MODEL_NAME` to be "".

### Using GPU with the local model

- see [GPU README](./README.gpu.md)

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

## Related

Inspired by an excellent DeepLearning.ai course: [Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/)
