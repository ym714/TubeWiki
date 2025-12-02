---
marp: true
theme: default
paginate: true
header: "FlashNote AI 実装報告書"
footer: "2025-12-02"
---

# FlashNote AI 実装報告書

## 実装完了項目の概要
### Week 1-3

---

## プロジェクト概要

**FlashNote AI** は、YouTube動画からNotion学習ガイドを自動生成するツールです。
現在、**Backend (Core & Worker)** および **Frontend (Chrome Extension)** の実装が完了しています。

### 主な成果
- **モノレポ構成**: 関心の分離を徹底したクリーンな構成。
- **サーバーレスアーキテクチャ**: スケーラブルかつコスト効率の高い設計。
- **AI統合**: GPT-4oによる高品質な要約と図解生成。
- **プラットフォーム連携**: YouTube, Notion, Chrome拡張機能の統合。

---

## アーキテクチャ概要

本システムは **サーバーレス・イベント駆動アーキテクチャ** を採用しています。

1.  **Core Service (FastAPI)**: ユーザーリクエストと認証を処理。
2.  **Event Bus (Upstash QStash)**: CoreとWorkerを疎結合に接続。
3.  **Worker Service (FastAPI)**: 重いAI処理を非同期で実行。
4.  **Database (Supabase)**: ユーザーとノートデータを保存。
5.  **Frontend (Chrome Ext)**: 動画キャプチャ用UI。

---

## 1. 共通ライブラリ (`shared/`)

CoreとWorkerで共通して使用されるライブラリで、一貫性を担保します。

- **Pydantic Schemas**: `JobRequest` など、サービス間の契約を定義。
- **SQLModel Models**: `Note`, `User` などのデータベーススキーマ定義。
- **Database**: `asyncpg` と SQLAlchemy を使用した非同期DB接続ロジック。

---

## 2. Core Service (`core/`)

アプリケーションのエントリーポイントです。

- **API Endpoints**:
    - `POST /notes`: 動画URLを受け取り、`PENDING` ノートを作成し、QStashへジョブを発行。
    - `GET /notes/{id}`: ノートのステータスと内容を返却（ポーリング用）。
- **Authentication**:
    - **Supabase Auth**: `SUPABASE_JWT_SECRET` を使用してJWTトークンを検証。
    - **Security**: 全エンドポイントを保護。
- **QStash Publisher**: Workerへジョブを非同期プッシュ。

---

## 3. Worker Service (`worker/`)

スケール・トゥ・ゼロ（Scale-to-Zero）可能なワーカーサービスです。

- **Webhook Handler**: `POST /webhooks/process-job` でQStashからのイベントを受信。
- **Security**: `Upstash-Signature` を検証し、不正アクセスを防止。
- **Idempotency**: ノートが既に `COMPLETED` の場合は処理をスキップ。
- **Pipeline**:
    1.  **YouTube**: `youtube-transcript-api` で字幕を取得。
    2.  **AI (GPT-4o)**: Markdown要約とMermaid図解を生成。
    3.  **Notion**: 生成されたコンテンツでNotionページを作成。
    4.  **DB Update**: ノートのステータスとコンテンツを更新。

---

## 4. Frontend - Chrome Extension (`extension/`)

Reactベースのサイドパネル拡張機能です。

- **Tech Stack**: Vite, React, TypeScript, Tailwind CSS, CRXJS.
- **Features**:
    - **Auth**: Supabase Auth (Email/Password) によるログイン。
    - **Capture**: 現在のYouTubeタブからワンクリックで生成開始。
    - **Real-time Feedback**: Core APIをポーリングし、`PROCESSING` -> `COMPLETED` の状態を表示。
    - **Result View**: 生成された要約をサイドパネル内で直接表示。

---

## 5. インフラ & デプロイ

- **Database**: Supabase (PostgreSQL) + Transaction Pooler (Port 6543).
- **Compute**:
    - Core: Vercel Serverless Functions 対応。
    - Worker: Docker化済み、Cloud Run 対応。
- **Event Bus**: Upstash QStash (Push型配送)。

---

## 今後のステップ (Week 4)

- **QA & Robustness (品質保証)**:
    - QStashのリトライメカニズムとDead Letter Queueの検証。
    - 包括的な統合テスト。
- **Polish (ブラッシュアップ)**:
    - 拡張機能のUI/UX改善。
    - ランディングページ (LP) 作成。
- **Deployment**:
    - 本番環境へのデプロイ。
