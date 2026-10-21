# LLM-jp-Moshi-v1.1-prompted 推論サーバ

LLM-jp-Moshi-v1.1-prompted と対話するためのWebサーバです．テキストプロンプトの前置（prefill）に
対応しているため，`moshi.server` の代わりにこちらを使用してください（v1 / v1.1-base には
公式の [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) をそのまま使えます）．

プロンプトの条件づけ機構は [PersonaPlex](https://arxiv.org/abs/2602.06053) の Hybrid System Prompt
（テキストによる話題条件づけの部分）を論文に基づいて再現実装したものであり，
[NVIDIA/personaplex](https://github.com/NVIDIA/personaplex) のコードは使用していません．

## Installation

Python 3.12 での動作を確認しています．

```bash
pip install -r requirements.txt
```

## Usage

`server.py` を実行することで，対話用のweb UIを起動できます．`--hf-repo`オプションでモデルの
🤗HuggingFace Hubリポジトリ（[llm-jp/llm-jp-moshi-v1.1-prompted](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-prompted)）を
指定してください（モデルファイル一式が自動でダウンロードされます．`--moshi-weight` 等で
ローカルのファイルも指定できます）．

```bash
python server.py --hf-repo llm-jp/llm-jp-moshi-v1.1-prompted
```

ブラウザで `http://localhost:8998/` を開き，画面上部の入力欄で話題プロンプトを編集して
（学習済み15話題のプリセットあり），「接続」を押して対話を開始します．
モデルとユーザー双方の音声波形が時間軸で表示され，モデルの発話テキストが波形の下に重ねて描かれます．

### プロンプトの指定方法

- 画面上で設定するほか，`/ws` への接続時に `?text_prompt=...` クエリで直接渡せます
  （空文字なら prefill 無し）．
- サーバ側でプロンプト集合から接続ごとに選ぶこともできます:

```bash
python server.py --hf-repo llm-jp/llm-jp-moshi-v1.1-prompted --prompt-file prompts.txt --prompt-mode random
```

`prompts.txt` は1行1プロンプト．`--prompt-mode` は `fixed`（既定）/ `random` / `roundrobin`．
`?prompt_seed=<id>` を付けると集合から決定的に1本選びます（A/B比較で両者のプロンプトを揃える用）．

プロンプトの書き方や制約は[モデルカード](https://huggingface.co/llm-jp/llm-jp-moshi-v1.1-prompted)を参照してください．

## Tips

- 実行には，24GB以上のVRAMを搭載したLinux GPUマシンが必要です．MacOSには対応していません．
- モデルの発話音声がエコーすることを避けるため，対話時にはスピーカではなくイヤホン・ヘッドホンを使用してください．
