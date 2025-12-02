---
marp: true
theme: default
paginate: true
header: "TubeWiki プロジェクト全体の残り実装タスク"
footer: "2025-12-02"
---

# TubeWiki プロジェクト全体の残り実装タスク

## 1. Extension (Chrome拡張機能)
**ステータス: 完了 (v1.0)**
- [x] Popup UI, Content Script (Overlay), Background Script 実装完了
- [x] Core API との連携完了
- [x] アイコン設定、Markdownレンダリング対応完了

## 2. Core Service (Backend API)
**ステータス: ほぼ完了**
- [x] 認証 (Supabase Auth)
- [x] ノート作成・取得 API (`POST /notes`, `GET /notes/{id}`, `GET /notes/by-url`)
- [x] QStash へのジョブ発行
- [ ] **CORS設定**: 本番環境 (Vercel) での CORS 設定確認。

## 3. Worker Service (AI Processing)
**ステータス: 実装済みだが改善の余地あり**
- [x] Webhook 受信 (`POST /webhooks/process-job`)
- [x] QStash 署名検証
- [x] YouTube 字幕取得 (`youtube-transcript-api`)
- [x] AI コンテンツ生成 (GPT-4o)
- [x] Mermaid ダイアグラム生成
- [ ] **Notion 連携の強化**:
    - 現在は Markdown をそのままテキストブロックとして Notion に送信しているため、見栄えが悪い。
    - **Markdown to Notion Blocks** の変換ロジックが必要。
- [ ] **環境変数設定**: `NOTION_TOKEN` が `config.py` に定義されていない。

## 4. Shared Library
**ステータス: 完了**
- [x] DB Models (`Note`, `User`)
- [x] Schemas (`JobRequest`)

---

## 推奨される次のステップ

### A. Notion 連携の改善 (Worker)
`worker/services/notion.py` を修正し、Markdown を Notion のブロック形式（見出し、リスト、コードブロックなど）に変換して送信するようにする。これにより、Notion 上での可読性が大幅に向上します。

### B. 環境変数の整理
`worker/config.py` に `NOTION_TOKEN` を追加し、デプロイメント環境（Railway/Cloud Run/Vercel）に設定する。

### C. 統合テスト (E2E)
1. 拡張機能から「Generate Wiki」をクリック。
2. Core API がリクエストを受け、QStash に Publish。
3. Worker が Webhook を受信し、YouTube -> AI -> Notion のフローを実行。
4. 拡張機能のポーリングで「COMPLETED」になり、Markdown が表示されることを確認。
