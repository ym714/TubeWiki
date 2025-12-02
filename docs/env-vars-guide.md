---
marp: true
theme: default
paginate: true
header: FlashNote AI - 環境変数の取得場所ガイド
footer: 2025-12-03 | Setup Guide
---

# 環境変数の取得場所ガイド

各サービスのAPIキーやURLの取得方法をまとめました。

---

## 1. Supabase (Database & Auth)

**取得先**: [Supabase Dashboard](https://supabase.com/dashboard)

### `DATABASE_URL`
1.  Project Settings (左下の歯車アイコン) -> **Database** をクリック。
2.  **Connection String** セクションを探す。
3.  "URI" タブを選択し、"Mode: Transaction Pooler" (Port 6543) を選択。
4.  コピーして、`[YOUR-PASSWORD]` を実際のパスワードに置き換える。

### `SUPABASE_JWT_SECRET`
1.  Project Settings -> **API** をクリック。
2.  **JWT Settings** セクションを探す。
3.  `JWT Secret` をコピーする。

---

## 2. Upstash (QStash)

**取得先**: [Upstash Console](https://console.upstash.com/)

### `QSTASH_URL` & `QSTASH_TOKEN`
1.  QStash タブを選択。
2.  **REST API** セクションを見る。
3.  `QSTASH_URL` (例: `https://qstash.upstash.io/v1/publish`) と `QSTASH_TOKEN` をコピー。

### `QSTASH_CURRENT_SIGNING_KEY` & `NEXT_SIGNING_KEY`
1.  **Signing Keys** タブを選択。
2.  `Current Signing Key` と `Next Signing Key` をコピー。

---

## 3. Groq (AI Model)

**取得先**: [Groq Console](https://console.groq.com/keys)

### `GROQ_API_KEY`
1.  **API Keys** メニューを選択。
2.  "Create API Key" をクリック。
3.  名前を付けて作成し、表示されたキー（`gsk_...`）をコピー。

---

## 4. Notion (Export)

**取得先**: [Notion Developers](https://www.notion.so/my-integrations)

### `NOTION_TOKEN`
1.  "New integration" をクリック。
2.  名前（例: "FlashNote AI"）を入力して送信。
3.  **Internal Integration Secret** (これがToken) をコピー。
    *   **重要**: Notionのページ側で、このインテグレーションを「接続 (Connect)」する必要があります（右上の ... メニュー -> Connections）。

---

## 5. まとめ: 設定ファイル別の必要項目

### `core/.env`
- `DATABASE_URL` (Supabase)
- `SUPABASE_JWT_SECRET` (Supabase)
- `QSTASH_URL` (Upstash)
- `QSTASH_TOKEN` (Upstash)

### `worker/.env`
- `DATABASE_URL` (Supabase - **coreと同じもの**)
- `QSTASH_CURRENT_SIGNING_KEY` (Upstash)
- `GROQ_API_KEY` (Groq)
- `NOTION_TOKEN` (Notion)
