---
marp: true
theme: default
paginate: true
header: "TubeWiki 残りの実装プロセス"
footer: "2025-12-02"
---

# TubeWiki 残りの実装プロセス

## 現状の進捗

これまでに以下の実装が完了しています：

- [x] **プロジェクト初期化**: Vite + React + TS, Tailwind CSS, Manifest V3
- [x] **アーキテクチャ再構築**: Popup と Content Script の分離, Shadow DOM の導入
- [x] **Popup UI**: ログイン, ステータス表示, ノート作成トリガー
- [x] **Content Script**: YouTube 上へのオーバーレイ表示, ノート内容の表示
- [x] **Backend API**: URL によるノート取得エンドポイント (`GET /notes/by-url`)

---

## 残っているプロセス

### 1. Background Script の実装
**目的**: 拡張機能全体の状態管理と認証情報の同期。

- **認証状態の同期**:
  - Popup (Supabase Auth) でログインしたセッション情報を `chrome.storage` に保存。
  - Content Script が API リクエストを行う際に、保存されたトークンを使用できるようにする。
  - 現在の実装では Popup と Content Script でセッションが共有されていないため、これを解決する必要があります。
- **メッセージング**:
  - Popup, Content Script, Background 間でのイベント通信（例: ログイン完了通知など）。

### 2. Core API との完全な統合
**目的**: フロントエンドとバックエンドの連携強化。

- **認証ミドルウェアの検証**: 拡張機能からのリクエストが正しく認証されるか確認。
- **エラーハンドリング**: トークン期限切れ時の再ログインフローなど。

---

## 具体的な次のアクション

1.  **`src/background/index.ts` の実装**:
    -   `supabase.auth.onAuthStateChange` を監視し、セッション変更時に `chrome.storage.local` にトークンを保存するリスナーを実装（Popup 側で実装が必要な場合もあり）。
    -   または、Popup 側でログイン時に `chrome.storage` に保存し、Content Script はそこから読み込む形に修正。

2.  **API クライアント (`src/lib/api.ts`) の改修**:
    -   `supabase.auth.getSession()` だけでなく、`chrome.storage` からのトークン取得もサポートするように変更。

3.  **動作検証**:
    -   拡張機能をリロードし、Popup でログイン -> YouTube ページをリロード -> オーバーレイが「Generate Wiki」ボタンを表示できるか確認。
