# Download model
export MODEL=llama-2-13b-chat.ggmlv3.q4_0.bin
export MODEL_PATH=~/Downloads/models/${MODEL}
if [ ! -f ${MODEL_PATH} ]; then
    curl -L "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML/resolve/main/${MODEL}" -o ${MODEL_PATH}
fi
