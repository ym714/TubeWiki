---
marp: true
theme: default
paginate: true
header: "TubeWiki Notion認証調査レポート"
footer: "2025-12-09"
---

# Notion認証に関する調査レポート

## 認証未設定がエラーの原因か？

---

## 🔍 エグゼクティブサマリー

**結論:**
「Timeout（タイムアウト）」エラーの原因は、Notion API認証の欠如では**ありません**。

**理由:**
1.  **サーバーサイド連携の無効化**: バックエンドコードでは現在、Notion API呼び出しがスキップされています (`worker/api/webhook.py`)。
2.  **クライアントサイド「自動ペースト」**: 拡張機能は、コンテンツをクリップボードにコピーし、`notion.so/new` を開く仕組みを使用しています。
3.  **ブラウザログインが必要**: この方法では、拡張機能設定でのAPIトークンは不要ですが、**ブラウザでNotionにログインしていること**が必要です。

---

## 🛠 現在のアーキテクチャ

### 「Notionへエクスポート」の現在の動作:

1.  **リクエスト**: 拡張機能がサーバーにAI要約をリクエスト。
2.  **生成**: サーバーがYouTube字幕を取得し、Markdownを生成（タイムアウトは通常ここで発生）。
3.  **レスポンス**: サーバーがMarkdownを拡張機能に返却。
4.  **自動ペースト**:
    - 拡張機能がMarkdownをChromeストレージに保存。
    - 拡張機能が `https://notion.so/new` を開く。
    - 拡張機能のスクリプト (`content/notion.ts`) がストレージを読み込み、新規ページにペースト。

---

## 💻 コードによる証拠

### サーバーサイド (`worker/api/webhook.py`)
Notionページ作成処理が明示的にスキップされています：

```python
# 89: Simplified Flow: We no longer create Notion pages server-side.
# 90: The client handles "Copy & Open".
notion_url = None
```

### 拡張機能サイド (`content/ExportBar.tsx`)
拡張機能はクライアントサイドフローの準備をしています：

```typescript
// 140: window.open('https://notion.so/new', '_blank')
```

---

## ⚠️ タイムアウトの真の原因

「Timeout waiting for note generation」が表示される場合、主な原因は以下の通りです：

1.  **YouTube Transcript API**: 字幕の取得に失敗している（例：動画に字幕がない、IPブロックなど）。
2.  **AI生成の遅延**: LLM (Groq/OpenAI) の処理時間が、拡張機能のタイムアウト制限（30秒）を超えている。
3.  **Workerのコールドスタート**: バックエンドが無料枠（Railway/Renderなど）にある場合、起動に時間がかかっている。

---

## ✅ 推奨アクション

### ユーザー向け
1.  **Notionログイン確認**: ブラウザで [Notion.so](https://www.notion.so) にログインしているか確認してください。
2.  **再試行**: タイムアウトの問題か確認するため、短い動画で試してみてください。
3.  **設定は無視**: 拡張機能設定の「Notion Token」は、現在バックエンドでは**使用されていません**。

### 開発者向け
1.  **タイムアウト延長**: `ExportBar.tsx` の30秒のポーリング制限を延長する。
2.  **YouTube API修正**: `youtube-transcript-api` が動作しているか確認する（最近修正済み）。
3.  **API連携の復元**: バックグラウンドでの完全なエクスポートが必要な場合、サーバーサイドのNotionコードを再度有効化する。
