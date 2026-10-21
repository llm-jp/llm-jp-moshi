# LLM-jp-Moshi: Japanese Full-duplex Spoken Dialogue Models

[![English](https://img.shields.io/badge/README-English-red.svg)](README-en.md) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

[📑 **Paper**](https://aclanthology.org/2026.iwsds-1.10/)
&nbsp;|&nbsp;
[🤗 **Models**](https://huggingface.co/models?search=llm-jp-moshi)
&nbsp;|&nbsp;
[🖥️ **Demo**](https://llm-jp.github.io/llm-jp-moshi/)

LLM-jp-Moshiは，日本語におけるfull-duplex音声対話システムです．英語における7Bパラメータのfull-duplex音声対話モデル [Moshi](https://arxiv.org/abs/2410.00037) をベースとし，日本語音声対話データでの追加学習によって構築されました．

このリポジトリでは，LLM-jp-Moshiのモデル群（v1 / v1.1-base / v1.1-prompted）を紹介します．

> [!NOTE]
> これらのモデルは試作段階であり，その応答は不自然な場合があります．


## Models

### LLM-jp-Moshi-v1
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1](https://huggingface.co/llm-jp/llm-jp-moshi-v1)
- **学習データ:**
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - LLM-jp-Zoom1

### LLM-jp-Moshi-v1.1-base
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1.1-base](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-base)
- **学習データ:**
  - [J-CHAT](https://arxiv.org/abs/2407.15828)（事前学習）
  - 合成対話コーパス（追加学習：15話題，約4,000時間．LLM-jpで独自に構築，公開に向けて準備中）

v1と同じJ-CHAT事前学習チェックポイントから，LLM-jpで独自に構築した日常的な15話題をカバーする大規模な日本語合成対話コーパス（約4,000時間）のみで追加学習したモデルです．この追加学習にはLLM-jp-Zoom1を使用していません．使い方はv1と同じく`moshi.server`でそのまま対話できます（Interactive Demo参照）．

### LLM-jp-Moshi-v1.1-prompted
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1.1-prompted](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-prompted)
- **学習データ:**（話題ラベル・テキストプロンプト付き）
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - 合成対話コーパス（15話題，約4,000時間．LLM-jpで独自に構築，公開に向けて準備中）
  - LLM-jp-Zoom1

合成対話コーパスとLLM-jp-Zoom1を追加学習に使用し，話題のテキストプロンプトを付与して学習したモデルです．対話の冒頭でテキストプロンプトとして話題を与えることで，その話題から雑談を始めるように条件づけできます．条件づけの仕組みは [PersonaPlex](https://arxiv.org/abs/2602.06053) のHybrid System Promptのうち，テキストによる話題条件づけの部分のみを参考にしています．プロンプトの書き方や制約の詳細はモデルカードを参照してください．

各リポジトリには，以下のモデルファイルが含まれています:
- `model.safetensors` - モデル本体の重み
- `tokenizer_spm_32k_3.model` - テキストトークナイザ（[rinna/japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium)の日本語SentencePieceモデル）
- `tokenizer-e351c8d8-checkpoint125.safetensors` - 音声トークナイザ（[kyutai/moshiko-pytorch-bf16](https://huggingface.co/kyutai/moshiko-pytorch-bf16)のMimiモデル）


## Interactive Demo

Kyutai公式の[MoshiのPyTorch実装](https://github.com/kyutai-labs/moshi/tree/main/moshi)を用いて，LLM-jp-Moshi-v1およびv1.1-baseと対話することができます．実装の詳細は，オリジナルMoshiのリポジトリ [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) を参照してください．

### Installation

Python 3.10以上が必要です．

```bash
pip install moshi<=0.2.2
```

### Usage

`moshi.server`を実行することで，対話用のweb UIを起動できます．`--hf-repo`オプションで使用するモデルの 🤗HuggingFace Hubリポジトリを指定してください．

```bash
python -m moshi.server --hf-repo llm-jp/llm-jp-moshi-v1
# または
python -m moshi.server --hf-repo llm-jp/llm-jp-moshi-v1.1-base
```

### v1.1-promptedと対話する場合

> [!NOTE]
> v1.1-promptedは，テキストプロンプトの前置（prefill）に対応した専用の推論実装が必要なため，`moshi.server`では動作しません．本リポジトリの [`inference/`](inference/) に対応サーバを同梱しています．

```bash
cd inference
pip install -r requirements.txt
python server.py --hf-repo llm-jp/llm-jp-moshi-v1.1-prompted
```

ブラウザで `http://localhost:8998/` を開き，画面上部の入力欄で話題プロンプトを編集して「接続」を押します．
オプションは [`inference/README.md`](inference/README.md) を参照してください．

### Tips

- 実行には，24GB以上のVRAMを搭載したLinux GPUマシンが必要です．MacOSには対応していません．
- モデルの発話音声がエコーすることを避けるため，対話時にはスピーカではなくイヤホン・ヘッドホンを使用してください．音声デバイスはweb UIアクセス時にブラウザ上で設定できます．


## Terms of Use

LLM-jp-Moshiの各モデルは [Apache License, Version 2.0](LICENSE) の下で公開されています．
本モデルは，なりすましや詐欺などの悪意ある目的での使用を意図したものではありません．また，本モデルの出力には，学習データに起因するバイアス，不正確な情報，または不適切もしくは攻撃的な内容が含まれる可能性があります．
我々はその使用によって生じるいかなる損害についても責任を負いません．


## Acknowledgments

本研究では，国立研究開発法人産業技術総合研究所および株式会社AIST Solutionsが提供するAI橋渡しクラウド（ABCI）3.0を，「ABCI 3.0開発加速利用」の支援を受けて実施しました．
また，ベースモデルであるMoshiおよびテクニカルペーパーを公開されたKyutai Labs，J-CHATデータセットを公開された研究者の皆様，ならびにHybrid System Prompt手法を提案されたPersonaPlexの著者の皆様に深く感謝の意を表します．


## Citation

LLM-jp-Moshi-v1 を使用する場合は，以下を引用してください．

```bibtex
@inproceedings{abe2026effects,
    title={Effects of dialogue corpora properties on fine-tuning a {M}oshi-based spoken dialogue model},
    author={Abe, Yuto and Saeki, Mao and Ohashi, Atsumoto and Takamichi, Shinnosuke and Fujie, Shinya and Kobayashi, Tetsunori and Ogawa, Tetsuji and Higashinaka, Ryuichiro},
    booktitle={Proc. International Workshop on Spoken Dialogue Systems (IWSDS)},
    pages={104–108},
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
