---
marp: true
theme: default
paginate: true
header: "TubeWiki Core API リファレンス"
footer: "© 2025 TubeWiki"
---

# TubeWiki Core API リファレンス

**バージョン:** 1.0.0
**ベースURL:** `http://localhost:8080`

---

## 概要

TubeWiki Core APIは、TubeWikiアプリケーションのバックエンドサービスを提供します。主な機能は以下の通りです：

- ノートの生成と管理
- 決済処理 (Stripe連携)
- ヘルスモニタリング

---

## 認証

現在、APIはノート生成のための匿名利用をサポートしています。
決済関連のエンドポイントでは、クライアントから渡される `user_id` によってユーザー識別が行われます（将来的にはFirebase Authトークンなどを想定していますが、現在は簡略化されています）。

---

## エンドポイント: ヘルスチェック

### `GET /healthz`

サービスの稼働状況を監視するためのヘルスチェックエンドポイントです。

**レスポンス:**
```json
{
  "status": "ok",
  "service": "core-api",
  "version": "1.0.0"
}
```

---

## エンドポイント: ノート (Notes)

### `POST /api/v1/notes`

YouTube動画の新しいノート（ジョブ）を作成します。

**リクエストボディ:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=...",
  "user_id": "optional-user-id",
  "options": {
    "language": "ja"
  }
}
```

**レスポンス (202 Accepted):**
```json
{
  "message": "Job accepted",
  "note_id": 123,
  "status": "PENDING"
}
```

---

### `GET /api/v1/notes/{note_id}`

IDを指定して特定のノートを取得します。

**レスポンス:**
```json
{
  "id": 123,
  "video_url": "...",
  "status": "COMPLETED",
  "content": "Markdown content...",
  "created_at": "2025-..."
}
```

---

### `GET /api/v1/notes/by-url/`

YouTube動画のURLを指定してノートを取得します。

**クエリパラメータ:**
- `video_url`: YouTube動画の完全なURL。

**レスポンス:**
見つかった場合はNoteオブジェクトを返し、見つからない場合は404を返します。

---

## エンドポイント: 決済 (Payment)

### `POST /api/v1/payment/checkout`

ProプランへアップグレードするためのStripe Checkoutセッションを作成します。

**リクエスト:**
ヘッダーに認証情報を含める必要があります（現在は依存関係を通じて処理されます）。

**レスポンス:**
```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

---

### `POST /api/v1/payment/webhook`

Stripeイベント用のWebhookエンドポイントです。

**対応イベント:**
- `checkout.session.completed`: ユーザーステータスをProに更新します。

---

## エラーハンドリング

標準的なHTTPステータスコードが使用されます：

- `200 OK`: 成功
- `202 Accepted`: ジョブ受付完了
- `400 Bad Request`: 無効な入力
- `404 Not Found`: リソースが見つかりません
- `500 Internal Server Error`: サーバー内部エラー

---

## 開発

**ローカルサーバー:**
`http://0.0.0.0:8080` で稼働します。

**APIドキュメント (Swagger UI):**
`http://localhost:8080/docs` で利用可能です。
