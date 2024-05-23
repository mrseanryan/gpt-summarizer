# gpt-summarizer

Summarize text using ChatGPT or a local LLM, with support for multiple large text files, PDF files and translation.

## Dependencies

- Python3

If running a local LLM:

- ctransformers

If using Open AI Chat GPT:

- Chat GTP 3.5 Turbo

## Usage

To see the available options:

```
./go.sh
```

or

```
python3 main_cli.py
```

Output:

```
Usage: main_cli.py <path to input file or input directory> [options]

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

`python3 main_cli.py <path to input text file or directory> [options]`

### Alternate Usage - a PDF file

**gpt-summarizer** can also summarize PDF files:

`python3 main_cli.py <path to PDF file or directory> [options]`

## Example Output

The output is printed to STDOUT (terminal output):

```
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
pip3 install cornsnake==0.0.53 openai==1.23.6 PyMuPDF==1.24.1 pyyaml==6.0.1 ruff==0.3.5
```

2. Get an Open AI key

3. Set environment variable with your OpenAI key:

```
export OPENAI_API_KEY="xxx"
```

Add that to your shell initializing script (`~/.zprofile` or similar)

Load in current terminal:

```
source ~/.zprofile
```

4. Set config.py to use open-ai

Set the value of LOCAL_MODEL_FILE_PATH to be "".

### Option 2 - Local LLM

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

Set `LOCAL_MODEL_FILE_PATH` to the path to the model file.

### Using GPU with the local model

If you have an NVIDIA graphics card, then you can run part or all of the model (depending on the card's RAM) on the GPU,
which has much higher level of parallelism than the typical CPU.

Required:
- latest NVIDIA graphic driver
- up to date version of CUDA

#### Tip: if you get errors when running the model, like this:

```
>> Cuda error: no kernel image is available for execution on the device
```
Then recommend to build ctransformers locally.

This is actually quite simple:

```
pip3 uninstall ctransformers
pip3 install ctransformers --no-binary ctransformers # use --no-binary to force a local build. This ensures that the local version of CUDA and NVIDIA graphics driver will be used.
```

You can tweak the settings in `config.py`.

For more details, see my [gpt-local](LOCAL_MODEL_FILE_PATH) wrapper project, or the main tool [ctransformers](https://github.com/marella/ctransformers).

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
