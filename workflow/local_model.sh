#!/usr/bin/env bash
# Public weights on a standard runner. No hosted model account or token is needed.
set -euo pipefail

model_directory="${RUNNER_TEMP}/autose-model"
install_directory="${RUNNER_TEMP}/autose-llama"
model_revision="13fb94bfda8c8cf22497dc57b78f391a9acb426a"
model_file="qwen2.5-coder-7b-instruct-q4_k_m.gguf"
mkdir -p "$model_directory" "$install_directory"

download() {
    curl --fail --silent --show-error --location --retry 2 \
        --connect-timeout 20 --max-time 540 --proto '=https' "$1" -o "$2"
}

download "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/${model_revision}/${model_file}?download=true" \
    "$model_directory/$model_file"
download "https://github.com/ggml-org/llama.cpp/releases/download/b11146/llama-b11146-bin-ubuntu-x64.tar.gz" \
    "$install_directory/llama.tar.gz"
printf '%s  %s\n' "c150306eb16b5ab696f76a8bdf810c35fd98a24e82158742e6fa28f420ff8410" \
    "$install_directory/llama.tar.gz" | sha256sum -c -
tar -xzf "$install_directory/llama.tar.gz" -C "$install_directory"
server="$(find "$install_directory" -type f -name llama-server -print -quit)"
test -x "$server"

nohup "$server" --model "$model_directory/$model_file" --alias autose-qwen \
    --host 127.0.0.1 --port 8173 --ctx-size 16384 --parallel 1 \
    --threads "$(nproc)" --n-gpu-layers 0 --no-webui \
    > "$RUNNER_TEMP/autose-llama.log" 2>&1 < /dev/null &
server_pid=$!
for try in {1..60}; do
    if curl --fail --silent --output /dev/null http://127.0.0.1:8173/health; then
        exit 0
    fi
    if ! kill -0 "$server_pid" 2>/dev/null; then
        break
    fi
    sleep 2
done
tail -25 "$RUNNER_TEMP/autose-llama.log"
exit 1
