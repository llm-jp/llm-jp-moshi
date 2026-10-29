# LLM-jp-Moshi: Japanese Full-duplex Spoken Dialogue Models

[![English](https://img.shields.io/badge/README-English-red.svg)](README-en.md) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

[📑 **Paper**](https://aclanthology.org/2026.iwsds-1.10/)
&nbsp;|&nbsp;
[🤗 **Model**](https://huggingface.co/llm-jp/llm-jp-moshi-v1)
&nbsp;|&nbsp;
[🖥️ **Demo**](https://llm-jp.github.io/llm-jp-moshi/)

LLM-jp-Moshiは，日本語におけるfull-duplex音声対話システムです．英語における7Bパラメータのfull-duplex音声対話モデル [Moshi](https://arxiv.org/abs/2410.00037) をベースとし，日本語音声対話データでの追加学習によって構築されました．

このリポジトリでは，LLM-jp-Moshiのモデル群（v1 / v1.1-base / v1.1-topic-prompted）を紹介します．

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
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - 合成対話コーパス（15話題，93,679対話，約4,000時間．LLM-jpで独自に構築，公開に向けて準備中）
  - LLM-jp-Zoom1

v1と同じJ-CHAT事前学習チェックポイントから，LLM-jpで独自に構築した日本語合成対話コーパスとLLM-jp-Zoom1の実対話データを混合して2エポック追加学習したモデルです．

合成音声の生成にはLLM-jp-Zoom1でファインチューニングしたFireRedTTS-2を使用し，合成時のシステム側話者の参照音声にもLLM-jp-Zoom1から抜粋した一部の音声を使用しています．

補足として，同じJ-CHAT事前学習チェックポイントから[合成データのみで追加学習した比較モデル](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-base-synthetic-ft)も用意しています．本プロジェクトの比較評価ではほぼ同程度の結果でしたが，日本語の全二重対話ベンチマークによる比較では，この比較モデルはv1.1-baseよりも相手の発話中に発話を開始しにくい傾向が見られました．詳細はリンク先を参照してください．

### LLM-jp-Moshi-v1.1-topic-prompted
- **🤗 Model:** [llm-jp/llm-jp-moshi-v1.1-topic-prompted](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-topic-prompted)
- **学習データ:**（話題ラベル・テキストプロンプト付き）
  - [J-CHAT](https://arxiv.org/abs/2407.15828)
  - 合成対話コーパス（15話題，93,679対話，約4,000時間．LLM-jpで独自に構築，公開に向けて準備中）
  - LLM-jp-Zoom1（Zoomによるオンライン対話データ，1,723対話，約1,000時間）

合成対話コーパスとLLM-jp-Zoom1を追加学習に使用し，話題のテキストプロンプトを付与して学習したモデルです．対話の冒頭でテキストプロンプトとして話題を与えることで，その話題から雑談を始めるように条件づけできます．条件づけの仕組みは [PersonaPlex](https://arxiv.org/abs/2602.06053) のHybrid System Promptのうち，テキストによる話題条件づけの部分のみを参考にしています．プロンプトの書き方や制約の詳細はモデルカードを参照してください．

v1.1-topic-promptedでは，1学習例の長さは約164秒を上限としています．このため実際に学習に使用したのは，合成コーパスが約3,600時間，LLM-jp-Zoom1は1対話が長い（平均約32分）ため各対話の冒頭のみで計約78時間です．

v1.1-base と v1.1-topic-prompted が使用する合成対話コーパスの音声は，LLM-jp-Zoom1でファインチューニングした音声合成モデルで生成しています．

各リポジトリには，以下のモデルファイルが含まれています:
- `model.safetensors` - モデル本体の重み
- `tokenizer_spm_32k_3.model` - テキストトークナイザ（[rinna/japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium)の日本語SentencePieceモデル）
- `tokenizer-e351c8d8-checkpoint125.safetensors` - 音声トークナイザ（[kyutai/moshiko-pytorch-bf16](https://huggingface.co/kyutai/moshiko-pytorch-bf16)のMimiモデル）

v1.1-topic-promptedのリポジトリには，加えてプロンプト条件づけ用の `prefix_tokens.npz` が含まれます．


## Interactive Demo

LLM-jp-Moshiの各モデルと対話する方法を説明します．v1 および v1.1-base はKyutai公式の[MoshiのPyTorch実装](https://github.com/kyutai-labs/moshi/tree/main/moshi)をそのまま使用できます（実装の詳細はオリジナルMoshiのリポジトリ [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) を参照）．v1.1-topic-prompted は専用の推論サーバが必要なため，手順が異なります（後述）．

### v1 / v1.1-baseのインストール

Python 3.10以上が必要です．

```bash
pip install 'moshi<=0.2.2'
```

### v1 / v1.1-baseの起動

`moshi.server`を実行することで，対話用のweb UIを起動できます．`--hf-repo`オプションで使用するモデルの 🤗HuggingFace Hubリポジトリを指定してください．

```bash
python -m moshi.server --hf-repo llm-jp/llm-jp-moshi-v1
# または
python -m moshi.server --hf-repo llm-jp/llm-jp-moshi-v1.1-base
```

#### v1.1-topic-promptedと対話する場合

> [!NOTE]
> v1.1-topic-promptedは，テキストプロンプトによる条件づけに対応した専用の推論実装が必要なため，`moshi.server`では動作しません．本リポジトリの [`inference/`](inference/) に対応サーバを同梱しています．

```bash
python inference/server.py --hf-repo llm-jp/llm-jp-moshi-v1.1-topic-prompted
```

画面上部で話題プロンプト（学習済み15話題のプリセット）を選択し，「接続」を押して対話を開始します．

### Tips

- 実行には，24GB以上のVRAMを搭載したLinux GPUマシンが必要です．MacOSには対応していません．
- モデルの発話音声がエコーすることを避けるため，対話時にはスピーカではなくイヤホン・ヘッドホンを使用してください．音声デバイスはweb UIアクセス時にブラウザ上で設定できます．


## Terms of Use

LLM-jp-Moshiの各モデルは [Apache License, Version 2.0](LICENSE) の下で公開されています．
本モデルは，なりすましや詐欺などの悪意ある目的での使用を意図したものではありません．また，本モデルの出力には，学習データに起因するバイアス，不正確な情報，または不適切もしくは攻撃的な内容が含まれる可能性があります．
我々はその使用によって生じるいかなる損害についても責任を負いません．


## Acknowledgments

本研究では，国立研究開発法人産業技術総合研究所および株式会社AIST Solutionsが提供するAI橋渡しクラウド（ABCI）3.0を，「ABCI 3.0開発加速利用」の支援を受けて実施しました．
また，ベースモデルであるMoshiおよびテクニカルペーパーを公開されたKyutai Labs，ならびにJ-CHATデータセットを公開された研究者の皆様に深く感謝の意を表します．


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
