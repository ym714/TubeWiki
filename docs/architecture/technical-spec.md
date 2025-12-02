---
marp: true
theme: default
paginate: true
header: FlashNote AI Technical Specification
footer: 2025-12-02
---

# FlashNote AI 技術仕様書
## Technical Specification

---

## 概要

本ドキュメントは、FlashNote AIの技術仕様をまとめたものです。
**サーバーレス・イベント駆動アーキテクチャ**を採用し、コスト最適化とスケーラビリティを実現します。

---

## 直近のレビュー反映 (Red Team Review - Round 4)

**堅牢性と信頼性 (Robustness & Reliability)** に焦点を当てた最終レビューを実施しました。

- **冪等性 (Idempotency)**:
  - QStashは「At Least Once（少なくとも1回）」の配信を保証するため、Workerは**冪等**である必要があります。
  - ノートが既に `COMPLETED` の場合、処理をスキップするチェックを追加しました。

- **リトライポリシー**:
  - QStashのリトライ設定を明示的に定義しました（最大3回、指数バックオフ）。
  - 一時的な障害に対応しつつ、Workerへの過負荷を防ぎます。

- **ローカル開発**:
  - Webhookのテストに `ngrok` またはローカルQStashエミュレータを使用することを明確化しました。

---

## アーキテクチャ概要 (What we did)

**サーバーレス・イベント駆動アーキテクチャ**を採用しました。
システムは **Upstash QStash** によって疎結合された2つのサービスで構成されます。

1.  **Core Service (User API)**
2.  **Worker Service (AI Processing)**

この構成により、長時間の動画処理タスク（最大1時間）を非同期で処理し、ユーザー体験を損なうことなく、アイドル時の**インフラコストをゼロ**に抑えます。

---

## 開発ガイドライン: コア原則

1.  **関心の厳密な分離 (Strict Separation of Concerns)**
    *   **Core ("The Manager")**: ユーザー認証、DB状態管理、ジョブ投入を担当。重い計算は行わない。
    *   **Worker ("The Specialist")**: AIタスクを実行するプライベートAPI。ステートレスであり、イベントバスからのWebhookのみでトリガーされる。

2.  **サーバーレス & マネージド (Serverless & Managed)**
    *   **Database**: **Supabase** (PostgreSQL + Auth)。Transaction Pooler (Port 6543) の使用が必須。
    *   **Event Bus**: **Upstash QStash** (HTTP Queue)。
    *   **Compute**: **Cloud Run** (Worker) および **Vercel** (Core)。

3.  **SOLIDとシンプルさのバランス (YAGNI)**
    *   **Monorepo**: 単一リポジトリを使用。`shared` ディレクトリはビルド時にWorkerイメージにコピーされる。
    *   **No Frameworks for AI**: LangChainは使用せず、生の `openai` ライブラリを使用。

---

## 技術スタック & インフラ (1/3)

### 1. コンピュート & ランタイム層

*   **Core Service**: **Python (FastAPI)**
    *   **責務**: ユーザーAPIゲートウェイ、認証、ジョブ作成。
    *   **ホスティング**: Vercel (Serverless Functions)。

*   **Worker Service**: **Python (FastAPI)**
    *   **責務**: AIパイプライン実行 (YouTube -> Transcript -> GPT-4o -> Notion)。
    *   **ホスティング**: Cloud Run (リクエスト処理中のみCPU割り当て)。
    *   **セキュリティ**: `Upstash-Signature` ヘッダーの検証。

---

## 技術スタック & インフラ (2/3)

### 2. イベントバス (神経系)

*   **サービス**: **Upstash QStash**
*   **役割**: 信頼性の高い非同期ジョブ配信。
*   **設定**:
    *   **リトライ**: 3回 (指数バックオフ)。
    *   **タイムアウト**: 1時間 (Cloud Runの制限に合わせる)。
*   **プロトコル**:
    *   **Core**: JSONペイロードをQStashにPublish。
    *   **Worker**: QStashからHTTP POSTを受信。

---

## 技術スタック & インフラ (3/3)

### 3. データ永続化 (記憶)

*   **データベース**: **Supabase (PostgreSQL)**
    *   **役割**: リレーショナルデータ保存。
    *   **設定**: **Transaction Mode (Port 6543)**。
    *   **理由**: サーバーレスWorkerからの高並列接続を `max_connections` エラーなしで処理するため必須。

