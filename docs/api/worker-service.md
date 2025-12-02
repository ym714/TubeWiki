---
marp: true
theme: default
paginate: true
header: "TubeWiki Worker Service"
footer: "2025-12-02"
---

# TubeWiki Worker Service

## バックグラウンド処理と外部連携の中核

---

## 概要

**Worker Service** は、TubeWikiのバックエンドにおいて、時間のかかる処理や外部APIとの連携を担当する非同期ワーカーです。

- **主な役割**:
  - YouTube動画の文字起こし取得
  - AIによる要約と学習ガイド生成 (OpenAI / Gemini)
  - Mermaid.jsによるマインドマップ生成
  - Notionへのページ作成
- **アーキテクチャ**: FastAPIベースのWebサーバーですが、主に **QStash** からのWebhookを受け取って駆動します。

---

## アーキテクチャとフロー

Workerは **QStash** からのHTTPリクエスト（Webhook）をトリガーとして動作します。

1. **Trigger**: Core ServiceがQStashにジョブをパブリッシュ
2. **Webhook**: QStashがWorkerの `/webhooks/process-job` を叩く
3. **Process**:
   - **YouTube**: 字幕取得
   - **AI**: コンテンツ生成
   - **Notion**: ページ作成
   - **DB**: 結果保存 (`Note` テーブル更新)

---

## ディレクトリ構造 (`worker/`)

```
worker/
├── main.py           # エントリーポイント (FastAPIアプリ定義)
├── config.py         # 環境変数設定 (Pydantic)
├── api/
│   └── webhook.py    # メインロジック (ジョブ処理フロー)
└── services/         # 外部連携サービス群
    ├── ai.py         # AI生成 (OpenAI / Gemini)
    ├── notion.py     # Notion API クライアント
    ├── youtube.py    # YouTube字幕取得
    └── security.py   # QStash署名検証
```

---

## 主要コンポーネント: Webhook (`api/webhook.py`)

ジョブ処理のオーケストレーターです。以下のステップを実行します。

1. **署名検証**: `Upstash-Signature` ヘッダーを検証し、正当なリクエストであることを確認。
2. **冪等性チェック**: `Note` IDを確認し、既に完了している場合はスキップ。
3. **実行**: 各サービス (`youtube`, `ai`, `notion`) を順次呼び出し。
4. **状態更新**: 処理中 (`PROCESSING`) -> 完了 (`COMPLETED`) または 失敗 (`FAILED`) にDBを更新。

---

## 外部サービス連携

### 1. YouTube Service (`services/youtube.py`)
- `youtube_transcript_api` を使用。
- 動画URLからIDを抽出し、日本語 (`ja`) または英語 (`en`) の字幕を取得。

### 2. AI Service (`services/ai.py`)
- **生成モデル**: `gpt-4o` (OpenAI) または `gemini-1.5-flash` (Google)。
- **機能**:
  - **Note Generation**: 字幕からMarkdown形式の学習ガイドを生成。
  - **Diagram Generation**: 内容に基づいたMermaidマインドマップを生成。

### 3. Notion Service (`services/notion.py`)
- `notion-client` を使用。
- 指定された親ページ配下に、生成されたコンテンツを含む新しいページを作成。

---

## 設定と環境変数 (`config.py`)

動作には以下の環境変数が必要です。

| 変数名 | 説明 |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL接続URL |
| `QSTASH_CURRENT_SIGNING_KEY` | Webhook署名検証用キー |
| `QSTASH_NEXT_SIGNING_KEY` | (Optional) ローテーション用キー |
| `OPENAI_API_KEY` | OpenAI APIキー (Gemini未使用時) |
| `GEMINI_API_KEY` | Gemini APIキー (優先使用) |
| `NOTION_TOKEN` | Notion Integration Token |

---

## 起動方法

開発環境では `uvicorn` を使用して起動します。

```bash
# プロジェクトルートで実行
uvicorn worker.main:app --reload --port 8001
```

- ポート `8001` で起動 (Coreは `8000`)。
- ローカル開発時は `ngrok` 等を使用して外部からアクセス可能にするか、QStashのローカルエミュレーションが必要です。
