# LLM-jp-Moshi: Japanese Full-duplex Spoken Dialogue Models

[![Japanese](https://img.shields.io/badge/README-Japanese-red.svg)](README.md) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

[📑 **Paper**](https://aclanthology.org/2026.iwsds-1.10/)
&nbsp;|&nbsp;
[🤗 **Model**](https://huggingface.co/llm-jp/llm-jp-moshi-v1)
&nbsp;|&nbsp;
[🖥️ **Demo**](https://llm-jp.github.io/llm-jp-moshi/)

LLM-jp-Moshi is a full-duplex spoken dialogue system for Japanese. Built upon the English 7B-parameter full-duplex spoken dialogue model [Moshi](https://arxiv.org/abs/2410.00037), it was developed through additional training on Japanese spoken dialogue data.

This repository introduces the LLM-jp-Moshi models (v1 / v1.1-base / v1.1-topic-prompted).

> [!NOTE]
> These models are prototypes and their responses may be unnatural.


## Models

### LLM-jp-Moshi-v1
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1](https://huggingface.co/llm-jp/llm-jp-moshi-v1)
- **Training Data:**
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - LLM-jp-Zoom1

### LLM-jp-Moshi-v1.1-base
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1.1-base](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-base)
- **Training Data:**
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - Synthetic dialogue corpus (15 topics, 93,679 dialogues, approx. 4,000 hours; built in-house by LLM-jp, release in preparation)

A model trained from the same J-CHAT pre-training checkpoint as v1, with additional training only on a large-scale Japanese synthetic dialogue corpus built in-house by LLM-jp, covering 15 everyday topics (approx. 4,000 hours).

Real dialogue audio from LLM-jp-Zoom1 is not mixed into the inputs for this additional Moshi training. However, the synthetic audio is generated using FireRedTTS-2 fine-tuned on LLM-jp-Zoom1, and selected excerpts from LLM-jp-Zoom1 are also used as reference audio for the system-side speaker during synthesis.

### LLM-jp-Moshi-v1.1-topic-prompted
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1.1-topic-prompted](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-topic-prompted)
- **Training Data:** (with topic labels and text prompts)
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - Synthetic dialogue corpus (15 topics, 93,679 dialogues, approx. 4,000 hours; built in-house by LLM-jp, release in preparation)
  - LLM-jp-Zoom1 (online dialogue data recorded over Zoom; 1,723 dialogues, approx. 1,000 hours)

A model additionally trained on the synthetic dialogue corpus and LLM-jp-Zoom1, with topic text prompts attached. By providing a topic as a text prompt at the beginning of a dialogue, the model can be conditioned to start chatting about that topic. The conditioning mechanism follows the text-based topic conditioning part of the Hybrid System Prompt from [PersonaPlex](https://arxiv.org/abs/2602.06053). See the model card for prompt formats and limitations.

Each training example is capped at about 164 seconds. As a result, the amounts actually used for training are approx. 3,600 hours of the synthetic corpus and approx. 78 hours of LLM-jp-Zoom1, for which only the beginning of each dialogue is used because the recordings are long (about 32 minutes on average).

The speech in the synthetic dialogue corpus used by v1.1-base and v1.1-topic-prompted was generated with a text-to-speech model fine-tuned on LLM-jp-Zoom1.

Each repository contains the following model files:
- `model.safetensors` - The main model weights
- `tokenizer_spm_32k_3.model` - Text tokenizer (Japanese SentencePiece model from [rinna/japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium))
- `tokenizer-e351c8d8-checkpoint125.safetensors` - Audio tokenizer (Mimi model from [kyutai/moshiko-pytorch-bf16](https://huggingface.co/kyutai/moshiko-pytorch-bf16))

The v1.1-topic-prompted repository additionally contains `prefix_tokens.npz`, used for text-prompt conditioning.


## Interactive Demo

This section describes how to interact with each of the LLM-jp-Moshi models. For v1 and v1.1-base, you can use the official [Moshi PyTorch implementation](https://github.com/kyutai-labs/moshi/tree/main/moshi) from Kyutai as is (see the original Moshi repository [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) for implementation details). v1.1-topic-prompted requires a dedicated inference server, so the procedure differs (see below).

### Installation for v1 / v1.1-base

Python 3.10 or higher is required.

```bash
pip install 'moshi<=0.2.2'
```

### Running v1 / v1.1-base

You can launch the web UI by running `moshi.server`. Specify the 🤗 HuggingFace Hub repository of the model to use with the `--hf-repo` option.

```bash
python -m moshi.server --hf-repo llm-jp/llm-jp-moshi-v1
# or
python -m moshi.server --hf-repo llm-jp/llm-jp-moshi-v1.1-base
```

#### Interacting with v1.1-topic-prompted

> [!NOTE]
> v1.1-topic-prompted does not work with `moshi.server`, as it requires a dedicated inference implementation that supports text-prompt conditioning. A compatible server is included in this repository under [`inference/`](inference/).

```bash
python inference/server.py --hf-repo llm-jp/llm-jp-moshi-v1.1-topic-prompted
```

Select a topic prompt (presets for the 15 trained topics) at the top of the screen and press 接続 (connect) to start the conversation.

### Tips

- A Linux GPU machine with at least 24GB of VRAM is required for execution. MacOS is not supported.
- To prevent echo of the model's speech output, please use earphones or headphones instead of speakers during dialogue. Audio devices can be configured in the browser when accessing the web UI.


## Terms of Use

The LLM-jp-Moshi models are released under the [Apache License, Version 2.0](LICENSE). 
This model is not intended for use in malicious activities, including but not limited to impersonation or fraud. The outputs generated by this model may contain biases, inaccuracies, or inappropriate or offensive content originating from the training data.
We assume no responsibility for any damages arising from its use.


## Acknowledgments

We used ABCI 3.0 provided by AIST and AIST Solutions with support from “ABCI 3.0 Development Acceleration Use”.  
We would like to thank Kyutai Labs for releasing the original Moshi model and technical paper. We also thank the researchers who released the J-CHAT dataset.


## Citation

If you use LLM-jp-Moshi-v1, please cite the following.

```bibtex
@inproceedings{abe2026effects,
    title={Effects of dialogue corpora properties on fine-tuning a {M}oshi-based spoken dialogue model},
    author={Abe, Yuto and Saeki, Mao and Ohashi, Atsumoto and Takamichi, Shinnosuke and Fujie, Shinya and Kobayashi, Tetsunori and Ogawa, Tetsuji and Higashinaka, Ryuichiro},
    booktitle={Proc. International Workshop on Spoken Dialogue Systems (IWSDS)},
    pages={104-108},
    year={2026},
    month={Feb}
}

@inproceedings{abe2026moshi,
    title={Moshi音声対話モデルの日本語ファインチューニングにおける対話データ特性の影響},
    author={阿部雄斗 and 佐伯真於 and 大橋厚元 and 高道慎之介 and 藤江真也 and 小林哲則 and 小川哲司 and 東中竜一郎},
    booktitle={日本音響学会研究発表会講演論文集},
    year={2026},
    month={Mar}
}
```
