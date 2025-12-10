---
marp: true
theme: default
paginate: true
header: "Error Troubleshooting: Failed to fetch"
footer: "2025-12-09 | TubeWiki Team"
---

# 🐛 エラー解決: Failed to fetch

Chrome拡張機能で発生する「Failed to fetch」エラーの原因と対策について

---

## 🚨 エラーの概要

**エラーメッセージ**:
```
Error: Failed to fetch
```
または
```
[TubeWiki] ensureNote failed: Error: Failed to fetch
```

**発生場所**: Chrome拡張機能 (Extension)
**意味**: 拡張機能がバックエンドサーバー (`localhost:8000`) に接続しようとしましたが、通信に失敗しました。

---

## 🔍 主な原因

最も一般的な原因は **バックエンドサーバーが起動していない** ことです。

TubeWikiの拡張機能は、ローカルで動作しているAPIサーバーと通信して機能します。サーバーが停止していると、このエラーが発生します。

その他の可能性:
- サーバーが別のポートで起動している
- Chromeのセキュリティポリシーによるブロック (CORSなど)

---

## ✅ 解決策

### 1. サーバーの起動確認

ターミナルで以下のコマンドを実行し、サーバーが起動しているか確認してください。

```bash
# Core API (Backend)
PYTHONPATH=. uvicorn core.main:app --reload --port 8000
```

### 2. サーバーの再起動

もしサーバーが起動しているように見えても応答がない場合は、一度 `Ctrl+C` で停止し、再度起動してください。

### 3. 接続テスト

別のターミナルで以下のコマンドを実行し、サーバーが応答するか確認できます。

```bash
curl http://localhost:8000/health
# {"status":"ok"} が返ってくれば正常です
```

---

## 📝 補足: 開発時の注意点

- `git` コマンドなどを実行するためにサーバーを停止した場合は、作業後に必ず再起動してください。
- 拡張機能のエラーログは、拡張機能管理画面 (`chrome://extensions`) の「ビューを検査: Service Worker」または「エラー」ボタンから確認できます。
