# gpt-summarizer

Summarize text using ChatGPT, with support for large text files, PDF files and translation.

## Dependencies

- Python3

If running a local LLM:

- ctransformers

If using Open AI Chat GPT:

- Chat GTP 3.5 Turbo

## Usage

1. Copy the text you want to summarize, into `data/input.txt`.

Tip: unless using a local LLM, make sure the text does not contain commercially or personally sensitive information!

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

**gpt-summary** can be used in 2 ways:

1 - via remote LLM on Open-AI (Chat GPT)
2 - OR via local LLM (see the model types supported by [ctransformers](https://github.com/marella/ctransformers)).

First, edit config.py according to whether you can use GPU acceleration:
- If you have an NVidia graphics card and have also installed CUDA, then set IS_GPU_ENABLED to be True.
- Otherwise, set it to be False


### Option 1 - Open AI (Chat GPT)

1. Install openai Python client.

```
pip3 install cornsnake==0.0.51 openai==1.23.6 PyMuPDF==1.24.1
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

# Tip: if you get errors when running the model, like this:
# >> Cuda error: no kernel image is available for execution on the device
# THEN recommend to build ctransformers locally.
# This is actually quite simple:

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