*   **ORM**: **SQLModel (SQLAlchemy + Pydantic)**
    *   **役割**: 非同期ORM。

---

## アーキテクチャ構造

```
flashnote-ai/
├── core/               # FastAPI (User Facing)
│   ├── api/            # Routes (Auth, Notes)
│   └── main.py         # App Entrypoint
├── worker/             # FastAPI (Internal Job Handler)
│   ├── api/            # Routes (Webhooks)
│   ├── services/       # OpenAI, YouTube, Notion Logic
│   ├── Dockerfile      # Multi-stage build (copies shared)
│   └── main.py         # App Entrypoint
└── shared/             # Shared Library
    ├── models/         # SQLModel Database Models
    ├── schemas/        # Pydantic API/Event Schemas
    └── utils/          # Common utilities
```

---

## 実装アプローチ: YAGNI

1.  **スキーマファースト**:
    `shared` で `JobRequest` スキーマを定義することから始めます。

2.  **環境変数戦略**:
    ローカルでは単一の `.env` を使用。CI/CDでシークレットを注入します。

3.  **時期尚早な最適化の回避**:
    現時点ではキャッシュ層は導入しません。

---

## 各層の責務とイベントバス統合 (1/2)

### 1. Core Service (The Manager)
*   **責務**:
    1.  `POST /notes` リクエストの検証。
    2.  DBに `Note` レコードを作成 (Status: `PENDING`)。
    3.  QStashへジョブを **Publish** (`POST https://qstash.upstash.io/v1/publish/...`)。
    4.  ユーザーへ `202 Accepted` を返却。
*   **イベントバス利用**: Publisher

### 2. Worker Service (The Specialist)
*   **責務**:
    1.  `POST /webhooks/process-job` を受信。
    2.  **署名検証**: `Upstash-Signature` をチェック。
    3.  **冪等性チェック**: Noteが既に `COMPLETED` なら即座に200を返す。
    4.  文字起こし取得 & コンテンツ生成 (GPT-4o)。
    5.  Mermaid図の生成。
    6.  Notionページの作成。
    7.  DBの `Note` を更新 (Status: `COMPLETED`)。
*   **イベントバス利用**: Receiver (Webhook)

---

## 各層の責務とイベントバス統合 (2/2)

### 3. Event Bus (Upstash QStash)
*   **メカニズム**: HTTP Push
*   **接続性**: REST API

---

## テスト駆動開発 (TDD)

### テスト戦略
*   **ユニットテスト**:
    *   **Core**: `QStashClient` をモック化。
    *   **Worker**: モック化されたOpenAIレスポンスを使用してAIサービスをテスト。
*   **統合テスト**:
    *   `ngrok` を使用してローカルWorkerをQStashに公開（またはローカルエミュレータを使用）し、E2Eテストを実施。

### TDDサイクル
1.  🔴 **Red**: QStashを呼び出すことを検証する `POST /notes` のテストを書く。
2.  🟡 **Yellow**: エンドポイントとQStash統合を実装する。
3.  🟢 **Green**: リファクタリングとエラーハンドリングを追加する。

---

## コード品質ガイドライン

1.  **依存性の逆転 (Dependency Inversion)**:
    サービスは注入（Inject）されなければなりません。

2.  **ステートレスなエージェント**:
    Workerはステートレスである必要があります。

3.  **設定 (Configuration)**:
    `QSTASH_CURRENT_SIGNING_KEY` や `DATABASE_URL` が欠落している場合は、即座に失敗（Fail fast）させます。

---

## コードベースガイドの保守

`CODEBASE_GUIDE.md` を保守します。

### 構造例
*   **Event Schema Registry**: `JobRequest` の定義
*   **Infrastructure Configuration**: QStashトピック、DB接続設定
*   **Current Status**: Core/Workerのセットアップ状況

---

## 実装ルール

### ドメインエンティティとORM

**ルール**: ドメインエンティティがデータベースドキュメントに対応する場合、**インターフェースを手動で再定義しないでください**。ORM (SQLModel) によって生成された型を直接インポートして使用します。

```python
# ✅ 正しい例
from shared.models import Note

# APIルート内
@app.post("/notes")
async def create_note(note: Note, session: AsyncSession):
    session.add(note)
    await session.commit()
    return note
```
