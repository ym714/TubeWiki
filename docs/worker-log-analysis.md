---
marp: true
theme: default
paginate: true
header: TubeWiki Worker Log Analysis
footer: 2025-12-09
---

# TubeWiki Worker Log Analysis

## 概要
TubeWiki Workerのログ出力に関する分析と、トラブルシューティングのためのガイドライン。

---

## ログの分析結果

### 観測されたログ
```
WARNING:worker.api.webhook:No signature provided - assuming local development mode
INFO:worker.api.webhook:Processing job for note 26, video ...
INFO:worker.services.youtube:Fetching transcript for video: ...
INFO:worker.services.youtube:Successfully fetched transcript
WARNING:worker.api.webhook:DEBUG: Transcript fetched. Length: 3234
WARNING:worker.api.webhook:DEBUG: Content generated. Length: 1062
INFO:worker.api.webhook:Job completed for note 26
```

### 状態: 正常終了 (Success)
- `Job completed for note 26` の出力により、ジョブが正常に完了したことが確認できます。
- エラーログのように見える `WARNING` 行が含まれていますが、これは開発用デバッグ情報の出力レベル設定によるものです。

---

## 警告メッセージの解説

### 1. `No signature provided`
```
WARNING:worker.api.webhook:No signature provided - assuming local development mode
```
- **原因**: ローカル開発環境や手動テスト（curl等）からのリクエストには、QStashの署名（Upstash-Signature）が含まれていないため。
- **対応**: ローカル開発では無視して問題ありません。本番環境（Production）では署名検証が必須となります。

### 2. `DEBUG: Transcript fetched...`
```
WARNING:worker.api.webhook:DEBUG: Transcript fetched. Length: 3234
```
- **原因**: デバッグ情報を可視化するために `logger.warning` を使用していたため。
- **対応**: コード修正により `logger.debug` に変更済み。これにより、通常のログレベルでは出力されなくなり、ノイズが減少します。

---

## トラブルシューティング

### 正常なフロー
1. `Processing job for note X` (開始)
2. `Fetching transcript` (YouTube取得)
3. `Successfully fetched transcript` (取得成功)
4. `Job completed for note X` (完了)

### よくあるエラー
- **Timeout**: YouTube取得やAI生成に時間がかかりすぎている場合。
- **Signature verification failed**: 本番環境で署名が一致しない場合。
- **Missing note_id**: リクエストボディに必須パラメータが欠けている場合。
