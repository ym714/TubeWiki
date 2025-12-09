---
marp: true
theme: default
paginate: true
header: "TubeWiki Troubleshooting Report"
footer: "2025-12-09"
---

# 🐛 トラブルシューティング報告: ノート生成タイムアウト

## 🚨 発生していた問題

### エラー内容
Chrome拡張機能で「Export to Notion」を実行すると、以下のエラーが発生して失敗する。

```
Error: Timeout waiting for note generation
```

### 原因分析

このエラーは、拡張機能がバックエンド（Core API）にリクエストを送信した後、60秒以内に「完了 (COMPLETED)」または「失敗 (FAILED)」のステータスを受け取れなかったことを意味します。

主な原因として以下が特定されました：

1.  **Workerサービスのバグ (修正済み)**:
    - `youtube-transcript-api` のバージョン不整合により、Workerが字幕取得時にエラーを発生させていました。
    - これにより処理が止まり、ステータスが更新されなかった可能性があります。

2.  **ローカル環境設定の不備 (修正済み)**:
    - `core/.env` の `WORKER_URL` が `http://worker.railway.internal:8080`（Railway内部用）になっていました。
    - ローカル環境ではこのURLにアクセスできないため、CoreからWorkerへのジョブ送信が失敗していました。

---

## 🛠 実施した修正

### 1. Workerサービスの修正
`worker/services/youtube.py` を修正し、最新の `youtube-transcript-api` に対応させました（前回の対応）。

### 2. 環境変数の修正
`core/.env` の `WORKER_URL` をローカル開発用に変更しました。

- **Before**: `http://worker.railway.internal:8080`
- **After**: `http://localhost:8001`

---

## ✅ 推奨アクション

### ローカル開発の場合
1. **サーバーの再起動**: `core` と `worker` の両方のプロセスを再起動してください。
2. **動作確認**: 拡張機能から再度「Generate」を実行してください。

### 本番環境 (Railway) の場合
1. **デプロイ**: 修正したコード (`worker/services/youtube.py`) をGitHubにプッシュし、Railwayへのデプロイをトリガーしてください。
2. **環境変数の確認**: Railway上の `tubewiki-core` サービスの `WORKER_URL` が正しく設定されているか確認してください（通常は自動設定または `https://tubewiki-worker.up.railway.app`）。

---

## 📝 補足: コンソールエラーについて

ログに含まれていた以下のエラーは、今回のタイムアウトとは無関係です。

- `Uncaught TypeError: Cannot redefine property: ethereum`: MetaMaskなどのウォレット拡張機能による競合。
- `requestStorageAccessFor: Permission denied`: YouTubeの埋め込みスクリプトによる警告。
